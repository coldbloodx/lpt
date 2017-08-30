#!/usr/bin/env python

import re
import sys
import signal
import time
import os

def sig_handler(signum, frame):
    sys.stderr.write("Abort signal caught, exiting...\n")
    sys.exit(0)

class SyslogListener:
    def __init__(self, doc_position='/var/log/syslog'):
        self.syslog = doc_position
        self.syslogfp = file(self.syslog, 'r')
        self.syslogfp.seek(os.SEEK_SET, os.SEEK_END)
        self.log_cur_pos = self.syslogfp.tell()
        self.syslogfp.close()

    def get_mac(self, line):
        if not line:
            return None, None
        pattern = re.compile(r'.* dhcpd: DHCPDISCOVER from ([a-fA-F0-9:]{17}) via ([.a-zA-Z0-9]+)')
        matches = re.match(pattern, line)
        if not matches:
            return None, None
        mac = matches.group(1)
        interface = matches.group(2)
        return mac, interface

    def listen(self):
        self.syslogfp = file(self.syslog, 'r')
        self.syslogfp.seek(os.SEEK_SET, os.SEEK_END)
        cur_pos = self.syslogfp.tell()
        if self.log_cur_pos == cur_pos:
            yield
         
        self.syslogfp.seek(self.log_cur_pos, 0)
        mac_dict = { }
        content = self.syslogfp.readlines()
        for line in content:
            mac, interface = self.get_mac(line.strip())
            if not mac or not interface:
                continue
            print "Found DHCP request from %s, nic = %s" %(mac, interface)
            mac_dict[mac] = interface

        self.log_cur_pos = cur_pos
        self.syslogfp.close()
        yield mac_dict
        time.sleep(1)
