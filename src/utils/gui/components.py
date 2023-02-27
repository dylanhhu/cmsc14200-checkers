#
# © Kevin Gugelmann, 20 February 2023.
# All rights reserved.
#
from enum import Enum
from typing import Union, List, Dict
from dataclasses import dataclass

from pygame_gui.elements import (UIImage, UIButton, UIHorizontalSlider,
                                 UIVerticalScrollBar, UIHorizontalScrollBar,
                                 UILabel, UIPanel, UIProgressBar,
                                 UIScreenSpaceHealthBar, UISelectionList,
                                 UITextBox, UITextEntryLine, UITooltip,
                                 UIDropDownMenu, UIStatusBar,
                                 UIWorldSpaceHealthBar, UIWindow,
                                 UIScrollingContainer, UITextEntryBox)

# ===============
# TYPE ALIASES
# ===============

PyGameGUIElement = Union[UIImage, UIButton, UIHorizontalSlider,
                         UIVerticalScrollBar,
                         UIHorizontalScrollBar, UILabel, UIPanel, UIProgressBar,
                         UIScreenSpaceHealthBar, UISelectionList, UITextBox,
                         UITextEntryLine, UITooltip, UIDropDownMenu,
                         UIStatusBar, UIWorldSpaceHealthBar, UIWindow,
                         UIScrollingContainer, UITextEntryBox]
Element = Union[PyGameGUIElement]
ScreenId = str
ElementId = str


# ===============
# ENUMS
# ===============


class ModifyElemCommand(Enum):
    """
    An enumeration for the internal representation of element modification
    commands.
    """

    SHOW = "show"
    HIDE = "hide"
    ENABLE = "enable"
    DISABLE = "disable"


# ===============
# DATA CLASSES
# ===============


@dataclass
class _GuiComponent:
    elem_id: str
    elem: Union[Element, None]
    screen_id: str


# ===============
# GUI COMPONENT LIBRARY CLASS
# ===============


