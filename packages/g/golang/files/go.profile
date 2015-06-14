# Begin /etc/profile.d/50-go.sh

if [ ! -n "$GOPATH" ] ; then
    export GOPATH="$HOME/go"
fi

export PATH="$PATH:$GOPATH/bin"

# End /etc/profile.d/50-go.sh