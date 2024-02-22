## Updating Thunderbird

Bump the release:

`go-task bump`

Build the langpack:

`./langpacks.sh $version` e.g `./langpacks.sh 115.8.0`

The script will output the relevant information to update the package.yml with:
```
115.8.0/source/thunderbird-115.8.0.source.tar.xz : 804c8cb0896b2cf24643621c0c879c9bb8c56abd517eb9d603cec6fdb91561c7
thunderbird-115.8.0-langpacks.tar.zst : 648ce1b4360836b18f2c1e6bb443efd6f8f2ef58971bf9dbfc68f0d8142ddd27
```
Upload the langpack you just built:

`rsync -avhP thunderbird-115.8.0-langpacks.tar.zst packages.getsol.us:`

Shell in and move the langpack to the correct directory:

`sudo mv thunderbird-115.8.0-langpacks.tar.zst /srv/www/sources/mozilla/thunderbird/`

You are now ready to start building.
