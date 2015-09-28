# multitest
 Multiprocess unittest runner for Python's unittest module

### Usage

    python -m multitest discovery --multitest-workers 8 -t . -s .

`multitest` extends the standard `unittest` library, refer to `python -m unittest --help` for basic usage.

Additional parameters can be referred to with `python -m multitest --help`.

### Known Limitation(s)
* Does not handle expectedFailures and unexpectedSuccesses
