from itertools import (
    filterfalse, count as itercount, chain as iterchain,
    cycle as itercycle, tee as itertee
)
from collections import defaultdict, namedtuple, OrderedDict
from operator import itemgetter
from functools import total_ordering
import inspect  # Oh no...


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
    def __init__(self, name, enum, value, implicit_value):
        self.name = name
        self.enum_name = enum
        self.value = value
        self.implicit = value is None
        self.implicit_value = implicit_value

    def __or__(self, other):
        return EnumConstantDisjunction(other, self)

    def __next__(self):
        """
        Overriding this method allows us to call next(SomeEnum.X) and
        get the next constant along (e.g. SomeEnum.Y).
        """
        # Iterate through our Enum, i.e. each Constant in order.
        enum_values = itercycle(type(self))
        this_values, next_values = itertee(enum_values, 2)

        # Enable ourselves to iterate in a two-item sliding window.
        this_values = iterchain([None], iter(this_values))

        # If we're the current Constant, return the next one.
        for this, next_ in zip(this_values, next_values):
            if this == self:
                break

        # Or if we don't find the current Constant, something's VERY wrong.
        else:
            raise AttributeError("Something went badly wrong!")

        # Return the next one along in the series.
        return next_

    def __str__(self):
        """
        The string representation of an EnumConstant should include
        the value, but only if that value has been manually set --
        not if it's been generated implicitly.
        """
        display = f"{self.enum_name}.{self.name}"
        if not self.implicit:
            display += f"(value={repr(self.value)})"
        return display

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
        """
        If integer values are provided, order results by those.
        Otherwise, use the order in which the constants are defined.
        """
        if isinstance(self.value, int):
            return self.value < other.value
        return self.implicit_value < other.implicit_value

    def __hash__(self):
        return hash(self.value)


NameValue = namedtuple("NameValue", "name value implicit_value")


class EnumDefaultNamespace:
    """
    This is an alternative to defaultdict, which allocates an implicit
    ordering value to each referenced value -- whether it's been added
    manually or just referenced implicitly.

    We use an instance of this class for the namespace of our Enum,
    before the values are finalized.
    """

    def __init__(self, sequence):
        self.namespace = {}
        self.sequence = sequence

    def __setitem__(self, key, value):
        """
        Be careful with this! This method is called when we're setting
        values for the enum constants, but it's also called by Python
        internals for special methods.

        Luckily we can mitigate any nasty side-effects by just checking
        if the name being assigned is "special" (i.e. potentially a
        Python internal).
        """
        if is_special(key):
            self.namespace[key] = value

        # Assume here that we're setting a default value.
        else:
            # This was a nasty bug: make the assumption that if the value
            # provided is a tuple with a single element, it's probably just
            # someone ending each line with a comma.
            if isinstance(value, tuple) and len(value) == 1:
                value = value[0]

            # Wrap our name and value in a NameValue instance and attach
            # the next element from our generator.
            self.namespace[key] = NameValue(key, value, next(self.sequence))

    def __getitem__(self, key):
        """
        We can make a pretty safe assumption that if we're looking up
        a value in this namespace, what we're *actually* doing is
        defining constants inside an Enum class.
        """

        # Todo: investigate whether there's an assignment!

        # Scary stuff: pop back a couple of stack frames so we can see
        # where the enum values are being defined.
        frame = inspect.currentframe()
        frame = frame.f_back.f_back

        # Assumption: if we're trying to lookup a value, and that value
        # appears in the locals or the globals of the frame in which the
        # enum constant is being defined, we're explicitly assigning a
        # value to an enum constant. If, however, it doesn't appear, we
        # want to define a new enum constant.
        if key in frame.f_locals:
            return frame.f_locals[key]
        if key in frame.f_globals:
            return frame.f_globals[key]

        # We can't find the name, so we'll define a new enum constant.
        name_value = NameValue(key, None, next(self.sequence))
        self.namespace[key] = name_value
        return name_value


class MetaEnum(type):
    """
    The MetaEnum class does a lot of the scary meta-stuff around
    patching the default namespace of the Enum class, making sure
    the Enum classes are iterable etc.
    """

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
        classdict = classdict.namespace

        # Get an instance of the MetaEnum class, e.g. Colour or TrafficLight.
        EnumClass = super().__new__(mcs, name, bases, classdict)

        # Get a list of the requested names for enum constants.
        non_special_names = filterfalse(is_special, classdict.keys())

        # Initialize a 'members' dictionary in the enum class, to register
        # each instance of that enum.
        EnumClass._members = {}

        # Create an instance of the enum for each enum constant:
        for const_name in non_special_names:
            const_name, value, implicit_value = classdict[const_name]

            # Create an instance of the Enum.
            constant = EnumClass(
                name=const_name, enum=name, value=value,
                implicit_value=implicit_value
            )

            # Register the instance we've created with the enum class.
            EnumClass._members[const_name] = constant

        return EnumClass

    def __prepare__(self, bases, **kwargs):
        """
        Return a dictionary-like object which assigns a new integer
        to every successive enum constant. This is used for the
        initial class dictionary, where a bare "red" inside the class
        body of a "Colour" enum is treated as a dictionary lookup.

        N.B. for future use: although PyCharm complains if the first
        parameter isn't called "self", it should really be called
        "name", as it's the name of the class we're creating a
        namespace for.
        """
        counter = itercount()
        return EnumDefaultNamespace(counter)

    def __iter__(self):
        """
        Make it possible to iterate through an Enum's values.
        """
        return iter(sorted(self._members.values()))

    def __getitem__(self, value):
        """
        Subscripting an Enum class should have the same effect
        as a dot-syntax lookup.
        """
        return getattr(self, value)

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
