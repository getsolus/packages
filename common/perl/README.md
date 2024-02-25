# README for perl scripts

## Documentation and help output

For each script, there should be documentation written in pod and help output.

Docs are read with perldoc. For example:

```bash
perldoc get_unique_updates/get_unique_updates.pl
```

Each script *should* have help output. For example:

```bash
get_unique_updates.pl --help
```

## Running tests

Tests are run with `prove`. To run all tests for a script, run prove on all the test files in the test directory:

```bash
prove get_unique_updates/t/*.t
```