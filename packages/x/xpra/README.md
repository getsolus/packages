# Packaging instructions for xpra

xpra tries hardly to use Xdummy as a driver. But Xdummy doesn't work out-of-the box with solus. Instead xvfb should be used. The switch '--without-Xdummy' doesn't change the default configuration. So a patch is needed to set a minimal working configuration.

Also the setup procedure has hardwired paths and linux distro detection. So some paths have to be patched. 

- /lib/systemd/system -> /usr/lib64/systemd/system
- /etc/dbus-1/system.d -> /usr/share/dbus-1/system.d
- /etc/default -> /usr/share/defaults
