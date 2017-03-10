#Magic Enum

####Magic Enum is a better Enum for Python.

An Enum can be initialized like either of these:

```
class TrafficLight(Enum):
    red
    amber
    green
    
class Colour(Enum):
    red, blue, yellow
```

Enum constants have all the goodies you'd expect from a regular enum:

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

Involving some arcane magic under the hood:
```
>>> next(TrafficLight.red)
TrafficLight.amber
```


They've got a type that makes sense:

```
>>> type(Colour.blue) == Colour
True
>>> type(Colour.blue)
<class 'Colour' at 0x7fe78a8000e8>
```



And more tests can be found in `testing.py`. Enjoy!