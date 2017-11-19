#! /usr/bin/env python

import os
import unittest
import argparse
import importlib


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        'specs', nargs='*',
        help='<path-to-test-file>[:<class.method>|<class>|<method>]. '
             'We use file name here because it is more convenient to type '
             'in command line using auto-completion. This file name will '
             'be stupidly converted into module name by replacing slashes '
             'with dots and removing ".py" extension.')
    args, flags = p.parse_known_args()

    tests = []

    for spec in args.specs:
        testfile, has_testname, testname = spec.partition(':')

        if not os.path.isfile(testfile):
            p.error("File not found: "+testfile)
            return
        if testfile.endswith('.py'):
            testfile = testfile[:-3]
        if testfile.endswith(os.sep+'__init__'):
            testfile = testfile[:-len(os.sep+'__init__')]
        test = testfile.replace(os.sep, '.')

        if has_testname:
            if '.' in testname:
                test += '.' + testname
            else:
                module = importlib.import_module(test)
                if hasattr(module, testname):
                    test += '.'+testname
                else:
                    for cls_name in dir(module):
                        test_cls = getattr(module, cls_name)
                        if isinstance(test_cls, type) \
                                and issubclass(test_cls, unittest.TestCase) \
                                and not getattr(test_cls, '__abstract_test__', False):
                            if hasattr(test_cls, testname):
                                test += '.{}.{}'.format(cls_name, testname)
                                break
                    else:
                        p.error('Test "{}" not found'.format(testname))
                        return
        tests.append(test)

    argv = [''] + flags
    if tests:
        argv += tests
    else:
        argv += ['discover', '-s', 'test_tensorlab', '-t', '.']
    unittest.main(argv=argv, module=None)


if __name__ == '__main__':
    main()
