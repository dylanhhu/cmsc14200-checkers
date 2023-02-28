"""
© Kevin Gugelmann, 20 February 2023.
All rights reserved.

This file contains type aliases and classes for setting a GUI app's window
options, including: current and minimum dimensions, padding, title, and FPS.
"""

from typing import Union, Tuple
from dataclasses import dataclass


# ===============
# TYPE ALIASES
# ===============

DimensionsTuple = Tuple[int, int]


# ===============
# DATA CLASSES
# ===============


@dataclass
class Dimensions:
    """
    Data class representing window dimensions (width & height).
    """
    width: int
    height: int

    @staticmethod
    def from_tuple(dimensions_tuple: DimensionsTuple) -> "Dimensions":
        """
        Creates a Dimensions instance from a tuple of two ints.

        Args:
            dimensions_tuple (DimensionsTuple): dimensions tuple (width, height)

        Returns:
            Dimensions: the new Dimensions instance
        """
        return Dimensions(dimensions_tuple[0], dimensions_tuple[1])


# ===============
# WINDOW OPTIONS CLASS
# ===============


class WindowOptions:
    """
    Class containing options for configuring the PyGame window.
    """

    # Default constants
    DEFAULT_DIMENSIONS = Dimensions(width=800, height=600)
    DEFAULT_MIN_DIMENSIONS = Dimensions(width=400, height=300)
    DEFAULT_PADDING = 32
    DEFAULT_FULLSCREEN = False
    DEFAULT_TITLE = ""
    DEFAULT_FPS = 60

    def __init__(self,
                 dimensions: Union[Dimensions, None] = None,
                 min_dimensions: Union[Dimensions, None] = None,
                 padding: Union[int, None] = None,
                 fullscreen: Union[bool, None] = None,
                 title: Union[str, None] = None,
                 fps: Union[int, None] = None) -> None:
        """
        Constructor for window options.

        Args:
            dimensions (Dimensions): window dimensions
            min_dimensions (Dimensions): minimum window dimensions
            padding (int): padding between the game content and window edges
            fullscreen (bool): whether to present the window in fullscreen mode
            title (str): window title
        """

        # Default initialization values
        self._dimensions = WindowOptions.DEFAULT_DIMENSIONS
        self._min_dimensions = WindowOptions.DEFAULT_MIN_DIMENSIONS
        self._padding = self.DEFAULT_PADDING
        self._fullscreen = self.DEFAULT_FULLSCREEN
        self._title = self.DEFAULT_TITLE
        self._fps = self.DEFAULT_FPS

        # Attempt set custom values
        if dimensions is not None:
            self.set_dimensions(dimensions)
        if min_dimensions is not None:
            self.set_min_dimensions(min_dimensions)
        if padding is not None:
            self.set_padding(padding)
        if fullscreen is not None:
            self.set_fullscreen(fullscreen)
        if title is not None:
            self.set_title(title)
        if fps is not None:
            self.set_fps(fps)

    def set_dimensions(self, new_dimensions: Dimensions) -> None:
        """
        Setter method for updating the window dimensions.

        Limited to minimum window dimensions.

        Args:
            new_dimensions (Dimensions): the new window dimensions

        Raises:
            ValueError if invalid dimensions are provided.
        """

        # Make sure window dimensions are positive and non-zero
        if new_dimensions.width <= 0 or new_dimensions.height <= 0:
            raise ValueError(f"Argument new_dimensions {str(new_dimensions)} "
                             f"is invalid.")

        self._dimensions = Dimensions(
            max(self.get_min_dimensions().width, new_dimensions.width),
            max(self.get_min_dimensions().height, new_dimensions.height),
        )

    def get_dimensions(self) -> Dimensions:
        """
        Getter method that returns the window dimensions.

        Returns:
            Dimensions: window dimensions
        """
        return self._dimensions

    def get_dimensions_tuple(self) -> DimensionsTuple:
        """
        Getter method that returns the window dimensions, as a tuple of ints.

        Returns:
            DimensionsTuple: window dimensions (width, height)
        """
        return self._dimensions.width, self._dimensions.height

    def set_min_dimensions(self, new_dimensions: Dimensions) -> None:
        """
        Setter method for updating the minimum window dimensions.

        Args:
            new_dimensions (Dimensions): the new minimum window dimensions

        Raises:
            ValueError if invalid dimensions are provided.
        """

        # Make sure minimum window dimensions are positive and non-zero
        if new_dimensions.width <= 0 or new_dimensions.height <= 0:
            raise ValueError(f"Minimum dimensions {str(new_dimensions)} are "
                             f"invalid.")

        # Update minimum dimensions
        self._min_dimensions = new_dimensions

        # Make sure minimum window dimensions are smaller than the current
        # window dimensions, by recalling `set_dimensions`
        if new_dimensions.width > self.get_dimensions().width or \
                new_dimensions.height > self.get_dimensions().height:
            self.set_dimensions(self.get_dimensions())

    def get_min_dimensions(self) -> Dimensions:
        """
        Getter method that returns the minimum window dimensions.

        Returns:
            Dimensions: minimum window dimensions
        """
        return self._min_dimensions

    def get_min_dimensions_tuple(self) -> DimensionsTuple:
        """
        Getter method that returns the minimum window dimensions, as a tuple of
        ints.

        Returns:
            DimensionsTuple: minimum window dimensions (width, height)
        """
        return self._min_dimensions.width, self._min_dimensions.height

    def set_padding(self, new_padding: int) -> None:
        """
        Setter method for updating the padding between the game content and
        window edges.

        Args:
            new_padding (int): the new window padding

        Raises:
            ValueError if invalid padding is provided.
        """

        # Make sure padding is positive
        if new_padding < 0:
            raise ValueError(f"Argument new_padding {str(new_padding)} is "
                             f"invalid.")

        self._padding = new_padding

    def get_padding(self) -> int:
        """
        Getter method that returns the padding between the game content and
        window edges.

        Returns:
            int: window padding
        """
        return self._padding

    def set_fullscreen(self, is_fullscreen: bool) -> None:
        """
        Setter method for updating whether the window is presented in
        fullscreen mode.

        Args:
            is_fullscreen (bool): whether the window is fullscreen
        """
        self._fullscreen = is_fullscreen

    def is_fullscreen(self) -> bool:
        """
        Getter method that returns whether the window is presented in
        fullscreen mode.

        Returns:
            bool: whether the window is fullscreen
        """
        return self._fullscreen

    def set_title(self, new_title: str) -> None:
        """
        Setter method for the window title.

        Args:
            new_title (str): the new window title
        """
        self._title = new_title

    def get_title(self) -> str:
        """
        Getter method that returns the window title.

        Returns:
            str: window title
        """
        return self._title

    def set_fps(self, new_fps: int) -> None:
        """
        Setter method for window frame rate.

        Args:
            new_fps (fps): the new frame rate
        """
        self._fps = new_fps

    def get_fps(self) -> int:
        """
        Getter method that returns the window frame rate.

        Returns:
            int: window frame rate
        """
        return self._fps
