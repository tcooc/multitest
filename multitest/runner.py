import sys
import time
import traceback
from StringIO import StringIO
from multiprocessing import Pool, TimeoutError
from unittest import defaultTestLoader, TestSuite, TextTestResult, TextTestRunner

DEFAULT_WORKERS = 4
DEFAULT_TIMEOUT = 10


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream,attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n') # text-mode streams translate to \r\n if needed


class _AggregateTestResult:
    def __init__(self):
        self.testsRun = 0
        self.errors = 0
        self.failures = 0
        self.skipped = 0
        self.errors_text = []
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
        self.errors_text = [result.stream.getvalue()]

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

    # Exists for contract with TestProgram
    def wasSuccessful(self):
        return self.successful


def _run_test(name, runner_args, test=None, runner_class=TextTestRunner, result_class=TextTestResult):
    try:
        stream = _WritelnDecorator(StringIO())
        runner_args['stream'] = stream

        if test is None:
            test = defaultTestLoader.loadTestsFromName(name)
        runner = runner_class(**runner_args)

        native_test_result = result_class(
            runner.stream, runner_args['descriptions'], runner_args['verbosity'])
        test(native_test_result)

        test_result = _AggregateTestResult()
        return stream.getvalue(), test_result.populate(native_test_result)
    except Exception:
        # Pass exception info to parent process
        raise Exception(''.join(traceback.format_exception(*sys.exc_info())))


class MultiprocessTestRunner(object):
    def __init__(self, stream=sys.stderr, descriptions=True, verbosity=1, failfast=False, buffer=False,
                 workers=DEFAULT_WORKERS, timeout=DEFAULT_TIMEOUT):
        self.stream = _WritelnDecorator(stream)
        self.runner_args = {
            'descriptions': descriptions,
            'verbosity': verbosity,
            'failfast': failfast,
            'buffer': buffer
        }
        self.workers = workers
        self.timeout = timeout

    def run(self, suite):
        tests, failed = self._create_tests_set(suite)

        worker_pool = Pool(self.workers)
        worker_tasks = []
        aggregate_test_results = _AggregateTestResult()

        if self.runner_args['verbosity'] >= 2:
            self.stream.writeln('Running tests using {workers} workers with {timeout}s timeout'
                                .format(workers=self.workers, timeout=self.timeout))

        start_time = time.time()
        for fail in failed:
            output, test_result = _run_test(fail.__class__.__name__, self.runner_args, test=fail)
            self.stream.write(output)
            aggregate_test_results.merge(test_result)

        for test in tests:
            worker_tasks.append((test, worker_pool.apply_async(_run_test, args=(test, self.runner_args))))
        worker_pool.close()

        for worker_task in worker_tasks:
            try:
                output, test_result = worker_task[1].get(self.timeout)
            except TimeoutError as e:
                self.stream.writeln('A child process timed out (%s)' % worker_task[0])
                raise e
            self.stream.write(output)
            aggregate_test_results.merge(test_result)
        worker_pool.join()
        stop_time = time.time()

        self._print_test_results(start_time, stop_time, aggregate_test_results)

        return aggregate_test_results

    def _create_tests_set(self, suite):
        index = 0
        children = [suite]
        tests = set()
        failed = []
        while index < len(children):
            child = children[index]
            if isinstance(child, TestSuite):
                for suite_child in child:
                    children.append(suite_child)
            elif child.__module__.startswith('unittest'):
                # loader failed
                failed.append(child)
            else:
                tests.add('%s.%s' % (child.__module__, child.__class__.__name__))
            index += 1
        return tests, failed

    def _print_test_results(self, start_time, stop_time, aggregate_test_results):
        run = aggregate_test_results.testsRun
        time_taken = float(stop_time - start_time)
        self.stream.writeln()
        for error_text in aggregate_test_results.errors_text:
            self.stream.write(error_text)
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
