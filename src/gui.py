from typing import Union

import pygame
from pygame_gui import UIManager, PackageResource

from utils.window import *


class GuiApp:
    DEFAULT_WINDOW_OPTIONS = WindowOptions()

    def __init__(self,
                 window_options: WindowOptions = WindowOptions()) -> None:
        """
        Constructor for the GUI app.

        Args:
            window_options (WindowOptions): options for window presentation

        # TODO: initialize components
        """

        # Initialize PyGame
        pygame.init()
        self._is_running = True

        # Window setup
        self._set_window_options(window_options)
        self._bg_surface = None
        self._ui_manager = UIManager(self._get_window_dimensions_tuple(),
                                     PackageResource(package="data.themes",
                                                     resource="theme_1.json"))

        raise NotImplementedError()

    def _set_window_options(self, new_options: WindowOptions) -> None:
        """
        Setter method for the app's window options.

        Args:
            new_options (WindowOptions): the new window options
        """

        # Window title
        pygame.display.set_caption(new_options.get_title())

        # Window dimensions
        if new_options.is_fullscreen():
            self._window_surface = pygame.display.set_mode(
                new_options.get_dimensions_tuple(),
                pygame.FULLSCREEN)
        else:
            self._window_surface = pygame.display.set_mode(
                new_options.get_dimensions_tuple())

        # Store window options
        self._window_options = new_options

    def _get_window_options(self) -> WindowOptions:
        """
        Getter method for the app's window options.

        Returns:
            WindowOptions: the app's window options
        """
        return self._window_options

    def _get_window_dimensions(self) -> Dimensions:
        """
        Getter method for the app's window dimensions.

        Returns:
            Dimensions: the app's window dimensions
        """
        return self._get_window_options().get_dimensions()

    def _get_window_dimensions_tuple(self) -> DimensionsTuple:
        """
        Getter method for the app's window dimensions, as a tuple of ints.

        Returns:
            DimensionsTuple: the app's window dimensions
        """
        return self._get_window_options().get_dimensions_tuple()

    def run(self) -> None:
        """
        Start the app in a GUI window.
        """
        while self._is_running:
            # ...

            pygame.display.update()

        raise NotImplementedError()


app = GuiApp()
app.run()
