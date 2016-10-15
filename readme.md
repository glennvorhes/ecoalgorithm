# Ecoalgorithm

Provides a framework with with to do optimizations as they
occur in nature. A number of different species, each of which
inherits from a base class defined in the package.  

## More Documentation

Additional documentation and description of this project 
will be forthcoming.  

```python
# Class inherits from SpeciesBase
class MySpecies(SpeciesBase):
    
    # Constructor creates some random attributes
    # Must be serializable, strings, numbers, booleans ...
    def __init__(self, x=None, y=None, blue=None):
        self.x = x if type(x) is float else (random() - 0.5) * 200
        self.y = y if type(y) is float else (random() - 0.5) * 200
        self.blue = blue if type(blue) is bool else True if random() > 0.5 else False
        
        """
        The call the the super constructor is important
        Some background process occurs dependent on a check
        if the object has already been persisted to the database
        
        If so, the random values generated by the constructor 
        are replaced by those present in the database
        
        the call to the super constructor is important
        some background processing occurs dependent on if
        
        """
        
        super().__init__()
    
    
    def mature(self):
        self.success = -1 * (self.x - 15) ** 2 + -1 * (self.y + 4) ** 2 + 25

    def mutate(self):
        pass

    def mate(self, other_individual):
        if random() > 0.5:
            new_x = self.x + (random() - 0.5) * random_change
        else:
            new_x = other_individual.x + (random() - 0.5) * random_change
        if random() > 0.5:
            new_y = self.y + (random() - 0.5) * random_change
        else:
            new_y = other_individual.y + (random() - 0.5) * random_change

        return self.__class__(new_x, new_y)

```