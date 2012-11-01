# coding: utf-8
# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module defines the `Quantity` object, which represents a number with some associated
units. `Quantity` objects support operations like ordinary numbers, but will deal with
unit conversions internally.
"""

from __future__ import absolute_import, unicode_literals, division, print_function

# Standard library
import copy
import numbers

# AstroPy
from .core import Unit

__all__ = ["Quantity"]

def _validate_value(value):
    """ Make sure that the input is a Python numeric type.

    Parameters
    ----------
    value : number
        An object that will be checked whether it is a numeric type or not.
    """

    if isinstance(value, numbers.Number):
        value_obj = value
    else:
        raise TypeError("The value must be a valid Python numeric type.")

    return value_obj

class Quantity(object):
    """ A `Quantity` represents a number with some associated unit.

    Parameters
    ----------
    value : number
        The numerical value of this quantity in the units given by unit.
    unit : `~astropy.units.UnitBase` instance, str
        An object that represents the unit associated with the input value. Must be an `~astropy.units.UnitBase`
        object or a string parseable by the `units` package.

    Raises
    ------
    TypeError
        If the value provided is not a Python numeric type.
    TypeError
        If the unit provided is not either a `Unit` object or a parseable string unit.
    """

    def __init__(self, value, unit):
        self._value = _validate_value(value)
        self._unit = Unit(unit)

    def to(self, unit):
        """ Returns a new `Quantity` object with the specified units.

        Parameters
        ----------
        unit : `~astropy.units.UnitBase` instance, str
            An object that represents the unit to convert to. Must be an `~astropy.units.UnitBase`
            object or a string parseable by the `units` package.
        """
        new_val = self.unit.to(unit, self.value)
        new_unit = Unit(unit)
        return Quantity(new_val, new_unit)

    @property
    def value(self):
        """ The numerical value of this quantity. """
        return self._value

    @value.setter
    def value(self, obj):
        """ Setter for the value attribute. We allow the user to change the value by setting this attribute,
        so this will validate the new object.

        Parameters
        ----------
        obj : number
            The numerical value of this quantity in the same units as stored internally.

        Raises
        ------
        TypeError
            If the value provided is not a Python numeric type.
        """
        self._value = _validate_value(obj)

    @property
    def unit(self):
        """ A `~astropy.units.UnitBase` object representing the unit of this quantity. """
        return self._unit

    def copy(self):
        """ Return a copy of this `Quantity` instance """
        return Quantity(self.value, unit=self.unit)

    # Arithmetic operations
    def __add__(self, other):
        """ Addition between `Quantity` objects. All operations return a new `Quantity` object
        with the units of the **left** object.
        """
        if not isinstance(other, Quantity):
            raise TypeError("Object of type '{0}' cannot be added with a Quantity object. Addition is only supported between Quantity objects.".format(other.__class__))
        return Quantity(self.value + other.to(self.unit).value, unit=self.unit)

    def __sub__(self, other):
        """ Subtraction between `Quantity` objects. All operations return a new `Quantity` object
        with the units of the **left** object.
        """
        if not isinstance(other, Quantity):
            raise TypeError("Object of type '{0}' cannot be subtracted with a Quantity object. Subtraction is only supported between Quantity objects.".format(other.__class__))
        return Quantity(self.value - other.to(self.unit).value, unit=self.unit)

    def __mul__(self, other):
        """ Multiplication between `Quantity` objects or numbers with `Quantity` objects. For operations between two `Quantity` instances,
        returns a new `Quantity` object with the units of the **left** object.
        """
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, unit=self.unit*other.unit)

        elif isinstance(other, numbers.Number):
            return Quantity(other*self.value, unit=self.unit)

        else:
            raise TypeError("Object of type '{0}' cannot be multiplied with a Quantity object.".format(other.__class__))


    def __rmul__(self, other):
        """ Right multiplication between `Quantity` object and a number. """

        if isinstance(other, numbers.Number):
            return Quantity(other*self.value, unit=self.unit)

        else:
            raise TypeError("Object of type '{0}' cannot be multiplied with a Quantity object.".format(other.__class__))

    def __div__(self, other):
        """ Division between `Quantity` objects. This operation returns a dimensionless object. """
        if isinstance(other, Quantity):
            return Quantity(self.value / other.value, unit=self.unit/other.unit)

        elif isinstance(other, numbers.Number):
            return Quantity(self.value / other, unit=self.unit)

        else:
            raise TypeError("Object of type '{0}' cannot be divided with a Quantity object.".format(other.__class__))

    def __rdiv__(self, other):
        """ Division between `Quantity` objects. This operation returns a dimensionless object. """
        if isinstance(other, numbers.Number):
            print(Unit("1/{}".format(self.unit.to_string())))
            return Quantity(other / self.value, unit=Unit("1/{}".format(self.unit.to_string())))

        else:
            raise TypeError("Object of type '{0}' cannot be divided with a Quantity object.".format(other.__class__))


    def __truediv__(self, other):
        """ Division between `Quantity` objects. This operation returns a dimensionless object. """
        return self.__div__(other)

    def __rtruediv__(self, other):
        """ Division between `Quantity` objects. This operation returns a dimensionless object. """
        return self.__rdiv__(other)

    def __pow__(self, p):
        """ Raise quantity object to a power. """
        return Quantity(self.value**p, unit=(self.unit**p).simplify())

    # Comparison operations
    def __eq__(self, other):
        return self.value == other.to(self.unit).value

    def __ne__(self, other):
        return self.value != other.to(self.unit).value

    def __lt__(self, other):
        return self.value < other.to(self.unit).value

    def __le__(self, other):
        return self.value <= other.to(self.unit).value

    def __gt__(self, other):
        return self.value > other.to(self.unit).value

    def __ge__(self, other):
        return self.value >= other.to(self.unit).value

    def __hash__(self):
        return hash(self.value) ^ hash(self.unit)

    # Display
    def __str__(self):
        return "{0} {1:s}".format(self.value, self.unit.to_string())

    def __repr__(self):
        return "<Quantity {0} {1:s}>".format(self.value, self.unit.to_string())

    def _repr_latex_(self):
        """
        Generate latex representation of unit name.  This is used by
        the IPython notebook to show it all latexified.

        Returns
        -------
        lstr
            LaTeX string
        """

        # Format value
        latex_value = "{0:g}".format(self.value)
        if "e" in latex_value:
            latex_value = latex_value.replace('e', '\\times 10^{') + '}'

        # Format unit
        # [1:-1] strips the '$' on either side needed for math mode
        latex_unit = self.unit._repr_latex_()[1:-1]  # note this is unicode

        return u'${0} \; {1}$'.format(latex_value, latex_unit)
