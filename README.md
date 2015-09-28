# multitest
 Multiprocess unittest runner for Python's unittest module

### Getting Started

Simply replacing your test command `python -m unittest [options]` with `python -m multitest [options]` should be enough to get it to run the tests.

If your tests depend on some external state, more work may be required to get tests working. For example, if multiple tests create/delete `README.txt`, it will be necessary to generate an unique name for each `TestCase`.

### Usage

    python -m multitest discovery --multitest-workers 4 --multititest-timeout 10 -t . -s .

`multitest` extends the standard `unittest` library, refer to `python -m unittest --help` for basic usage.

Additional parameters can be referred to with `python -m multitest --help`.

### Scripting

`multitest.MultiprocessTestRunner` is the test runner. It shares a similar constructor to `unittest.TestRunner` in addition to the `workers` and `timeout` arguments.

    from unittest import defaultTestLoader
    from multitest import MultiprocessTestRunner
    suite = defaultTestLoader.loadTestsFromModule(my_module) # load the test suites using any method
    MultiprocessTestRunner(stream=my_stream, verbosity=2, workers=4, timeout=10).run(suite)

### Known Limitation(s)
* Does not handle expectedFailures and unexpectedSuccesses
