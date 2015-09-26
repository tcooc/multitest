__version__ = '0.1.0'

import os
import sys
import time
from StringIO import StringIO
from multiprocessing import Pool, TimeoutError
from unittest import defaultTestLoader, TestSuite, TextTestRunner


class _WritelnDecorator:
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        return getattr(self.stream,attr)

    def writeln(self, *args):
        if args: apply(self.write, args)
        self.write('\n') # text-mode streams translate to \r\n if needed


class _AggregateTestResult:
    def __init__(self):
        self.testsRun = 0
        self.errors = 0
        self.failures = 0
        self.skipped = 0
        self.errors_text = ''
        self.successful = True

    def populate(self, result):
        self.testsRun = result.testsRun
        self.errors = len(result.errors)
        self.failures = len(result.failures)
        self.skipped = len(result.skipped)

        result.stream = _WritelnDecorator(StringIO())
        result.dots = False
        result.showAll = False
        result.printErrors()
        self.errors_text = result.stream.getvalue()

        self.successful = result.wasSuccessful()
        return self

    def merge(self, other):
        self.testsRun += other.testsRun
        self.errors += other.errors
        self.failures += other.failures
        self.skipped += other.skipped
        self.errors_text = self.errors_text + other.errors_text
        self.successful = self.successful and other.successful
        return self


def _run_test(name, runner_args):
    stream = _WritelnDecorator(StringIO())
    runner_args['stream'] = stream

    test = defaultTestLoader.loadTestsFromName(name)
    runner = TextTestRunner(**runner_args)

    native_test_result = runner._makeResult()  # small hack for simpler code
    test(native_test_result)

    test_result = _AggregateTestResult()
    return stream.getvalue(), test_result.populate(native_test_result)


class MultiprocessTestRunner:
    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1):
        self.stream = _WritelnDecorator(stream)
        self.runner_args = {'descriptions': descriptions, 'verbosity': verbosity}

    def run(self, suite, workers=4, timeout=10):
        tests = self._create_tests_set(suite)

        worker_pool = Pool(workers)
        worker_tasks = []
        aggregate_test_results = _AggregateTestResult()

        start_time = time.time()
        for test in tests:
            worker_tasks.append(worker_pool.apply_async(_run_test, args=(test, self.runner_args)))
        worker_pool.close()

        try:
            for worker_task in worker_tasks:
                output, test_result = worker_task.get(timeout)
                self.stream.write(output)
                aggregate_test_results.merge(test_result)
        except TimeoutError as e:
            self.stream.writeln('a child process timed out')
            raise e
        stop_time = time.time()

        self._print_test_results(start_time, stop_time, aggregate_test_results)

        return aggregate_test_results

    def _create_tests_set(self, suite):
        index = 0
        children = [suite]
        tests = set()
        while index < len(children):
            child = children[index]
            if isinstance(child, TestSuite):
                for suite_child in child:
                    children.append(suite_child)
            else:
                tests.add('%s.%s' % (child.__module__, child.__class__.__name__))
            index += 1
        return tests

    def _print_test_results(self, start_time, stop_time, aggregate_test_results):
        run = aggregate_test_results.testsRun
        time_taken = float(stop_time - start_time)
        self.stream.writeln(aggregate_test_results.errors_text)
        self.stream.writeln('Ran %d test%s in %.3fs' % (run, run == 1 and '' or 's', time_taken))
        self.stream.writeln()
        if not aggregate_test_results.successful:
            self.stream.write('FAILED (')
            failed = aggregate_test_results.failures
            errors = aggregate_test_results.errors
            if failed:
                self.stream.write('failures=%d' % failed)
            if errors:
                self.stream.write('%serrors=%d' % (', ' if failed else '', errors))
            self.stream.writeln(')')
        else:
            self.stream.writeln('OK')

__all__ = ['MultiprocessTestRunner']
