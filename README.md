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

Involving some arcane magic under the hood:
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



And more tests can be found in [testing.py](https://github.com/bedekelly/magic-enum/blob/master/testing.py). Enjoy!
