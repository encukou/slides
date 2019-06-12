#! /bin/bash
while true; do
    echo "Running $@ with live-reload..."
    ls *.py | entr -dr -- $@
done
