"""
© Kevin Gugelmann, 20 February 2023.
All rights reserved.

This file contains enums and data classes used to calculate a PyGame relative
rectangle.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union


# ===============
# ENUMS
# ===============


class RelPos(Enum):
    """
    Enumeration for positioning of an element relative to its parent or itself.

    In the vertical axis:
        START: top
        CENTER: y-center
        END: bottom

    In the horizontal axis:
        START: left
        CENTER: x-center
        END: right
    """
    START = 0
    CENTER = 1
    END = 2


# ===============
# DATA CLASSES
# ===============


@dataclass
class ScreenPos:
    """
    Data class representing an element's position relative to the screen's
    dimensions.
    """
    x_pos: RelPos = RelPos.START
    y_pos: RelPos = RelPos.START


@dataclass
class ElemPos:
    """
    Data class representing an element's position relative to another element.
    """
    elem_id: str
    x_pos: RelPos = RelPos.END
    y_pos: RelPos = RelPos.END


@dataclass
class SelfAlign:
    """
    Data class representing an element's alignment in relation to its calculated
    position.

    In the vertical axis:
        START: above the reference point
        CENTER: centered with the reference point
        END: below the reference point

    In the horizontal axis:
        START: left of the reference point
        CENTER: center of the reference point
        END: right of the reference point
    """
    x_pos: RelPos = RelPos.START
    y_pos: RelPos = RelPos.START


@dataclass
class Fraction:
    """
    Data class representing a fractional value between [0,1].
    """
    value: float

    def __post_init__(self) -> None:
        """
        Check that arguments are all valid. Called by the dataclass initializer
        after instantiation.

        Raises:
            ValueError if value is out of bounds [0,1].
        """
        if self.value < 0 or self.value > 1:
            raise ValueError("Fraction value is out of bounds.")

    def __add__(self, other: object) -> "Fraction":
        """
        Dunder method to add two fractions.

        Args:
            other (object): the object to be added to

        Returns:
            Fraction: the computed fraction

        Raises:
            ValueError if other is not a Fraction.
            ValueError if computed Fraction is out of bounds [0,1].
        """
        if not isinstance(other, Fraction):
            raise ValueError("Can only add two Fractions.")

        return Fraction(self.value + other.value)

    def __sub__(self, other: object) -> "Fraction":
        """
        Dunder method to subtract two fractions.

        Args:
            other (object): the object to subtract

        Returns:
            Fraction: the computed fraction

        Raises:
            ValueError if other is not a Fraction.
            ValueError if computed Fraction is out of bounds [0,1].
        """
        if not isinstance(other, Fraction):
            raise ValueError("Can only subtract two Fractions.")

        return Fraction(self.value - other.value)

    def __truediv__(self, other: object) -> "Fraction":
        """
        Dunder method to divide this fraction by a number.

        Args:
            other (object): the divisor

        Returns:
            Fraction: the computed fraction

        Raises:
            ValueError if other is not a number.
            ValueError if computed Fraction is out of bounds [0,1].
        """
        if not isinstance(other, (int, float)):
            raise ValueError("Can only divide a Fraction by a number.")

        return Fraction(self.value / other)

    def __mul__(self, other: object) -> "Fraction":
        """
        Dunder method to multipy this fraction by a number (int, float).

        Args:
            other (object): the number to be multiplied by

        Returns:
            Fraction: the computed fraction

        Raises:
            ValueError if other is not a number.
            ValueError if computed Fraction is out of bounds [0,1].
        """
        if not isinstance(other, (int, float)):
            raise ValueError("Can only multiply a Fraction by a number.")

        return Fraction(self.value * other)


@dataclass
class NegFraction(Fraction):
    """
    Data class representing a negative fractional value between [-1,0].

    Takes a value between [0,1], where positive values represent their negative
    counterpart.
    """


@dataclass
class Offset:
    """
    Data class representing an element's offset from its calculated relative
    position.
    """
    x: Union[int, Fraction, NegFraction] = 0
    y: Union[int, Fraction, NegFraction] = 0


class IntrinsicSize:
    """
    Empty-constructor class to represent the intrinsic size of a dynamically
    sized PyGame-GUI element.
    """


class MatchOtherSide:
    """
    Empty-constructor class to represent the other side's length, which must not
    also be defined as `MatchOtherSide()`.
    """
