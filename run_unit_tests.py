
import sys
from unittest import main, TestCase

import rpdb2
import test_rpdb2

class TestGetPythonExecutable( TestCase ):
    def setUp(self):
        self.__sys_executable = sys.executable
        sys.executable = 'fake_executable'

    def tearDown(self):
        sys.executable = self.__sys_executable

    def testGetPythonExecutable(self):
        self.assertEqual( 'titi', rpdb2.get_python_executable( interpreter='titi' ) )
        self.assertEqual( 'fake_executable', rpdb2.get_python_executable( interpreter='' ) )
        self.assertEqual( 'fake_executable', rpdb2.get_python_executable( interpreter=rpdb2.as_unicode('') ) )
        self.assertEqual( 'fake_executable', rpdb2.get_python_executable( interpreter=None ) )
        self.assertEqual( 'fake_executable', rpdb2.get_python_executable() )

    def testGetPythonExecutableWithPythonW(self):
        sys.executable = 'python30w.exe'
        self.assertEqual( 'python30.exe', rpdb2.get_python_executable( ) )

class TestCEventDispatcherRecord( TestCase ):

    def testNoMatchForEmptyCallback( self ):
        er = rpdb2.CEventDispatcherRecord( None, {}, False)
        self.assertEquals( False, er.is_match( rpdb2.CEventNull() ) )

    def testMatchNormal( self ):
        er = rpdb2.CEventDispatcherRecord( None, { rpdb2.CEventExit: {} }, False)
        self.assertEquals( False, er.is_match( rpdb2.CEventNull() ) )
        self.assertEquals( True, er.is_match( rpdb2.CEventExit() ) )

    def testMatchNormalWithArgs( self ):
        er = rpdb2.CEventDispatcherRecord( None, { rpdb2.CEventState: {} }, False)
        self.assertEquals( True, er.is_match( rpdb2.CEventState( rpdb2.STATE_BROKEN ) ) )

    def testMatchExclude( self ):
        er = rpdb2.CEventDispatcherRecord( None, { rpdb2.CEventState: { rpdb2.EVENT_EXCLUDE: [rpdb2.STATE_BROKEN, rpdb2.STATE_ANALYZE] } }, False)
        self.assertEquals( False, er.is_match( rpdb2.CEventState( rpdb2.STATE_BROKEN ) ) )
        self.assertEquals( False, er.is_match( rpdb2.CEventState( rpdb2.STATE_ANALYZE ) ) )
        self.assertEquals( True, er.is_match( rpdb2.CEventState( rpdb2.STATE_RUNNING ) ) )

    def testMatchInclude( self ):
        er = rpdb2.CEventDispatcherRecord( None, {rpdb2.CEventState: { 
            rpdb2.EVENT_INCLUDE: [rpdb2.STATE_BROKEN, rpdb2.STATE_ANALYZE],
            } } , False)
        self.assertEquals( True, er.is_match( rpdb2.CEventState( rpdb2.STATE_BROKEN ) ) )
        self.assertEquals( True, er.is_match( rpdb2.CEventState( rpdb2.STATE_ANALYZE ) ) )
        self.assertEquals( False, er.is_match( rpdb2.CEventState( rpdb2.STATE_RUNNING ) ) )

    def testMatchIncludeExclude( self ):
        er = rpdb2.CEventDispatcherRecord( None, {rpdb2.CEventState: { 
            rpdb2.EVENT_INCLUDE: [rpdb2.STATE_BROKEN, rpdb2.STATE_ANALYZE],
            rpdb2.EVENT_EXCLUDE: [rpdb2.STATE_BROKEN],
            } } , False)
        self.assertEquals( True, er.is_match( rpdb2.CEventState( rpdb2.STATE_ANALYZE ) ) )
        self.assertEquals( False, er.is_match( rpdb2.CEventState( rpdb2.STATE_BROKEN ) ) )


