#!/bin/bash
if [ -a /etc/mongodb/mongodb.conf ]; then
        /usr/bin/mongod --config /etc/mongodb/mongodb.conf
    else
        /usr/bin/mongod --config /usr/share/defaults/mongodb/mongodb.conf
fi
