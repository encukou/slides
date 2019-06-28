#! /bin/bash -ex
while true; do
    ls *.py | entr -dr -- /bin/bash -c "clear; date; echo 'Running with live-reload: $*'; echo; $*"
done
