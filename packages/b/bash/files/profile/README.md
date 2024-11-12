Files in this directory must have code that is POSIX compliant, since the file is loaded by all BOURNE compatible shells
If you must use a bash-only function like shopt it must be put in a block that will load it only for bash

e.g.

```
current_shell=$(readlink /proc/$$/exe)
if [ $current_shell = "/usr/bin/bash" ]; then
    shopt -s checkwinsize
fi
```
