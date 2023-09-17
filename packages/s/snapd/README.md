# snapd AppArmor confinement testing

To ensure that we don't unwittingly break snapd AppArmor confinement, it is useful to have a vetted set of tests with the same starting and ending point.

## Reset the snapd environment

To test snapd.apparmor confinement, start by resetting the snapd environment to a known good state:

```
# remove the hello-world snap if installed
sudo snap remove hello-world
# remove the AppArmor cache
sudo rm -rf /var/cache/apparmor
# reinstall snapd and apparmor and ensure that aa-lsm-hook and usysoncf triggers run
sudo eopkg it --reinstall snapd apparmor
```

If you have more than the hello-world snap installed, please `sudo snap remove` all installed snaps.

At this point, either relog or reboot the machine on which the test is being run.

## Install and check the `hello-world` snap

After the relog/reboot, check that the following works:

```
# check the status of the snapd.apparmor.service (it should be enabled and running in the green)
sudo systemctl status snapd.apparmor.service
# install and run the hello-world snap
sudo snap install hello-world
snap run hello-world
```

The expected output of `snap run hello-world` with a correctly configured snapd AppArmor confinement:

```
$ snap run hello-world
Hello World!
```

If something is wrong with how the snapd AppArmor confinement is set up, the error state will typically look something like this:

```
$ snap run hello-world
snap-confine has elevated permissions and is not confined but should be. Refusing to continue to avoid permission escalation attacks
Please make sure that the snapd.apparmor service is enabled and started.
```
