## Updating Firefox

Bump the release:

`go-task bump`

Build the langpack:

`./langpacks.sh $version` e.g `./langpacks.sh 123.0`

The script will output the relevant information to update the package.yml with:
```
123.0/source/firefox-123.0.source.tar.xz : 9e885abdaddb14cd4f313c1575282fec6af5901f445e9744fe24e2ea837d4cb7
firefox-123.0-langpacks.tar.zst : c3b291919797d7f38b6cdbe61ec612e615f01d6759d88a336d06f744ce91e9f7
```
Upload the langpack you just built:

`rsync -avhP firefox-123.0-langpacks.tar.zst packages.getsol.us:`

Shell in and move the langpack to the correct directory:

`sudo mv firefox-123.0-langpacks.tar.zst /srv/www/sources/mozilla/firefox/`

You are now ready to start building.
