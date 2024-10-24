import doctest

from src.nested_data_helper import navigation, pathfinder


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(navigation))
    tests.addTests(doctest.DocTestSuite(pathfinder))
    return tests
