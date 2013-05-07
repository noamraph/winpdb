
# Python
import unittest, subprocess, threading
import os, time, socket, sys, re

if sys.version_info[:2] < (2,6):
    from StringIO import StringIO
else:
    from io import StringIO

if sys.version_info[:2] < (2,7):
    CREATE_NEW_PROCESS_GROUP=0x200
else:
    CREATE_NEW_PROCESS_GROUP=subprocess.CREATE_NEW_PROCESS_GROUP

# RPDB2
import rpdb2

PYTHON='C:/Python27/python.exe'
DEBUGME=u'debugme.py'
RPDB2 = 'rpdb2.py'
PWD=u'toto'

STEPS = [ 'f1', 'f2', 'f3', 'done' ]

class FakeStdin:
    def __init__(self):
        self.please_stop = False
        self.lines = []
        self.dispStdin = True

    def appendCmd( self, l ):
        cmd = l if (l[-1] == '\n') else (l + '\n')
        self.lines.append( l )

    def readline(self):
        while not self.please_stop:
           if len(self.lines):
                p = self.lines.pop(0)
                if self.dispStdin:
                    sys.stdout.write( 'stdin: %s\n' % (p[:-1] if p[-1] == '\n' else p) )
                return p
        time.sleep(0.1)

def dbg( t ):
    print( '>>>>>> %s <<<<<<' % t )

class Rpdb2Stdout(StringIO):
    def __init__(self, *args):
        StringIO.__init__(self, *args)
        self.attached = False

    reAttached = re.compile(r'\*\*\* Successfully attached to.*')
    reDetached = re.compile(r'\*\*\* Detached from script.*' )

    def write(self,t):
        if self.reAttached.match( t ):
            self.attached = True
        elif self.reDetached.match(t):
            self.attached = False

        sys.stdout.write( '%s' % t )


class TestRpdb2Stdout( unittest.TestCase ):
    def testReAttached( self ):
        self.assertNotEqual( Rpdb2Stdout.reAttached.match( '*** Successfully attached to\n' ), None )

class TestRpdb2( unittest.TestCase ):

    def setUp(self):
        self.cleanStepFiles()
        self.console = None
        self.sm = None
        self.fakeStdin = FakeStdin()
        self.rpdb2Stdout = Rpdb2Stdout()
        self.script = subprocess.Popen( [ PYTHON, RPDB2, '-d', '--pwd=%s' % PWD, os.path.join( 'tests', DEBUGME ) ], 
                        creationflags=CREATE_NEW_PROCESS_GROUP, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )

    def cleanStepFiles(self):
        for fname in STEPS:
            if os.path.exists( fname ):
                os.unlink( fname )

    def tearDown(self):
        dbg( 'Teardown' )
        self.cleanStepFiles()
        if self.console:
            if self.rpdb2Stdout.attached:
                dbg( 'Teardown: Stopping...' )
                self.fakeStdin.appendCmd('stop\n')
                time.sleep(1.0)

                #dbg( 'Teardown: Detaching...' )
                #self.fakeStdin.appendCmd('detach\n')
                #time.sleep(1.0)

            dbg( 'Teardown: Exiting...' )
            self.fakeStdin.appendCmd('exit\n')
            time.sleep(1.0)

            # dbg( 'console exit ok' )
            self.console.join( 1.0 )
            # dbg( 'console join ok' )
            self.sm.shutdown()
            # dbg( 'sm shutdown ok' )
            time.sleep(1.0)
            dbg( 'Teardown: Console done' )

        dbg( 'Teardown.Script: check if finished')
        if self.script.poll() != None: return

        dbg( 'Teardown.Script: check if finished after 1 sec')
        time.sleep(1.0)
        if self.script.poll() != None: return

        dbg( 'Teardown.Script: terminate()')
        self.script.terminate()
        if self.script.poll() != None: return
        time.sleep(1.0)
        if self.script.poll() != None: return

        dbg( 'Teardown.Script: kill()')
        self.script.kill()
        if self.script.poll() != None: return
        time.sleep(1.0)
        if self.script.poll() != None: return

        raise ValueError( 'Error, script not terminated: pid=%d' % self.script.pid )


    def testGo( self ):
        fAttach=True
        fchdir=False,
        _rpdb2_pwd=PWD
        fAllowUnencrypted=True
        fAllowRemote=False
        host='localhost'
        command_line=DEBUGME
        fSplit=True

        self.sm = rpdb2.CSessionManager(_rpdb2_pwd, fAllowUnencrypted, fAllowRemote, host)
        self.console = rpdb2.CConsoleInternal(self.sm, stdout=self.rpdb2Stdout, stdin=self.fakeStdin, fSplit=fSplit )
        self.console.start()

        time.sleep(1.0)

        self.fakeStdin.appendCmd( "attach %s\n" % DEBUGME )
        startCountDown = time.time()
        while time.time() - startCountDown < 10.0:
            time.sleep(1.0)
            if self.rpdb2Stdout.attached: 
                break
        self.assertEqual( self.rpdb2Stdout.attached, True )

        self.fakeStdin.appendCmd( "go" )
        time.sleep(1.0)

        assert os.path.exists( 'f1' )
        assert os.path.exists( 'done' )

if __name__ == '__main__':
    unittest.main()
