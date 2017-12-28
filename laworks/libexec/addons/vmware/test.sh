#!/bin/bash

echo abcd efgh | awk '{print "'$1'","'$2'",$1,$2}'

