# Solus LMMS maintainer guidelines
	
This document includes notes on maintaining and testing LMMS and its various features.

## VST support

For VST support, LMMS uses Wine. It makes sense to pull Wine as a rundep as attempting to use Vestige without Wine results in a very broken-looking behavior and doesn't produce an error message except for command line. It should be noted that currently (as of 1.2-stable branch) LMMS supports only 32-bit VST plugins through Wine. 64-bit plugins will silently fail.

## Testing VST support

There are several VST instruments known to work with LMMS. Synth1 is a good testing candidate, as it seems to work reliably on many DAWs.
Synth1 is available at https://daichilab.sakura.ne.jp/softsynth/index.html#down
A listing for tested VSTs can be found here https://lmms.io/wiki/index.php?title=Tested_VSTs

You should run LMMS once to have the configuration folders created to ~/Documents/lmms
VST plugins go to ~/Documents/lmms/plugins/vst regardless of whether they are instruments or effects.

To test your plugin, drag Vestige to the Sound Editor or Beat+Bassline Editor and open its properties.
Click on a green folder icon next to the "No VST-plugin loaded" text and search for your plugin. The plugin interface should pop up after loading and the plugin should produce a sound when playing with either keyboard or MIDI.

To test effect plugins, open FX-Mixer, click Add effect button on the effects chain and search for your plugin. The plugin should load without problems and alter the sound how it's supposed to.

## Unknown symbol errors

The dependency discover phase shows errors for these libraries:
- libZynAddSubFxCore.so
- libgig.so.9
- libvstbase.so
- libZynAddSubFxCore.so
These can be ignored as they're private libraries used only by LMMS.
