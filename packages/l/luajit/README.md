# LuaJIT notes

## LuaJIT "releases"

- LuaJIT does not do releases and wants packagers to build from latest git, see https://luajit.org/download.html
- LuaJIT has an internal version number that our packaging uses: major.minor.timestamp.
- So far as David can tell, this version number is generated at buid time from the last commit timestamp, and is not discoverable by browsing the repository.

## Determining the version number to update luajit package

- Update to a recent git snapshot of the v2.1 branch, include a placeholder release number, build it
- Observe new version number in abi_libs, or last few lines of output from build process
- Edit package.yml with new version number
- Build and install package
- Run `luajit -v` as a basic function test
