#!/usr/bin/env python

import logging
import os
import sys

from dbitem import OS, makeos

try:
    import subprocess
except:
    from popen5 import subprocess


def objs2dict(objs, key):
    retdict = {} 
    for obj in objs:
        tmpdict = {}
        tmpdict.update(obj.__dict__)
        for okey in tmpdict.keys():
            if okey.startswith('_') or okey.startswith('__'):
                tmpdict.pop(okey)

        retdict[tmpdict[key]] = tmpdict

    return retdict

def getmyos():
    cmd = 'lsb_release -is' 
    out, err, ret = runcmd(cmd)
    osname = out[0].strip()

    cmd =  'lsb_release -rs'
    out, err, ret = runcmd(cmd)
    ver = out[0].strip()

    osmajor, osminor = ver.split(".")

    os = makeos(["%s%s" %(osname,ver),  osname.lower(), osmajor, osminor, "linux", None])

    return os

def errout(msg):
    sys.stderr.write("%s\n" % msg)

def errexit(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

def runcmd(cmd):
    executor = CmdExecutor()
    return  executor.run_cmd(cmd)

def parseconf(conf="/opt/laworks/etc/install.conf"):
    try:
        fp = open(conf, 'r')
        content = fp.readlines()
        if not content: return None
        content = [ line.strip()  for line in content if (not line.startswith("#")) and  (len(line.strip()) > 0) ]
        ret = eval(' '.join(content))
        return ret
    except Exception, e:
        return None

class CmdExecutor(object):
    def __init__(self, logger=None):
        self.logger = logger
        if not self.logger:
            # dummy logger
            self.logger = logging.getLogger('dummy')

    def run_cmd(self, cmdline, logcmdline=True, logresult=False, env=None):
        # Runs a command and returns this tuple: 
        #     ([stdout msgs], [stderr msgs], returncode)

        if logcmdline:
            self.logger.debug("++ %s" % cmdline)
        
        p = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env)
        sout, serr = p.communicate()
        outlines = sout.split('\n')
        errlines = serr.split('\n')
        retcode = p.returncode

        if logresult:
            self.logger.debug("++ retcode=%s" % retcode)
            if sout:
                self.logger.debug("++ sout=%s" % sout)
            if serr:
                self.logger.debug("++ serr=%s" % serr)

        return outlines, errlines, retcode

    def run_cmd_quietly(self, cmdline):
        return self.run_cmd(cmdline, logcmdline=False, logresult=False)

class CommandExecError(Exception): pass
class Command(object):
    """wrapper of subprocess
    provide simple interface to execute command
    PARAMS:
        command   the command to be executed.
        logging   whether log the output of command.
        logger    the logger handler to write the command output.
        

    Example:
        cat = Command('cat /etc/passwd')
        if cat() == 0:
            content = cat.getStdout()
    """

    def __init__(self, command, logging=False, logger=None,
                 dump_to_tty=False, exception_on_failed=False):
        self.command = command
        self.logging = logging
        self.logger = logger
        self.dump_to_tty = dump_to_tty
        self.exception_on_failed = exception_on_failed

        self.retcode = 0
        self.stdout = None
        self.stderr = None

    def __call__(self):
        """execute the command and reture it's exit code"""

        assert(type(self.command) in [str, unicode])
        assert(len(self.command) > 0)

        if self.logging:
            proc = subprocess.Popen(self.command, shell=True, bufsize=-1,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, close_fds=True)
        else:
            proc = subprocess.Popen(self.command, shell=True, bufsize=0,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.stdout, self.stderr = proc.communicate()
        self.retcode = proc.wait()
        
        if self.logging:
            if self.logger:
                if len(self.stdout) > 0:
                    self.logger.info(self.stdout)
                if len(self.stderr) > 0:
                    self.logger.error(self.stderr)

            if self.dump_to_tty:
                if len(self.stdout) > 0:
                    sys.stdout.write(self.stdout)
                if len(self.stderr) > 0:
                    sys.stderr.write(self.stderr)

        if self.exception_on_failed and self.retcode != 0:
            raise CommandExecError('Command execution failed, due to %s' % self.stderr)

        return self.retcode

    def get_stdout(self):
        """return the standard output of the command."""
        return self.stdout

    def get_stderr(self):
        """return the standard error output of the command."""
        return self.stderr

    def get_retval(self):
        return self.retcode


if __name__ == '__main__':
    cmd_executor = CmdExecutor()
    out, err, ret = cmd_executor.run_cmd('ls')
    if ret:
        print err
    else:
        print out

    out, err, ret = cmd_executor.run_cmd('ls  /asdfasdf')
    if ret:
        print err
    else:
        print out

    test_cmd = Command('ls /')
    if test_cmd():
        print test_cmd.get_stderr()
    else:
        print test_cmd.get_stdout()


    test_cmd = Command('ls /asdfasdf')
    if test_cmd():
        print test_cmd.get_stderr()
    else:
        print test_cmd.get_stdout()


    conf = parseconf("/opt/laworks/etc/install.conf")
    if not conf:
        print "error, conf not parsed"
    else:
        print "conf content:"
        print conf
