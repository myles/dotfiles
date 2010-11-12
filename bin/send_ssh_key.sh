#!/bin/bash

## Adapted form jonshea work at http://textsnippets.com/posts/show/374

## USAGE: send_ssh_key.sh username remote_server

#set -v
username=$1
remote_server=$2

if [[ -z "$1" ]]; then
        echo "send_ssh_key.sh: wrong number of arguments"
        echo "Usage: send_ssh_key username remote_server"
elif [[ -z "$2" ]]; then
        echo "send_ssh_key.sh: wrong number of arguments"
        echo "Usage: send_ssh_key username remote_server"
else
        ## Pipe the public key to ssh, then remotely touch the file to 
        ## make sure it will be there, and concat to the end of it.
        ## Might work without the touch?
        cat ~/.ssh/id_rsa.pub | ssh ${username}@${remote_server} "touch ~/.ssh/authorized_keys && cat - >> ~/.ssh/authorized_keys"
fi

exit 0
