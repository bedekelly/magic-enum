# Make a couple of Enums to play around with.

from magic_enum import Enum
from minitools.test import tests, case


class Colour(Enum):
    red,
    blue,
    yellow


class TrafficLight(Enum):
    red,
    yellow,
    green


@case
def test_equality(t):
    """
    Enum Constants should be equal like you'd expect.
    """
    red = Colour.red
    red2 = Colour.red
    blue = Colour.blue
    t.check_equal(red, red2)
    t.check_not_equal(red, blue)


@case
def test_individuality(t):
    """
    Enum Constants from different Enums shouldn't overlap, despite
    having the same member names.
    """
    colour_red = Colour.red
    light_red = TrafficLight.red
    t.check_not_equal(colour_red, light_red)


@case
def test_iteration(t):
    """
    Iterating over an Enum should yield all its members.
    """
    seen = set()
    for c in Colour:
        seen.add(c)
    t.check_equal(len(seen), 3)
    t.check_equal({Colour.red, Colour.blue, Colour.yellow}, seen)


@case
def test_iteration_order(t):
    """
    Iterating over an enum should yield all its members, *in order*.
    """
    seen = []
    for c in Colour:
        seen.append(c)
    t.check_equal(seen, [Colour.red, Colour.blue, Colour.yellow])


@case
def test_string(t):
    """
    An Enum Constant should have a pretty-printed string representation.
    This should also be its repr, since it's how you'd create a new one!
    """
    t.check_equal(str(Colour.red), "Colour.red")
    t.check_equal(repr(Colour.red), "Colour.red")


@case
def test_attribute_error(t):
    """
    Looking up a non-existent Enum Constant should raise an AttributeError.
    """
    t.check_raises(lambda: Colour.green, AttributeError)


@case
def test_attribute_setting(t):
    """
    Trying to set one of the Enum Constant fields should raise an exception.
    """
    def try_setting_attribute(): Colour.green = "Hello, world!"
    t.check_raises(try_setting_attribute, AttributeError)


tests.run_all()
