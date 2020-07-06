#!/bin/bash

localectl set-locale LANG=en_US.UTF-8
localectl set-keymap us


setcap cap_setuid+ep  /usr/bin/newuidmap
setcap cap_setgid+ep  /usr/bin/newgidmap

ls -l --color=always /usr/bin/newuidmap /usr/bin/newgidmap


