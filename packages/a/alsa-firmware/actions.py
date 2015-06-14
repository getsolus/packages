#!/usr/bin/python


from pisi.actionsapi import get, autotools, pisitools

# Prevent PiSi from stripping these files (won't work)
NoStrip = ["/usr/share/alsa/firmware/mixartloader/miXart8.elf",
           "/lib/firmware/mixart/miXart8.elf"]


# Already provided by linux-firmware package
Removals = ["/lib/firmware/sb16/ima_adpcm_init.csp",
            "/lib/firmware/sb16/ima_adpcm_capture.csp",
            "/lib/firmware/ctefx.bin",
            "/lib/firmware/sb16/ima_adpcm_playback.csp",
            "/lib/firmware/yamaha/ds1_dsp.fw",
            "/lib/firmware/ess/maestro3_assp_minisrc.fw",
            "/lib/firmware/sb16/mulaw_main.csp",
            "/lib/firmware/yamaha/yss225_registers.bin",
            "/lib/firmware/ess/maestro3_assp_kernel.fw",
            "/lib/firmware/yamaha/ds1_ctrl.fw",
            "/lib/firmware/sb16/alaw_main.csp",
            "/lib/firmware/korg/k1212.dsp",
            "/lib/firmware/yamaha/ds1e_ctrl.fw",
            "/lib/firmware/ctspeq.bin"]


def setup():
    autotools.configure()


def build():
    autotools.make()


def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    for removal in Removals:
        pisitools.remove(removal)

    pisitools.dodoc("COPYING")
