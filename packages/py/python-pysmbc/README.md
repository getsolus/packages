# python-pysmbc test notes for maintainers

Given the relative difficulty of setting up a one-size-fits-all test scenario in the python-pysmbc package.yml proper, this document intends to outline how to manually set up and run the included `nosetests` from a pristine clone of the upstream `pysmbc` repository.

This testing should happen in the package check stage, before building the package for Solus.

## Setup prior to testing

1. Install prerequisites
**NOTE:** may be incomplete, edit as necessary
`sudo eopkg it python3-devel python-nose`

2. Obtain a copy of upstream pysmbc
`git clone https://github.com/hamano/pysmbc.git` as of this writing.

3. Edit `Makefile` to use the `python3` target
Edit the `Makefile` in the file provided by the upstream python repo clone such that `PYTHON=python3`  
Failing to do this will make pysmbc compile against `python` which is presently python-2.7.18 on Solus -- this will not work with the python3-based python-nosetests package installed above.  
After a correct edit, `git diff Makefile` should look like so:  
   ```
   $ git diff Makefile
   diff --git a/Makefile b/Makefile
   index ab0ec61..369e15f 100644
   --- a/Makefile
   +++ b/Makefile
   @@ -1,4 +1,4 @@
   -PYTHON=python
   +PYTHON=python3
    NAME=pysmbc
    VERSION:=$(shell $(PYTHON) setup.py --version)
   ```  
    Consult the upstream `README.md` for detailed build instructions.

4. Set up a password-protected Samba share
The Solus samba config supports setting up shares via the desktop environment file manager. Consult https://getsol.us/articles/software/samba/en/ for details. Make sure the samba user has full control for the samba share.

5. Copy the relevant settings into the `nosetests_/settings.py` file
   The default `./nosetests_/settings.py` file looks like this:
   ```
   # This is setting template.
   # You must change these parameter if you perform test.
   # The following configration will create \\server\share\testdir
   # directory, so user should have write permission.

   WORKGROUP = "WORKGROUP"
   SERVER = "localhost"
   SHARE = "share"
   USERNAME = "user1"
   PASSWORD = "password1"
   ```
   **Edit these values:** _Edit the above to match your local samba settings -- otherwise the tests will fail._

## Running tests

Once the setup prerequisites have been sorted, navigate into the `./nosetests_/` directory in your upstream clone direcotry and run the tests with:

`nosetests`

If successful, the output should look something like:

```
$ nosetests
S...........................
----------------------------------------------------------------------
Ran 28 tests in 1.441s

OK (SKIP=1)
```

Good luck!