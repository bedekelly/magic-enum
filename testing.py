from magic_enum import Enum
from minitools.test import tests, case


class Colour(Enum):
    red,
    orange,
    yellow,
    green,
    blue,
    indigo,
    violet


class TrafficLight(Enum):
    red,
    amber,
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
    t.check_equal(len(seen), 7)
    t.check_equal(
        {
            Colour.red, Colour.blue, Colour.yellow, Colour.orange,
            Colour.indigo, Colour.violet, Colour.green
        },
        seen
    )


@case
def test_iteration_order(t):
    """
    Iterating over an enum should yield all its members, *in order*.
    """
    seen = []
    for c in Colour:
        seen.append(c)
    t.check_equal(seen, [
        Colour.red, Colour.orange, Colour.yellow,
        Colour.green, Colour.blue, Colour.indigo, Colour.violet
    ])


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
    t.check_raises(lambda: Colour.beige, AttributeError)


@case
def test_attribute_setting(t):
    """
    Trying to set one of the Enum Constant fields should raise an exception.
    """

    def try_setting_attribute(): Colour.green = "Hello, world!"

    t.check_raises(try_setting_attribute, AttributeError)


@case
def test_next(t):
    """
    Calling `next(c)` on an Enum constant should give the next one along.
    """
    t.check_equal(next(TrafficLight.red), TrafficLight.amber)


@case
def test_next_cycle(t):
    """
    Calling `next(c)` on the *last* Enum constant should give the first.
    """
    t.check_equal(next(TrafficLight.green), TrafficLight.red)


# Make an enum with orderable values.
class CarBrand(Enum):
    Ford = 1
    Toyota = 3
    Mitsubishi = 2


@case
def test_manual_value(t):
    """
    Setting values manually should allow them to be retrieved later.
    """
    t.check_equal(CarBrand.Mitsubishi.value, 2)


@case
def test_string_with_value(t):
    """
    If values are set manually, they should appear in the string repr.
    """
    t.check_equal(str(CarBrand.Toyota), "CarBrand.Toyota(value=3)")


@case
def test_order_of_orderable_values(t):
    """
    If values are order-able, they should appear in order.
    """
    seen = []
    for c in CarBrand:
        seen.append(c)
    t.check_equal(
        seen,
        [CarBrand.Ford, CarBrand.Mitsubishi, CarBrand.Toyota]
    )


# Make some unorderable classes for testing.
class Letter:
    def __repr__(self):
        return f"Letter('{self.__class__.__name__}')"


class A(Letter): pass
class B(Letter): pass
class C(Letter): pass


class Letters(Enum):
    a = A()
    b = B()
    c = C()


@case
def test_order_of_unorderable_values(t):
    """
    If values are unorderable, they should appear in order of addition.
    """
    seen = []
    for l in Letters:
        seen.append(l)
    t.check_equal(seen, [
        Letters.a, Letters.b, Letters.c
    ])


@case
def test_repr_of_value(t):
    """
    If an enum's value is repr-able, it should display properly.
    """
    t.check_equal(str(Letters.a), "Letters.a(value=Letter('A'))")


@case
def test_in_operator(t):
    """
    To check if an enum constant is in a set of values, use the
    built-in `in` operator.
    """
    col = Colour.red
    t.check_false(col in (Colour.blue, Colour.green, Colour.yellow))
    t.check_true(col in (Colour.red, Colour.yellow))


@case
def test_comma_assignment(t):
    """
    Try using the comma-separated syntax with assignments.
    """
    class Instruments(Enum):
        Keyboard = "<keyboard>",
        Guitar = "<guitar>",
        Drums = "<drums>"

    t.check_equal(
        Instruments.Keyboard.value,
        "<keyboard>"
    )


@case
def test_indexing(t):
    """
    Indexing into an Enum class should give a constant.
    """
    colour = Colour["red"]
    t.check_equal(colour, Colour.red)


@case
def test_indexing_nonexistent(t):
    """
    Indexing into an Enum class with a nonexistent constant
    name should give an AttributeError.
    """
    t.check_raises(
        lambda: Colour["beige"],
        AttributeError
    )


tests.run_all()
