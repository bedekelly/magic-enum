from minitest import case, tests


def add(a, b):
    """Add two numbers together and return the result."""
    return a + b


@case
def correct_value(t):
    """A case with two succeeding checks."""
    t.check_equal(add(1, 2), 3)
    t.check_not_equal(add(1, 2), 4)


@case
def incorrect_value(t):
    """A case with two failing checks."""
    t.check_equal(add(2, 2), 3)
    t.check_equal(add(2, 5), 1)


@case
def cause_internal_error(t):
    """A case with two checks which cause errors."""
    class ExceptionRaiser:
        def __eq__(self, other):
            raise Exception("Exception inside a check.")

    # An ExceptionRaiser will raise whenever it's compared to anything.
    t.check_equal(ExceptionRaiser(), 0)
    t.check_equal(ExceptionRaiser(), 1)


@case
def cause_external_error(_):
    """A case with an error outside any checks."""
    raise Exception("Exception outside a check.")


@case
def non_existent_check(t):
    """A case which tries to call a check that doesn't exist."""
    t.check_asdf()


@case
def wrong_args(t):
    """A case which tries to call a check with the wrong no. of arguments."""
    t.check_equal(1, 2, 3)


@case
def one_arg(t):
    """A case which calls a check with only one argument."""
    t.check_true(1)


@case
def try_calling(t):
    """A case which tries to call its checker. (Hint: this doesn't work!)"""
    t()


@case
def provide_alternative(t):
    """A case which provides 'alt-text' for its check."""
    t.check_equal(1, 2, otherwise="Don't be silly, 1 isn't 2!")


@case
def raises(t):
    """A case with three checks for whether something raises an exception."""
    def myfunction():
        raise ZeroDivisionError

    t.check_raises(myfunction, ZeroDivisionError)
    t.check_raises(myfunction, AttributeError)
    t.check_raises(myfunction, Exception)


if tests:
    tests.run_all()
