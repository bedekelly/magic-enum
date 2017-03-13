#Magic Enum

####Magic Enum is a better Enum for Python.

An Enum can be initialized like either of these:

```python
class TrafficLight(Enum):
    red
    amber
    green
    
class Colour(Enum):
    red, blue, green, yellow
```

Enum constants have all the goodies you'd expect from a regular enum:

```python
>>> Colour.red == Colour.blue
False

>> Colour.red == Colour.red
True
```

But they've also got some tricks up their sleeves:

```python
>>> for c in Colour:
...     print(c)
... 
Colour.red
Colour.blue
Colour.green
Colour.yellow
```

Like this one, inspired by the C++ enum's increment overloading:
```python
>>> next(TrafficLight.red)
TrafficLight.amber
```


They've got a type that makes sense:

```python
>>> type(Colour.blue) == Colour
True
>>> type(Colour.blue)
<class 'Colour' at 0x7fe78a8000e8>
```

And the type is meaningful, too:

```python
>>> Colour.red != TrafficLight.red
True
```

If you like, you can add values to the enum:

```python
class CarBrand(Enum):
    Ford = 1
    Toyota = 3
    Mitsubishi = 2


>>> for brand in CarBrand: print(brand)
CarBrand.Ford(value=1)
CarBrand.Mitsubishi(value=2)
CarBrand.Toyota(value=3)
```

Note that the results will be returned in order of their values!

(If the values aren't integers, we'll default to the order of insertion.)

In order to check if a value is one of multiple enum constants, use the built-in `in` operator:

```python
>>> col = Colour.red
>>> col in (Colour.blue, Colour.green, Colour.yellow)
False
>> col in (Colour.red, Colour.yellow)
True
```

It's also possible to use subscripting to get an enum constant, like so:

```python
>>> Colour["red"]
Colour.red
```

And more tests can be found in [testing.py](https://github.com/bedekelly/magic-enum/blob/master/testing.py). Enjoy!
