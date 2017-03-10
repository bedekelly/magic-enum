MiniTest
=========

##An extremely lightweight test framework for Python.

####Rationale:

Use this for adding tests to small scripts in Python. If you're testing a big project, use a more full-featured library like unittest or nose!

This was designed to be lightweight and unobtrusive, so there's a lot of magic under the hood enabling the various syntax hacks (e.g. the `if tests:` functionality and dynamic `check_X` lookups).

This library doesn't show the entire traceback for errors it catches; it just shows the exception text on a single line. This is based on my own experience with reading test output: I usually don't look at the traceback for long before just going to the file/line-number (both visible in minitest output) and setting a breakpoint to debug what's going on.

####Usage:

```python
from minitest import case, tests

@case
def test_something(t):
    t.check_equal(1, 2)

if tests:
    tests.run_all()
```

Running this script with `python script.py test` will run every test case marked by the `@case` decorator.

If `test` is not provided as an argument, the `tests.run_all()` command will not be executed, and the script will run without executing the tests.

Running `python script.py test` will yield this output:

```
F

(1) Failure:
[script.py:5] In test_something: 1 != 2
```

For a richer example, the output of `python use.py test` is the following:

```
..FFEEEEE.EF.F.

(6) Errors:
[use.py:31] In cause_internal_error: Exception inside a check.
[use.py:32] In cause_internal_error: Exception inside a check.
[use.py:38] In cause_external_error: Exception outside a check.
[use.py:44] In non_existent_check: No check for 'asdf'.
[use.py:50] In wrong_args: op_eq expected 2 arguments, got 3
[use.py:62] In try_calling: 'Checker' object is not callable


(4) Failures:
[use.py:19] In incorrect_value: 4 != 3
[use.py:20] In incorrect_value: 7 != 1
[use.py:68] In provide_alternative: 1 != 2 ("Don't be silly, 1 isn't 2!")
[use.py:78] In raises: myfunction didn't raise AttributeError
```

Please see use.py for the code responsible for this test output.