class TestCEventDispatcher( TestCase ):

    def setUp( self ):
        self.m_callbackTrace = []

    def callback( self, event ):
        self.m_callbackTrace.append( event )

    def testEventCallsCallback( self ):
        evd = rpdb2.CEventDispatcher()
        evd.register_callback( self.callback, { rpdb2.CEventNull: {} }, False )
        ev1 = rpdb2.CEventNull() 
        evd.fire_event( ev1 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )

        ev2 = rpdb2.CEventExit()
        evd.fire_event( ev2 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )

    def testCallbackRemoval( self ):
        evd = rpdb2.CEventDispatcher()
        evd.register_callback( self.callback, { rpdb2.CEventNull: {} }, False )
        ev1 = rpdb2.CEventNull() 
        evd.fire_event( ev1 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )

        evd.remove_callback( self.callback )
        ev2 = rpdb2.CEventNull() 
        evd.fire_event( ev2 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )

    def testCallbackDoubleRemoval( self ):
        evd = rpdb2.CEventDispatcher()
        # no exception raised evcen if not registed
        evd.remove_callback( self.callback )

        evd.register_callback( self.callback, { rpdb2.CEventNull: {} }, False )
        evd.remove_callback( self.callback )

        # no exception raised evcen if not registed
        evd.remove_callback( self.callback )

    def testEventCallsCallbackMultipleUse( self ):
        evd = rpdb2.CEventDispatcher()
        evd.register_callback( self.callback, { rpdb2.CEventNull: {} }, False )

        ev1 = rpdb2.CEventNull() 
        evd.fire_event( ev1 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )

        ev2 = rpdb2.CEventNull()
        evd.fire_event( ev2 )
        self.assertEquals( self.m_callbackTrace, [ ev1, ev2 ] )

    def testEventCallsCallbackSingleUse( self ):
        evd = rpdb2.CEventDispatcher()
        evd.register_callback( self.callback, { rpdb2.CEventNull: {} }, True )

        ev1 = rpdb2.CEventNull() 
        evd.fire_event( ev1 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )
        
        ev2 = rpdb2.CEventNull()
        evd.fire_event( ev2 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )

    def testChainedDispatcher( self ):
        evd_first = rpdb2.CEventDispatcher()
        evd_second = rpdb2.CEventDispatcher( evd_first )

        secondCallbackTrace = []
        def secondCallback( ev ):
            secondCallbackTrace.append( ev )

        self.assertEquals( secondCallbackTrace, [] )
        self.assertEquals( self.m_callbackTrace, [] )

        evd_first.register_callback( self.callback, { rpdb2.CEventNull: {} }, False)
        evd_second.register_callback( secondCallback, { rpdb2.CEventNull: {} }, False)

        # Event on first dispatcher
        ev1 = rpdb2.CEventNull() 
        evd_first.fire_event( ev1 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )
        self.assertEquals( secondCallbackTrace, [ ev1 ] )

        # Event on second dispatcher 
        ev2 = rpdb2.CEventNull() 
        evd_second.fire_event( ev2 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )
        self.assertEquals( secondCallbackTrace, [ ev1, ev2 ] )

    def testChainedDispatcherChainOverride( self ):
        evd_first = rpdb2.CEventDispatcher()
        evd_second = rpdb2.CEventDispatcher( evd_first )

        secondCallbackTrace = []
        def secondCallback( ev ):
            secondCallbackTrace.append( ev )

        self.assertEquals( secondCallbackTrace, [] )
        self.assertEquals( self.m_callbackTrace, [] )

        evd_second.register_chain_override( { rpdb2.CEventNull: {} } )
        evd_first.register_callback( self.callback, { rpdb2.CEventNull: {} }, False)
        evd_second.register_callback( secondCallback, { rpdb2.CEventNull: {} }, False)

        # Event on first dispatcher
        ev1 = rpdb2.CEventNull() 
        evd_first.fire_event( ev1 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )
        self.assertEquals( secondCallbackTrace, [] )

        # Event on second dispatcher 
        ev2 = rpdb2.CEventNull() 
        evd_second.fire_event( ev2 )
        self.assertEquals( self.m_callbackTrace, [ ev1 ] )
        self.assertEquals( secondCallbackTrace, [ ev2 ] )



class TestFindBpHint( TestCase ):
    def testReBpHint(self):
        self.assertEqual( test_rpdb2.reBpHint.search( 'asldfkj # BP1\n').group(1), 'BP1' )

class TestRpdb2( TestCase ):

    def testParseConsoleLaunchBackwardCompatibility( self ):
        # Positive tests
        self.assertEqual( (False, None, 'titi' ), rpdb2.parse_console_launch( '-k titi' ) )

        self.assertEqual( (True, None, 'titi -k' ), rpdb2.parse_console_launch( 'titi -k' ) )

        # Negative tests
        self.assertEqual( '', rpdb2.parse_console_launch( '' )[2] )


    def testParseConsoleLaunchWithInterpreter( self ):
        self.assertEqual( (False, 'toto', 'titi' ), rpdb2.parse_console_launch( '-k -i toto titi' ) )
        self.assertEqual( (False, 'toto', 'titi' ), rpdb2.parse_console_launch( '-i toto -k titi' ) )
        self.assertEqual( (True, '"toto tutu"', 'titi' ), rpdb2.parse_console_launch( '-i "toto tutu" titi' ) )
        self.assertEqual( (True, '"toto tutu"', 'titi' ), rpdb2.parse_console_launch( "-i 'toto tutu' titi" ) )
        self.assertEqual( (True, 'toto', 'tutu titi' ), rpdb2.parse_console_launch( '-i toto tutu titi' ) )


        self.assertEqual( (True, None, 'titi -k -i toto' ), rpdb2.parse_console_launch( 'titi -k -i toto' ) )
        self.assertEqual( (True, None, 'titi -i toto' ), rpdb2.parse_console_launch( 'titi -i toto' ) )


if __name__ == '__main__':
    main()