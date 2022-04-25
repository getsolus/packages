The following is a comprehensive list of test failures or "errors":

FAIL: tests/tail-2/inotify-dir-recreate
FAIL: tests/misc/shuf-reservoir
FAIL: tests/misc/sort-stale-thread-mem
FAIL: tests/misc/sort-u-FMR
FAIL: tests/misc/xattr
FAIL: tests/cp/copy-FMR
FAIL: tests/ls/stat-free-symlinks
FAIL: tests/rmdir/symlink-errors
FAIL: tests/rm/no-give-up

ERROR: tests/tail-2/inotify-rotate-resources

ALSO NOTE:
Currently, without gl_cv_func_chown_ctime_works=yes forced enabled
the m4 check `checking whether chown always updates ctime` fails
which causes the preserve-slink-time test to fail. See T10232.
