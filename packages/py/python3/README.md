# Python 3 update policy

As Solus is now using [Nuitka](https://nuitka.net) to build a stand-alone, py3-based version of [eopkg](https://github.com/getsolus/eopkg/tree/python3), it follows that the python3 version in the getsolus package repo must never be updated past what Nuitka supports.

Please keep this in mind when planning python3 stack upgrades.

## Currently supported python3 version in Nuitka

As of ultimo February 2024, the latest fully supported version of python3 in Nuitka is Python 3.11.
