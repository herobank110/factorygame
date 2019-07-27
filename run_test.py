"""
Run start for FactoryGame test suite.
"""

## Whether to run GUI tests.
RUN_GUI_TESTS = 1


def main():
    if RUN_GUI_TESTS:
        # Run test for tkutils.
        from test.core.utils.tkutils_test import *

if __name__ == "__main__":
    main()