class GuiComponentLib:
    """
    GUI component library for keeping track of PyGame-GUI elements that are
    to be painted by PyGame.

    Each element is organized by its screen and referenced by its unique ID.

    1. Elements are initialized by screen via `init_elem` (individual elements)
        or `init_screen_elems` (multiple elements).
    2. Elements are drafted for painting via the `draft` method. To set the
        current screen, use `set_draft_screen`.
    3. Get or modify elements on the currently drafted screen by their unique
        ID.
    """

    def __init__(self) -> None:
        """
        Constructor for component library.
        """
        self._components_by_screen: Dict[ScreenId, List[_GuiComponent]] = {}
        self._unique_elem_ids: Dict[ScreenId, List[ElementId]] = {}
        self._draft_screen: Union[str, None] = None

    def init_elem(self, elem_id: str, screen_id: str) -> \
            None:
        """
        Initialize a new GUI element by its unique ID, and add it to the
        library. If element already in library - ignore.

        Required before drafting elements for painting.

        Args:
            elem_id (str): unique element identifier
            screen_id (str): screen to render the element on

        Raises:
            ValueError if invalid element ID is passed.
            ValueError if invalid screen ID is passed.
        """

        # Validate IDs
        if elem_id == "":
            raise ValueError("Argument elem_id should not be an empty string.")
        if screen_id == "":
            raise ValueError("Argument screen_id should not be an empty string"
                             ".")

        if elem_id in self._unique_elem_ids.get(screen_id, []):
            # Element already registered for screen - ignore
            return

        # Make note of unique element ID
        self._unique_elem_ids[screen_id] = \
            self._unique_elem_ids.get(screen_id, []) + [elem_id]

        # Add component to library
        self._components_by_screen[screen_id] = \
            self._components_by_screen.get(screen_id, []) + [
                _GuiComponent(elem_id, None, screen_id)
            ]

    def init_screen_elems(self,
                          screen_id: ScreenId,
                          elem_ids: List[ElementId]) -> None:
        """
        Initialize a list of GUI elements by their unique IDs, and then add
        them to the library.

        Args:
            screen_id (ScreenId): screen to render the elements on
            elem_ids (List[ElementId]): list of element ids

        Returns:
            None

        Raises:
            ValueError if invalid element ID is passed.
            ValueError if invalid screen ID is passed.
        """
        if screen_id not in self._components_by_screen:
            self._components_by_screen[screen_id] = []

        for elem_id in elem_ids:
            self.init_elem(elem_id, screen_id)

    def _get_component(self,
                       elem_id: ElementId,
                       screen_id: ScreenId) -> _GuiComponent:
        """
        Get a GUI component by screen and its unique element ID.

        Args:
            elem_id (ElementId): unique element ID
            screen_id (ScreenId): screen ID

        Raises:
            RuntimeError if screen ID doesn't exist.
            RuntimeError if element ID doesn't exist.

        Returns:
            _GuiComponent: the found GUI component
        """
        screen_components = self._components_by_screen.get(screen_id, None)

        if not screen_components:
            # Screen does not exist
            raise RuntimeError(f"Screen '{screen_id}' does not exist.")

        for component in screen_components:
            if component.elem_id == elem_id:
                # Found the component that corresponds to the element: success!
                return component

        # Element does not exist
        raise RuntimeError(
            f"Element '{elem_id}' does not exist in screen '{screen_id}'.")

    def get_elem(self, elem_id: ElementId) -> Union[Element, None]:
        """
        Get a GUI element by its unique element ID on the draft screen.

        Args:
            elem_id (ElementId): unique element ID

        Raises:
            RuntimeError if element ID doesn't exist.
            RuntimeError if element is not drafted.

        Returns:
            Union[Element, None]: the found GUI element
        """
        return self._get_component(elem_id, self._draft_screen).elem

    def get_elem_selection(self, elem_id: ElementId) -> str:
        """
        Get the selection of a dropdown element, finding it by its unique
        element ID on the draft screen.

        Args:
            elem_id (ElementId): unique element ID

        Raises:
            RuntimeError if element ID doesn't exist.

        Returns:
            str: dropdown selection value
        """
        if elem := self.get_elem(elem_id):
            return elem.selected_option

    def get_elem_text(self, elem_id: ElementId) -> str:
        """
        Get the text of a text-based element, finding it by its unique
        element ID on the draft screen.

        Args:
            elem_id (ElementId): unique element ID

        Raises:
            RuntimeError if element ID doesn't exist.

        Returns:
            str: text-based element string value
        """
        if elem := self.get_elem(elem_id):
            return elem.text

    def set_draft_screen(self, screen_id: ScreenId) -> None:
        """
        Setter method for the screen being drafted.

        Args:
            screen_id (ScreenId): screen ID

        Returns:
            None

        Raises:
            RuntimeError if screen ID doesn't exist.
        """
        self._draft_screen = screen_id

    def draft(self, new_elem: Element) -> None:
        """
        Draft a GUI element for painting. Must have an object ID.

        Requires that the draft screen is already set (via `set_draft_screen`).

        Args:
            new_elem (Element): the new element

        Returns:
            None

        Raises:
            ValueError if element doesn't have an Object ID.
            RuntimeError if draft screen is not set.
            RuntimeError if element ID doesn't exist.
        """
        if self._draft_screen is None:
            raise ValueError("Draft screen must first be set.")

        # Get unique element ID from Object ID
        if object_ids := new_elem.object_ids:
            elem_id = object_ids[0]
        else:
            raise ValueError("Element doesn't have an Object ID.")

        # Initialize element for draft screen
        self.init_elem(elem_id, self._draft_screen)

        # Set element for the relevant stored component
        self._get_component(elem_id, self._draft_screen).elem = new_elem

    def mod_elem(self,
                 elem_id: ElementId,
                 command: ModifyElemCommand) -> None:
        """
        Modify an element by one of four commands:
            - Show
            - Hide
            - Enable
            - Disable

        Args:
            elem_id (ElementId): unique element ID
            command (ModifyElemCommand): element modification command

        Returns:
            None

        Raises:
            RuntimeError if element ID doesn't exist.
            ValueError if command is invalid.
        """
        if elem := self.get_elem(elem_id):
            if command == ModifyElemCommand.SHOW:
                elem.show()
            elif command == ModifyElemCommand.HIDE:
                elem.hide()
            elif command == ModifyElemCommand.ENABLE:
                elem.enable()
            elif command == ModifyElemCommand.DISABLE:
                elem.disable()
            else:
                raise ValueError(f"Provided argument command '{command.value}'"
                                 f"is invalid.")

    def show_elem(self, elem_id: ElementId) -> None:
        """
        Show an element, given its unique ID. If the
        element is already visible - ignore.

        Args:
            elem_id (ElementId): unique element ID

        Returns:
            None

        Raises:
            RuntimeError if element ID doesn't exist.
        """
        if elem := self.get_elem(elem_id):
            elem.show()

    def hide_elem(self, elem_id: ElementId) -> None:
        """
        Hide an element, given its unique ID. If the
        element is already hidden - ignore.

        Args:
            elem_id (ElementId): unique element ID

        Returns:
            None

        Raises:
            RuntimeError if element ID doesn't exist.
        """
        if elem := self.get_elem(elem_id):
            elem.hide()

    def enable_elem(self, elem_id: ElementId) -> None:
        """
        Enable an element, given its unique ID. If the
        element is already enabled - ignore.

        Args:
            elem_id (ElementId): unique element ID

        Returns:
            None

        Raises:
            RuntimeError if element ID doesn't exist.
        """
        if elem := self.get_elem(elem_id):
            elem.enable()

    def disable_elem(self, elem_id: ElementId) -> None:
        """
        Disable an element, given its unique ID. If the
        element is already disabled - ignore.

        Args:
            elem_id (ElementId): unique element ID

        Returns:
            None

        Raises:
            RuntimeError if element ID doesn't exist.
        """
        if elem := self.get_elem(elem_id):
            elem.disable()

    @staticmethod
    def _clear_elem(component: _GuiComponent) -> None:
        """
        Clear the drafting of a GUI element, provided a GUI component.

        Args:
            component (_GuiComponent): component whose element to clear

        Returns:
            None
        """
        component.elem = None

    def _clear_screen(self, screen_id: ScreenId) -> None:
        """
        Clear the drafting of all GUI elements in a provided screen.

        Args:
            screen_id (ScreenId): screen ID

        Returns:
            None
        """
        for component in self._components_by_screen.get(screen_id, []):
            GuiComponentLib._clear_elem(component)

    def clear_all_screens(self) -> None:
        """
        Clear the drafting of all GUI elements in every screen.

        Returns:
            None
        """
        for screen_id in self._components_by_screen:
            self._clear_screen(screen_id)
