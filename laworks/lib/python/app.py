#!/usr/bin/env python

import os
import sys
import atexit
from optparse import OptionParser

from unipath.path import Path as path

from constant import LAWORKSVERSION
import log

sys.path.append("/opt/laworks/lib/python/")

class LAApp:
    """ base class for all applications to inherit from. """

    def __init__(self, debug=False, master=True, root=True, haslog=False):
        """ Initialize Class variables.  Extend as needed """
        
        if root:
            self.check_run_by_root()
        
        self.name = path(sys.argv[0]).absolute().stem

        if master:
            self.check_run_on_master()


        self.args       = sys.argv
        self.version    = LAWORKSVERSION 

        usage = self.name + " help"
        self.parser = OptionParser(usage)

        if haslog:
            self.logger = log.getapplogger(self.name, debug)

            self.log     = self.logger.info
            self.warnlog = self.logger.warn
            self.errlog  = self.logger.fatal

    def stderrmsg(self, msg, *args):
        """Output messages to STDERR with Internationalization.
        Additional arguments will be used to substitute variables in the
        message output"""
        sys.stderr.write(msg + "\n")

    def stdoutmsg(self, msg, *args):
        """Output messages to STDOUT with Internationalization.
        Additional arguments will be used to substitute variables in the
        message output"""
        sys.stdout.write(msg + "\n")

    def showversion(self, option, opt, value, parser):
        """
        Prints out the version of the tool to screen.
        """
        self.stdoutmsg("%s version %s\n" %(self.name, self.version))
        sys.exit(0)

    def optargs(self, option, opt_str, value, parser):
        '''A callback function that allows parsing CL keys with
        an optional argument. In RE terms, we can parse --foo [arg]?'''
        value = ''
        if parser.rargs:
            arg = parser.rargs[0]
            if not ((arg[:2] == '--' and len(arg)>2) or
                    (arg[:1] == '-'  and len(arg)>1 and arg[1] != '-')):
                value = arg
                del parser.rargs[0]
        setattr(parser.values, option.dest, value)

    def varargs(self, option, opt_str, value, parser):
        '''A callback function that allows parsing CL keys with
        arbitrary # of args. In RE terms, we can parse --foo [arg]*'''

        # 3-liner below allows for mult. instances of the CL option
        # value = getattr(parser.values, option.dest)
        # if not value:
        #     value = []

        value = []
        rargs = parser.rargs # CL args trailing this option
        while rargs:
            arg = rargs[0]
            if ((arg[:2] == '--' and len(arg)>2) or
                (arg[:1] == '-'  and len(arg)>1 and arg[1] != '-')):
                break
            else:
                value.append(arg)
                del rargs[0]
        setattr(parser.values, option.dest, value)

    def force_single_instance(self):
        if len(sys.argv) >= 1:
            app = path(sys.argv[0]).stem

            if self.islock():
                msg = 'An instance of %s is already running ' % app + \
                      '(lock file: %s).' % self.getlockfile()
                self.errorlog(msg)
                sys.exit(1)

            atexit.register(self.unlock)
            self.lock()

    def lock(self):
        if len(sys.argv) >= 1:
            lock = self._getappname()
            lock.write_file('')

    def unlock(self):
        if len(sys.argv) >= 1:
            lock = self._getappname()
            if lock.exists(): lock.remove()

    def islock(self):
        if len(sys.argv) >= 1:
            lock = self._getappname()
            return lock.exists()
        else:
            return None

    def getlockfile(self):
        if len(sys.argv) >= 1:
            lock = self._getappname()
            return lock
        else:
            return None

    def exit_success_and_unlock(self):
        if self.islock():
            self.unlock()
        sys.exit(0)

    def exit_failed_and_unlock(self, exitCode=-1):
        if self.islock():
            self.unlock()
        sys.exit(exitCode)


    def _getappname(self):
        """Returns the full path to the current program"""
        return path('/var/lock/') + self.name

    def ismaster(self):
        if os.path.exists('/etc/.master'):
            return True
        return False

    def check_run_by_root(self, quit=True):
        if os.getuid():
            self.stderrmsg("The tool must run by root")
            sys.exit(-1)

    def check_run_on_master(self, quit=True):
        if not self.ismaster():
            self.stderrmsg('The tool must run on master node')
            if quit:
                if self.islock():
                    self.unlock()
                sys.exit(-1)
            return False
        return True
