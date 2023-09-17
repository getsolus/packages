# Begin /usr/share/defaults/etc/profile.d/50-google-cloud-sdk.sh

export CLOUDSDK_ROOT_DIR=/usr/share/google-cloud-sdk
export CLOUDSDK_PYTHON=python3
export CLOUDSDK_PYTHON_ARGS=-S
export GOOGLE_CLOUD_SDK_HOME=$CLOUDSDK_ROOT_DIR
export PATH=$PATH:$CLOUDSDK_ROOT_DIR/bin

# End /usr/share/defaults/etc/profile.d/50-google-cloud-sdk.sh
