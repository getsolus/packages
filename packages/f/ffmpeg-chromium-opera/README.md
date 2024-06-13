## Updating ffmpeg-chromium-opera

`ffmpeg-chromium-opera` must be updated whenever `opera-stable` updates to a newer **major** version of its Chromium base, failure to do so will break some video playback.

Example: opera-stable 111.0.5168.25 updated its Chromium base from 124.* to 125.* so we must update ffmpeg-chromium-opera.

We need to get the correct commit to build `ffmpeg-chromium-opera` from to be compatible with a Chromium 125 base. We can get this using the value of `ffmpeg_revision` from the DEPS file for a Chromium release in the 125 series. Since opera-stable updated to 125.0.6422.142, that is the version we are going to use.

https://github.com/chromium/chromium/blob/125.0.6422.142/DEPS#L498

```
'ffmpeg_revision': '901248a373cbbe7af68fb92faf3be7d4f679150d',
```

Now we have our commit to build ffmpeg-chromium-opera from and can set the version to the **major** number of the Chromium version.

`version: '125'`

#### Testing

Sites to test codecs & widevine:

- https://demo.castlabs.com
- https://bitmovin.com/demos/drm
- https://help.vivaldi.com/desktop/media/html5-proprietary-media-on-linux/
