#!/usr/bin/env python

LAWORKSVERSION = "0.1"

PROVTYPE_DISKED    = "disked"
PROVTYPE_DISKLESS  = "diskless"
PROVTYPE_DUALBOOT  = "dualboot"
PROVTYPE_WIN       = "windows"

UITYPE_GUI       = "gui"
UITYPE_CLI       = "cli"

STATUS_IMPORTED   = "imported"
STATUS_CREATINGFS = "creatingfs"
STATUS_FIRSTBOOT  = "firstboot"
STATUS_OBSOLETE   = "obsolete"
STATUS_SYNCING    = "syncing"
STATUS_READY      = "ready"

NETTYPE_PROV      = "provision"
NETTYPE_PUB       = "public"
NETTYPE_OTHER     = "other"

NICTYPE_BOOT      = "boot"
NICTYPE_OTHER     = "other"
NICTYPE_PUBLIC    = "public"

LAWORKSROOT_DIR       = "/opt/laworks"
LAWORKSTMPL_DIR       = "%s/etc/templates" % (LAWORKSROOT_DIR)
NODEINFO_TMPL     = "%s/nodeinfo.tmpl" % (LAWORKSTMPL_DIR)
NETBOOT_TMPL      = "%s/mac.pxeboot"   % (LAWORKSTMPL_DIR)
LOCALBOOT_TMPL    = "%s/mac.localboot" % (LAWORKSTMPL_DIR)
AUTO_INSTALL_CMD_TMPL    = "%s/autoinstall.tmpl" % (LAWORKSTMPL_DIR)

PXEROOT_DIR       = "/var/lib/tftpboot"
PXEFILE_DIR       = "%s/pxelinux.cfg"  % (PXEROOT_DIR)

APACHE_USER       = "www-data"
APACHE_GROUP      = "www-data"

CONF_TMPL_DHCPD   = "%s/dhcpd.conf.tmpl" % (LAWORKSTMPL_DIR)
CONF_TMPL_TFTP    = "%s/tftp.tmpl" % (LAWORKSTMPL_DIR)
CONF_TMPL_HTTPD   = "%s/httpd.conf.tmpl" % (LAWORKSTMPL_DIR)

CONF_TMPL_ZONE    = "%s/zone.tmpl" % (LAWORKSTMPL_DIR)
CONF_TMPL_NAMED   = "%s/named.conf.tmpl" % (LAWORKSTMPL_DIR)
CONF_TMPL_REVZONE    = "%s/revzone.tmpl" % (LAWORKSTMPL_DIR)
