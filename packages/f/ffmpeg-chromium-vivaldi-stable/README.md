## Updating ffmpeg-chromium-vivaldi-stable

`ffmpeg-chromium-vivaldi-stable` must be updated whenever `vivaldi-stable` updates to a newer **major** version of its Chromium base, failure to do so will break some video playback.

Example: vivaldi-stable 6.8.3381.44 updated its Chromium base from 124.* to 126.* so we must update ffmpeg-chromium-vivaldi-stable.

We need to get the correct commit to build `ffmpeg-chromium-vivaldi-stable` from to be compatible with a Chromium 126 base. We can get this using the value of `ffmpeg_revision` from the DEPS file for any Chromium release in the 126 series.

Lets use Chromium 126.0.6478.24 https://github.com/chromium/chromium/blob/126.0.6478.24/DEPS#L498

```
'ffmpeg_revision': '092f84b6141055bfab609b6b2666b724eee2e130',
```

Now we have our commit to build ffmpeg-chromium from and can set the version to the **major** number of the Chromium version.

`version: '126'`

#### Testing

Sites to test codecs & widevine:

- https://demo.castlabs.com
- https://bitmovin.com/demos/drm
- https://help.vivaldi.com/desktop/media/html5-proprietary-media-on-linux/
