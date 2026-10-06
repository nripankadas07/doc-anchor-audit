# Contributing

Open an issue describing the supported user contract and a minimal synthetic fixture.
Keep changes bounded and document unsupported input rather than silently accepting it.
Run `python -m unittest -v`, compile the module, build the wheel and test the installed
CLI in an empty environment. Add regression tests for behavior changes; preserve
existing expectations unless the documented contract itself changes with explanation.

Support is best effort. No service-level guarantee or paid support is implied.
