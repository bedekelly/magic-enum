#Magic Enum

Magic Enum is a better Enum for Python.

```python
class Colour(Enum):
    red,
    blue,
    green,
    yellow
```

Magic Enum constants have all the goodies you'd expect from a regular enum:

```
>>> Colour.red == Colour.blue
False

>> Colour.red == Colour.red
True
```

But they've also got some tricks up their sleeves:

```
>>> for c in Colour:
...     print(c)
... 
Colour.red
Colour.blue
Colour.green
Colour.yellow
```

They've got a type that makes sense:

```
>>> type(Colour.blue) == Colour
True
>>> type(Colour.blue)
<class 'Colour' at 0x7fe78a8000e8>
```

By convention, they're initialised like this (commas optional!):

```
class TrafficLight(Enum):
    red,
    amber,
    green
```

Comprehensive tests can be found in `testing.py`.