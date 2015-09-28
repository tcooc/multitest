def main():
    import argparse
    from unittest import TestProgram
    from multitest import MultiprocessTestRunner
    from multitest.runner import DEFAULT_TIMEOUT, DEFAULT_WORKERS

    prog = 'python -m multitest'
    parser = argparse.ArgumentParser(
        prog=prog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Accepts the same arguments as the unittest program with the additions below.\n'
                    'see: python -m unittest --help',
        epilog='examples:\n'
               '%(prog)s test_module --multitest-timeout 60          - run tests from test_module with 60s timeout\n'
               '%(prog)s discover --multitest-workers 8 -s test    - run tests from test directory using 8 workers'
               % {'prog': prog})
    parser.add_argument('--multitest-workers', type=int, default=DEFAULT_WORKERS, dest='workers',
                        help='Number of worker process (default %s)' % DEFAULT_WORKERS)
    parser.add_argument('--multitest-timeout', type=int, default=DEFAULT_TIMEOUT, dest='timeout',
                        help='Test timeout in seconds (default %s)' % DEFAULT_TIMEOUT)
    parsed = parser.parse_known_args()[0]

    class _MultiTestProgram(TestProgram):
        USAGE = ''

    class _MultiprocessTestRunner(MultiprocessTestRunner):
        def __init__(self, *args, **kwargs):
            kwargs['workers'] = parsed.workers
            kwargs['timeout'] = parsed.timeout
            super(_MultiprocessTestRunner, self).__init__(*args, **kwargs)

    _MultiTestProgram(module=None, testRunner=_MultiprocessTestRunner)

if __name__ == '__main__':
    main()
