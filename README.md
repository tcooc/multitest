# multitest
 Multiprocess unittest runner for Python's unittest module

### Usage

    from multitest import MultiprocessTestRunner
    MultiprocessTestRunner(stream=sys.stderr, descriptions=True, verbosity=1).run(suite, workers=4, timeout=10)


### Examples

Create tests as usual:

    from unittest import TestCase

    class TestTest(TestCase):
        def test_test(self):
          self.assertTrue(True)

Then load the suite and run it:

    from unittest import defaultTestLoader
    from multitest import MultiprocessTestRunner

    suite = defaultTestLoader.loadTestsFromTestCase(TestTest)
    MultiprocessTestRunner().run(suite)

Outputs:

    .
    Ran 1 tests in 0.004s

    OK


### Known Limitations
* Does not handle expectedFailures and unexpectedSuccesses
* Does not handle errors inside workers as elegantly as it should
* Does not communicate errors as well as it should
