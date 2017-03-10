Minimock
=========

Minimock is a small and feature-light (tm) version of the ubiquitous Mock
library. It provides a single class, MiniMock, which is designed to mock the
functionality of any object. 

It contains some of the basic features of Mock, e.g. the `called_with` method
and `called` boolean attribute. It also dynamically spawns MiniMock instances
for its attributes (those that haven't been set manually, that is!).

To avoid confusion caused by typos, it borrows a feature from the Mock library:
it's possible to specify the 'spec' of the object we're mocking, and raise an
AttributeError when any non-existant attributes are requested.

 