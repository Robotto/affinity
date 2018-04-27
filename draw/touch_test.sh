#!/bin/sh

# ---- Global variables ----

input=/dev/input/event19
code_prefix="ABS"
code="${code_prefix}_[XY]"
val_regex=".*(${code_prefix}_\(.\)), value \([-]\?[0-9]\+\)"
val_subst="\1=\2"

# ---- Functions ----

send_axis() {
    # 1. Convert axis value ($1) from device specific units
    # 2. Send this axis value via UDP packet
    echo $1
}

process_line() {  
    while read line; do
        axis=$(echo $line | grep "^Event:" | grep $code | \
               sed "s/$val_regex/$val_subst/")

        if [ -n "$axis" ]; then
            send_axis $axis
        fi
    done
}

# ---- Entry point ----

if [ $(id -u) -ne 0 ]; then
    echo "This script must be run from root" >&2
    exit 1
fi

evtest $input | process_line
