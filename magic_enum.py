from itertools import filterfalse, count as itercount, chain as iterchain, cycle as itercycle
from collections import defaultdict
from operator import itemgetter
from functools import total_ordering


def is_special(name):
    """A name is special if it starts with an underscore."""
    return name.startswith("_")


@total_ordering
class EnumConstant:
    """
    An EnumConstant is, for example, something like Colour.RED.
    This class defines some basic properties for enum constants,
    like how they should compare equal to one another and how
    they should be next-able, hash-able, str-able etc.
    """
    def __init__(self, name, enum, value):
        self.name = name
        self.enum = enum
        self.value = value

    def __next__(self):
        """
        Overriding this method allows us to call next(SomeEnum.X) and
        get the next constant along (e.g. SomeEnum.Y).
        """
        # Iterate through our Enum, i.e. each Constant in order.
        next_enum_values = itercycle(type(self))

        # Enable ourselves to iterate in a two-item sliding window.
        enum_values = iterchain([None], next_enum_values)

        # If we're the current Constant, return the next one.
        for this, next_ in zip(enum_values, next_enum_values):
            if this == self:
                break

        # Or if we don't find the current Constant, something's VERY wrong.
        else:
            raise AttributeError("Something went badly wrong!")

        # Return the next one along in the series.
        return next_

    def __str__(self):
        return self.enum + "." + self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        """
        This is a shortcut, but it reliably gives the same result.
        When an enum constant is referenced, it invariably returns
        the reference to an item inside <enum>._members, so the ID
        is always the same. EnumConstants are, in effect, singletons.

        A more diligent, hardworking, and pointless implementation
        of this method would check if both the name and the enum
        were equal.
        """
        return id(self) == id(other)

    def __lt__(self, other):
        return self.value < other.value

    def __hash__(self):
        return hash(self.value)


class MetaEnum(type):

    @classmethod
    def __prepare__(mcs, name, bases):
        """
        Return a dictionary-like object which assigns a new integer
        to every successive enum constant. This is used for the
        initial class dictionary, where a bare "red" inside the class
        body of a "Colour" enum is treated as a dictionary lookup.
        """
        counter = itercount()
        return defaultdict(lambda: next(counter))

    def __new__(mcs, name, bases, classdict):
        """
        When it comes time to actually creating the class, convert
        our defaultdict into a regular dict -- this is so that we
        can raise a proper exception if a constant isn't found.

        This is also a good place to build up our own internal
        "classdict": instead of mapping the real values, we make
        a new enum of the given type and store it in a `_members`
        field on the enum class.
        """

        # Make sure we raise a proper exception if an element isn't found.
        classdict = dict(classdict)

        # Get an instance of the MetaEnum class, e.g. Colour or TrafficLight.
        enum_class = super().__new__(mcs, name, bases, classdict)

        # Get a list of the requested names for enum constants.
        non_special_names = filterfalse(is_special, classdict.keys())

        # Initialize a 'members' dictionary in the enum class, to register
        # each instance of that enum.
        enum_class._members = {}

        # Create an instance of the enum for each enum constant:
        for const_name in non_special_names:
            value = classdict[const_name]
            constant = enum_class(name=const_name, enum=name, value=value)

            # Register the instance we've created with the enum class.
            enum_class._members[const_name] = constant

        return enum_class

    def __iter__(self):
        """
        Make it possible to iterate through an Enum's values.
        """
        return iter(sorted(self._members.values()))

    def __setattr__(self, key, value):
        """
        Make sure that it's not possible to set an Enum's values
        after its initial creation.
        """
        # Note that here, "_members" is treated as special!
        if is_special(key):
            return super().__setattr__(key, value)
        raise AttributeError("Can't set attributes on an Enum!")

    def __getattribute__(self, attribute):
        """
        This method is called whenever an attribute of an Enum is
        requested. For example, if Colour.RED is referenced, this
        method will be called with the parameter "RED", and the
        return value of this method will be taken as its value.
        """

        # We probably don't want to interfere with any special attributes.
        if is_special(attribute):
            return super().__getattribute__(attribute)

        # Wrap any KeyErrors in our own (prettier) AttributeError.
        try:
            return self._members[attribute]
        except KeyError:
            enum_name = self.__name__
            msg = f"Enum constant not found: {enum_name}.{attribute}"
            raise AttributeError(msg) from None


class Enum(EnumConstant, metaclass=MetaEnum):
    """Tie the EnumConstant and MetaEnum types together!"""
    pass
