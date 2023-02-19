from typing import Union
from dataclasses import dataclass


# ===============
# TYPE ALIASES
# ===============

DimensionsTuple = tuple[int, int]


# ===============
# DATA CLASSES
# ===============

@dataclass
class Dimensions:
    width: int
    height: int


class WindowOptions:
    # Default constants
    DEFAULT_DIMENSIONS = Dimensions(width=800, height=600)
    DEFAULT_PADDING = 16
    DEFAULT_FULLSCREEN = False
    DEFAULT_TITLE = ""

    def __init__(self, dimensions: Union[Dimensions, None] = None,
                 padding: Union[int, None] = None,
                 fullscreen: Union[bool, None] = None,
                 title: Union[str, None] = None) -> None:
        """
        Constructor for window options.

        Args:
            dimensions (Dimensions): window dimensions
            padding (int): padding between the game content and window edges
            fullscreen (bool): whether to present the window in fullscreen mode
            title (str): window title
        """

        # Default initialization values
        self._dimensions = WindowOptions.DEFAULT_DIMENSIONS
        self._padding = self.DEFAULT_PADDING
        self._fullscreen = self.DEFAULT_FULLSCREEN
        self._title = self.DEFAULT_TITLE

        # Attempt set custom values
        if dimensions is not None:
            self.set_dimensions(dimensions)
        if padding is not None:
            self.set_padding(padding)
        if fullscreen is not None:
            self.set_fullscreen(fullscreen)
        if title is not None:
            self.set_title(title)

    def set_dimensions(self, new_dimensions: Dimensions) -> None:
        """
        Setter method for updating the window dimensions.

        Args:
            new_dimensions (Dimensions): the new window dimensions

        Raises:
            ValueError if invalid dimensions are provided.
        """

        # Make sure screen dimensions are positive and non-zero
        if new_dimensions.width <= 0 or new_dimensions.height <= 0:
            raise ValueError(f"Argument new_dimensions {str(new_dimensions)} "
                             f"is invalid.")

        self._dimensions = new_dimensions

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
