import inspect
import os
import sys
from collections import namedtuple
from functools import partial

Result = namedtuple("Result", "result data case alt filename lineno")
SUCCESS, FAILURE, ERROR = "SUCCESS FAILURE ERROR".split()

CHARACTER = {
    SUCCESS: ".",
    FAILURE: "F",
    ERROR: "E"
}


def raises(f, e):
    """Check whether callable f raises exception e."""
    try:
        f()
    except e:
        return True
    except Exception as e:  # Any other exceptions are errors.
        return False
    return False


class RaisesFormattable(str):
    """
    A wrapper around strings with "{}" arguments to allow formatting with
    function names and exception types. Use RaisesFormattable("{} {}") as a
    drop-in replacement for "{} {}".
    """
    def format(self, function, exception):
        return super().format(
            function.__name__,
            exception.__name__
        )


def dots(result):
    """Draw a character onscreen depending on the result of a test."""
    sys.stdout.write(CHARACTER[result])
    sys.stdout.flush()


def print_errors(errors):
    """Pretty-print any errors encountered."""
    print()  # Add newline after character-results.
    if errors:
        print("\n({}) Error{}:".format(len(errors),
                                       "s" if len(errors) != 1 else ""))
        for e in errors:
            print("[{}:{}] In {}: {}".format(
                e.filename, e.lineno, e.case, e.data
            ))
        print()


def print_failures(failures):
    """Pretty-print any failures found."""
    if failures:
        print("\n({}) Failure{}:".format(len(failures),
                                         "s" if len(failures) != 1 else ""))
        for f in failures:
            print("[{}:{}] In {}: {}".format(
                f.filename, f.lineno, f.case, f.data),
                end='')
            print(" (\"{}\")".format(f.alt) if f.alt else "")
        print()

def print_overview(errors, failures):
    """Pretty-print a short summary of the results."""
    if len(errors) + len(failures) == 0:
        print("All tests passed!")
    else:
        print("Some tests failed ({} errors, {} failures)"
              "".format(len(errors), len(failures)))


def update_results(failures, errors, case_):
    """
    Given a case, look through its checks and update our lists of failures and
    errors accordingly. (If a check is successful, ignore it.)
    """
    for check in case_.checks:
        if check.result == FAILURE:
            failures.append(check)
        elif check.result == ERROR:
            errors.append(check)


class MetaCases:
    """
    MetaCases is a wrapper around a list of cases. It allows us to add some
    extra convenience functionality like coercion to bool (`if tests: ...`)
    and string representation, as well as a method to run all the tests and
    display their results.
    """

    def __init__(self):
        self.cases = []

    def __bool__(self):
        """Quick hack to allow `if tests:` functionality."""
        return "test" in sys.argv

    def run_all(self):
        """Run each test in the suite and display results accordingly."""
        failures, errors = [], []

        # Run each test case registered with us and agglomerate the results.
        for case_ in self.cases:
            case_.run()
            update_results(failures, errors, case_)

        # Display our results.
        print_errors(errors)
        print_failures(failures)
        print_overview(errors, failures)

        # Exit with 0 if all tests passed, >0 otherwise.
        sys.exit(len(failures) + len(errors))

    def __str__(self):
        """Return a string representation of this suite of test cases."""
        return str(self.cases)


# We need an instance of `MetaCases` to refer to in our `case` decorator.        
tests = MetaCases()


class Checker:
    """
    This is injected into every @case function. It provides methods to test the
    values and behaviours of objects.
    """
    import operator as op
    checks = {  # Todo: add more checks!
        "equal": (op.eq, "{} == {}", "{} != {}"),
        "not_equal": (op.ne, "{} != {}", "{} == {}"),
        "in": (lambda a, b: a in b, "{} in {}", "{} not in {}"),
        "contains": (op.contains, "{} contains {}", "{} does not contain {}"),
        "less_than": (op.lt, "{} < {}", "{} >= {}"),
        "less_than_equal_to": (op.le, "{} <= {}", "{} > {}"),
        "greater_than": (op.gt, "{} > {}", "{} <= {}"),
        "greater_than_equal_to": (op.ge, "{} >= {}", "{} < {}"),
        "callable": (callable, "{} is callable", "{} is not callable"),
        "true": (op.truth, "{} is true", "{} is not true"),
        "false": (lambda a: not a, "{} is not true", "{} is true"),
        "raises": (raises, RaisesFormattable("{} raised {}"),
                   RaisesFormattable("{} didn't raise {}"))
    }

    def __init__(self, case_):
        self.results = []
        self.case = case_

    def _base_check(self, func, on_true, on_false, *args, otherwise=""):
        """Template for a 'check'."""

        # Retrieve information about the line number and filename of the check.
        frame = inspect.currentframe().f_back
        lineno = frame.f_lineno
        filepath = frame.f_globals["__file__"]
        filename = os.path.basename(filepath)

        # Try and run the check. If we run into an exception, report it.
        try:
            if func(*args):
                result, data = SUCCESS, on_true.format(*args)
            else:
                result, data = FAILURE, on_false.format(*args)
        except Exception as e:
            result, data = ERROR, str(e)

        # Display and record our results.
        dots(result)
        self.results.append(
            Result(result=result, data=data, case=self.case, alt=otherwise,
                   filename=filename, lineno=lineno)
        )

    def __getattr__(self, item):
        """
        Override getattr to provide dynamic lookups for check_* methods.
        This is preferable to repeating code for each check_* method.
        """
        # Early-exit for properties other than check_-methods.
        if not item.startswith("check_"):
            return super().__getattribute__(self, item)

        # Lookup the appropriate method. If not found, complain.
        name = item.replace("check_", "")
        try:
            func, on_true, on_false = self.checks[name]
        except KeyError:
            raise NotImplementedError("No check for '{}'.".format(name))
        else:
            return partial(self._base_check, func, on_true, on_false)


class case:
    """
    A test case is a 'block' of checks. The way to create a test case is to
    write a function which accepts a parameter `t`, and make calls to methods
    like `t.check_equal(a, b)`. Then you decorate the function with `@case`,
    and the rest is done under the hood.
    """

    def __init__(self, f):
        self.f = f
        self.name = self.f.__name__
        self.results = []
        self.checks = []
        tests.cases.append(self)

    def run(self):
        """
        Run our test case. If we run into an exception, log it and move on.
        """
        checker = Checker(self.name)
        try:
            self.f(checker)
        except Exception as e:
            # Find line number and filename where the exception was thrown.
            _, _, traceback = sys.exc_info()
            traceback = traceback.tb_next
            lineno = traceback.tb_lineno
            filepath = traceback.tb_frame.f_code.co_filename
            filename = os.path.basename(filepath)

            # We can't continue, so return a single result with this error.
            self.checks = [Result(ERROR, e, self.name, "", filename, lineno)]
            dots(ERROR)
        else:
            self.checks = checker.results

    def __repr__(self):
        return self.name
