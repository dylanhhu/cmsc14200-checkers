#
# © Kevin Gugelmann, 20 February 2023.
# All rights reserved.
#
from dataclasses import dataclass
from enum import Enum
from typing import Union, Callable

import pygame
import pygame_gui
from pygame.event import Event
from pygame_gui import UIManager, PackageResource
from pygame_gui.elements import (UIButton, UIDropDownMenu,
                                 UILabel, UIPanel, UITextEntryLine)

from src.bot import SmartLevel
from src.utils.gui.components import GuiComponentLib, ModifyElemCommand, Element
from src.utils.gui.relative_rect import (RelPos, ScreenPos, ElemPos, SelfAlign,
                                         Offset, Fraction)
from src.utils.gui.window import Dimensions, WindowOptions, DimensionsTuple


# ===============
# ENUMS
# ===============


class _Screens(Enum):
    """
    An enumeration for the internal representation of each screen.
    """

    SETUP = "#setup"
    GAME = "#game"

    @staticmethod
    def from_string(string: str) -> "_Screens":
        """
        Get enum by its string value.

        Args:
            string (str): enum value

        Returns:
            _Screens: enum
        """
        if string == _Screens.SETUP.value:
            return _Screens.SETUP
        return _Screens.GAME

    @staticmethod
    def get_setup_name() -> str:
        """
        Getter method for Setup Screen name.

        Returns:
            str: Setup Screen name
        """
        return str(_Screens.SETUP.value)

    @staticmethod
    def get_game_name() -> str:
        """
        Getter method for Game Screen name.

        Returns:
            str: Game Screen name
        """
        return str(_Screens.GAME.value)


class _PlayerType(Enum):
    """
    An enumeration for the internal representation of player types.
    """

    HUMAN = "Human"
    BOT = "Bot"

    @staticmethod
    def from_string(string: str) -> "_PlayerType":
        """
        Get enum by its string value.

        Args:
            string (str): enum value

        Returns:
            _PlayerType: enum
        """
        if string == _PlayerType.HUMAN.value:
            return _PlayerType.HUMAN
        return _PlayerType.BOT

    @staticmethod
    def get_human_name() -> str:
        """
        Getter method for human string representation.

        Returns:
            str: human string representation
        """
        return str(_PlayerType.HUMAN.value)

    @staticmethod
    def get_bot_name() -> str:
        """
        Getter method for bot string representation.

        Returns:
            str: bot string representation
        """
        return str(_PlayerType.BOT.value)


# ===============
# STATIC CONSTANT 'ENUMS'
# ===============


class _Sizes:
    MICRO = 2
    XXS = 4
    XS = 8
    S = 12
    M = 16
    L = 20
    XL = 24
    XXL = 32
    MEGA = 42


class _GeneralSizes:
    LABEL_HEIGHT = 20
    TEXTINPUT_HEIGHT = 40
    DROPDOWN_HEIGHT = 40
    BUTTON_HEIGHT = 40


class _SetupElems:
    # ID
    screen_id = _Screens.get_setup_name()

    # ===============
    # ELEMENTS
    # ===============

    WELCOME_TEXT = "#welcome-text"

    RED_PANEL = "#player-1-panel"
    RED_PANEL_TITLE = "#player-1-type-title-label"
    RED_TYPE_DROPDOWN = "#player-1-type-dropdown"
    RED_NAME_TEXTINPUT = "#player-1-name-textinput"
    RED_BOT_DIFFICULTY_DROPDOWN = "#player-1-bot-difficulty-dropdown"

    BLACK_PANEL = "#player-2-panel"
    BLACK_PANEL_TITLE = "#player-2-type-title-label"
    BLACK_TYPE_DROPDOWN = "#player-2-type-dropdown"
    BLACK_NAME_TEXTINPUT = "#player-2-name-textinput"
    BLACK_BOT_DIFFICULTY_DROPDOWN = "#player-2-bot-difficulty-dropdown"

    NUM_PLAYER_ROWS_TEXTINPUT = "#num-player-rows-textinput"
    NUM_PLAYER_ROWS_TITLE = "#num-player-rows-title"

    START_GAME_BUTTON = "#start-game-button"

    # ===============
    # LIST OF ELEMENT IDS
    # ===============

    elem_ids = [WELCOME_TEXT, RED_PANEL, BLACK_PANEL,
                RED_PANEL_TITLE, BLACK_PANEL_TITLE,
                RED_TYPE_DROPDOWN, BLACK_TYPE_DROPDOWN,
                RED_NAME_TEXTINPUT, BLACK_NAME_TEXTINPUT,
                RED_BOT_DIFFICULTY_DROPDOWN,
                BLACK_BOT_DIFFICULTY_DROPDOWN,
                NUM_PLAYER_ROWS_TEXTINPUT, NUM_PLAYER_ROWS_TITLE,
                START_GAME_BUTTON]


class _SetupConsts:
    # Numbers
    BETWEEN_PANELS = _Sizes.XL
    PANEL_WIDTH = Fraction(0.35)
    PANEL_HEIGHT = 220
    ABOVE_PANELS = _Sizes.MEGA
    PANEL_TITLE_WIDTH = Fraction(1)
    ABOVE_PANEL_TITLE = _Sizes.XXL
    BELOW_PANEL_TITLE = _Sizes.XXL
    BELOW_PLAYER_MODE_DROPDOWN = _Sizes.M
    PANEL_CONTENT_WIDTH = Fraction(0.8)
    START_GAME_BUTTON_WIDTH = Fraction(0.7)
    RIGHT_OF_NUM_ROWS = _Sizes.XS
    ABOVE_NUM_ROWS = _Sizes.XS
    NUM_PLAYER_ROWS_WIDTH = (Fraction(1) - START_GAME_BUTTON_WIDTH) - \
                            Fraction(0.02)

    # Dropdown options
    PLAYER_MODE_OPTIONS = [_PlayerType.get_human_name(),
                           _PlayerType.get_bot_name()]
    BOT_DIFFICULTY_OPTIONS = [SmartLevel.get_simple_name(),
                              SmartLevel.get_medium_name(),
                              SmartLevel.get_hard_name()]


# ===============
# APP STATE CLASS
# ===============


@dataclass
class _AppState:
    """
    Data class holding stateful values for PyGame app.
    """

    # Lifecycle
    is_alive: bool = True

    # Current screen
    screen: _Screens = _Screens.SETUP

    # Red player
    red_type: _PlayerType = _PlayerType.HUMAN
    red_name: str = ""
    red_bot_level: SmartLevel = SmartLevel.SIMPLE

    # Black player
    black_type: _PlayerType = _PlayerType.HUMAN
    black_name: str = ""
    black_bot_level: SmartLevel = SmartLevel.SIMPLE

    # Board settings
    _num_rows_per_player: Union[int, None] = 3

    @property
    def num_rows_per_player(self) -> Union[int, None]:
        """
        Getter method for the number of rows per player.
        """
        return self._num_rows_per_player

    @num_rows_per_player.setter
    def num_rows_per_player(self, v: str) -> None:
        """
        Setter method for the number of rows per player.

        Args:
            v (str): value
        """
        try:
            num_rows_int = int(v)
            if num_rows_int < 1:
                raise ValueError("Number of rows per player must be at least "
                                 "1.")

            # By this point, value is valid!
            self._num_rows_per_player = num_rows_int
        except ValueError:
            # Inputted number of rows per player is not a valid integer
            self._num_rows_per_player = None


# ===============
# GUI APP CLASS
# ===============


class GuiApp:
    """
    The graphical user interface PyGame application for the checkers board game.

    Start the GUI app via the `run()` command.
    """
    DEFAULT_WINDOW_OPTIONS = WindowOptions()

    def __init__(self,
                 window_options: WindowOptions = WindowOptions()) -> None:
        """
        Constructor for the GUI app.

        Args:
            window_options (WindowOptions): options for window presentation
        """

        # Initialize PyGame & app state
        pygame.init()
        self._state = _AppState()

        # Window setup
        self._update_window(window_options)
        self._bg_surface = None
        self._ui_manager = UIManager(self._get_window_resolution(),
                                     PackageResource(package="data.themes",
                                                     resource="theme_1.json"))

        # Initialize the element library
        self._lib = GuiComponentLib()
        self._lib.init_screen_elems(_Screens.get_setup_name(),
                                    _SetupElems.elem_ids)
        self._lib.init_screen_elems(_Screens.get_game_name(),
                                    [])

        # Build the UI for the first time
        self._rebuild_ui()

        # Start the render clock
        self._render_clock = pygame.time.Clock()

    def _update_window(self,
                       new_options: Union[WindowOptions, None] = None,
                       should_refresh_title: bool = True,
                       should_refresh_dimensions: bool = True) -> None:
        """
        Setter method for the app's window options.

        Args:
            new_options (WindowOptions | None): new window options
            should_refresh_title (bool): whether to refresh the window title
            should_refresh_dimensions (bool): whether to refresh the window
                dimensions
        """

        # Update window options in memory
        if new_options:
            self._window_options = new_options

        # Window title
        if should_refresh_title:
            pygame.display.set_caption(new_options.get_title())

        # Window dimensions
        if should_refresh_dimensions:
            if new_options.is_fullscreen():
                self._window_surface = pygame.display.set_mode(
                    new_options.get_dimensions_tuple(),
                    pygame.FULLSCREEN)
            else:
                self._window_surface = pygame.display.set_mode(
                    new_options.get_dimensions_tuple())

    def _get_window_options(self) -> WindowOptions:
        """
        Getter method for the app's window options.

        Returns:
            WindowOptions: the app's window options
        """
        return self._window_options

    def _set_window_dimensions(self, new_dimensions: Dimensions) -> None:
        """
        Setter method for the app's window dimensions.

        Raises:
            ValueError if invalid dimensions are passed.
        """
        self._window_options.set_dimensions(new_dimensions)

    def _get_window_dimensions(self) -> Dimensions:
        """
        Getter method for the app's window dimensions.

        Returns:
            Dimensions: the app's window dimensions
        """
        return self._get_window_options().get_dimensions()

    def _get_window_resolution(self) -> DimensionsTuple:
        """
        Getter method for the app's window dimensions, as a tuple of ints.

        Returns:
            DimensionsTuple: the app's window dimensions
        """
        return self._get_window_options().get_dimensions_tuple()

    def _rel_rect(self,
                  width: Union[int, Fraction],
                  height: Union[int, Fraction],
                  parent_id: Union[str, None] = None,
                  ref_pos: Union[ScreenPos, ElemPos] = ScreenPos(),
                  self_align: SelfAlign = SelfAlign(),
                  offset: Offset = Offset()) -> pygame.Rect:
        """
        Create a responsive pygame Rect based on relative screen positioning,
        relative alignment, and an offset.

        Args:
            width (Union[int, Fraction]): element width (either in px or
                fraction of parent width)
            height (Union[int, Fraction]): element height (either in px or
                fraction of parent height)
            parent_id (Union[str, None]): parent element ID – defaults to screen
            ref_pos (Union[ScreenPos, ElemPos]): relative positioning,
                according to the screen or another element (make sure the
                other element is drafted first)
            self_align (SelfAlign): self alignment in reference to `ref_pos`
            offset (Offset): offset from relative position

        Raises:
            RuntimeError if parent element's ID doesn't exist.
            RuntimeError if relative element's ID doesn't exist.
        """

        # Parent element, if chosen
        parent_elem: Union[Element, None] = None
        if parent_id:
            parent_elem = self._lib.get_elem(parent_id)

        # Calculate pixel-based width, height values
        if isinstance(width, Fraction):
            if parent_elem:
                # Fractional width based on parent element
                w = parent_elem.relative_rect.width * width.value
            else:
                # Fractional width based on screen and its padding
                w = (self._get_window_dimensions().width - 2 *
                     self._get_window_options().get_padding()) * width.value
        else:
            w = width

        if isinstance(height, Fraction):
            if parent_elem:
                # Fractional height based on parent element
                h = parent_elem.relative_rect.height * height.value
            else:
                # Fractional height based on screen and its padding
                h = (self._get_window_dimensions().height - 2 *
                     self._get_window_options().get_padding()) * height.value
        else:
            h = height

        # Calculate pixel-based reference position
        if isinstance(ref_pos, ScreenPos):
            # In reference to the screen

            if ref_pos.x_pos == RelPos.START:
                # `padding` px from left of screen
                x_ref = self._get_window_options().get_padding()
            elif ref_pos.x_pos == RelPos.CENTER:
                # horizontal center of screen
                x_ref = self._get_center_x()
            else:
                # `padding` px from right of screen
                x_ref = self._get_window_dimensions().width - \
                        self._get_window_options().get_padding()

            if ref_pos.y_pos == RelPos.START:
                # `padding` px from top of screen
                y_ref = self._get_window_options().get_padding()
            elif ref_pos.y_pos == RelPos.CENTER:
                # vertical center of screen
                y_ref = self._get_center_y()
            else:
                # `padding` px from bottom of screen
                y_ref = self._get_window_dimensions().height - \
                        self._get_window_options().get_padding()
        else:
            # In reference to another element
            other_elem = self._lib.get_elem(ref_pos.elem_id)

            if ref_pos.x_pos == RelPos.START:
                # Position left of other element
                x_ref = other_elem.relative_rect.left
            elif ref_pos.x_pos == RelPos.CENTER:
                # Position horizontal center of other element
                x_ref = other_elem.relative_rect.centerx
            else:
                # Position right of other element
                x_ref = other_elem.relative_rect.right

            if ref_pos.y_pos == RelPos.START:
                # Position top of other element
                y_ref = other_elem.relative_rect.top
            elif ref_pos.y_pos == RelPos.CENTER:
                # Position vertical center of other element
                y_ref = other_elem.relative_rect.centery
            else:
                # Position bottom of other element
                y_ref = other_elem.relative_rect.bottom

        # Calculate offset-less position, considering alignment
        if self_align.x_pos == RelPos.START:
            x = x_ref - w
        elif self_align.x_pos == RelPos.CENTER:
            x = x_ref - w / 2
        else:
            x = x_ref

        if self_align.y_pos == RelPos.START:
            y = y_ref - h
        elif self_align.y_pos == RelPos.CENTER:
            y = y_ref - h / 2
        else:
            y = y_ref

        # Return pygame Rect, now considering offset
        return pygame.Rect((int(x + offset.x), int(y + offset.y)), (w, h))

    def _get_center_x(self) -> int:
        """
        Get the x-coordinate of the screen's horizontal center.

        Returns:
            int: center x-coordinate
        """
        return self._get_window_dimensions().width // 2

    def _get_center_y(self) -> int:
        """
        Get the y-coordinate of the screen's vertical center.

        Returns:
            int: center y-coordinate
        """
        return self._get_window_dimensions().height // 2

    def _rebuild_ui(self) -> None:
        """
        Rebuilds all UI elements. Only run this if absolutely necessary,
        since compute is expensive.
        """

        # Clean slate window
        self._ui_manager.set_window_resolution(
            self._get_window_resolution())
        self._ui_manager.clear_and_reset()

        # Fill background
        self._bg_surface = pygame.Surface(self._get_window_resolution())
        self._bg_surface.fill(
            self._ui_manager.get_theme().get_colour("dark_bg")
        )

        # Create all UI elements for current screen only
        self._lib.clear_all_screens()
        self._lib.set_draft_screen(self._get_current_screen_name())
        if self._state.screen == _Screens.SETUP:
            # ===============
            # RED PANEL
            # ===============
            self._lib.draft(
                _SetupElems.RED_PANEL,
                UIPanel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_WIDTH,
                        height=_SetupConsts.PANEL_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.CENTER,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        offset=Offset(
                            - _SetupConsts.BETWEEN_PANELS // 2,
                            _SetupConsts.ABOVE_PANELS // 2),
                    ),
                    starting_layer_height=0))
            self._lib.draft(
                _SetupElems.RED_PANEL_TITLE,
                UILabel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_TITLE_WIDTH,
                        height=_GeneralSizes.LABEL_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_PANEL,
                            RelPos.CENTER,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.ABOVE_PANEL_TITLE)
                    ),
                    "Red"))
            self._lib.draft(
                _SetupElems.RED_TYPE_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.PLAYER_MODE_OPTIONS,
                    _PlayerType.get_human_name(),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralSizes.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_PANEL_TITLE,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.BELOW_PANEL_TITLE)),
                    object_id=_SetupElems.RED_TYPE_DROPDOWN,
                    manager=self._ui_manager))
            self._lib.draft(
                _SetupElems.RED_NAME_TEXTINPUT,
                UITextEntryLine(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralSizes.TEXTINPUT_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.RED_NAME_TEXTINPUT,
                    placeholder_text="Name..."))
            self._lib.draft(
                _SetupElems.RED_BOT_DIFFICULTY_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.BOT_DIFFICULTY_OPTIONS,
                    SmartLevel.get_simple_name(),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralSizes.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.RED_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.RED_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.RED_BOT_DIFFICULTY_DROPDOWN,
                    visible=False))

            # ===============
            # BLACK PANEL
            # ===============
            self._lib.draft(
                _SetupElems.BLACK_PANEL,
                UIPanel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_WIDTH,
                        height=_SetupConsts.PANEL_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.CENTER,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.CENTER
                        ),
                        offset=Offset(
                            _SetupConsts.BETWEEN_PANELS // 2,
                            _SetupConsts.ABOVE_PANELS // 2
                        ),
                    ),
                    starting_layer_height=0,
                    manager=self._ui_manager))
            self._lib.draft(
                _SetupElems.BLACK_PANEL_TITLE,
                UILabel(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_TITLE_WIDTH,
                        height=_GeneralSizes.LABEL_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_PANEL,
                            RelPos.CENTER,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.ABOVE_PANEL_TITLE)
                    ),
                    "Black"))
            self._lib.draft(
                _SetupElems.BLACK_TYPE_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.PLAYER_MODE_OPTIONS,
                    _PlayerType.get_human_name(),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralSizes.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_PANEL_TITLE,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0, _SetupConsts.BELOW_PANEL_TITLE)),
                    object_id=_SetupElems.BLACK_TYPE_DROPDOWN,
                    manager=self._ui_manager))
            self._lib.draft(
                _SetupElems.BLACK_NAME_TEXTINPUT,
                UITextEntryLine(
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralSizes.TEXTINPUT_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.BLACK_NAME_TEXTINPUT,
                    placeholder_text="Name..."))
            self._lib.draft(
                _SetupElems.BLACK_BOT_DIFFICULTY_DROPDOWN,
                UIDropDownMenu(
                    _SetupConsts.BOT_DIFFICULTY_OPTIONS,
                    SmartLevel.get_simple_name(),
                    self._rel_rect(
                        width=_SetupConsts.PANEL_CONTENT_WIDTH,
                        height=_GeneralSizes.DROPDOWN_HEIGHT,
                        parent_id=_SetupElems.BLACK_PANEL,
                        ref_pos=ElemPos(
                            _SetupElems.BLACK_TYPE_DROPDOWN,
                            RelPos.CENTER,
                            RelPos.END),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.END
                        ),
                        offset=Offset(0,
                                      _SetupConsts.BELOW_PLAYER_MODE_DROPDOWN)),
                    manager=self._ui_manager,
                    object_id=_SetupElems.BLACK_BOT_DIFFICULTY_DROPDOWN,
                    visible=False))

            # ===============
            # WELCOME TEXT
            # ===============
            self._lib.draft(
                _SetupElems.WELCOME_TEXT,
                UILabel(
                    self._rel_rect(
                        width=Fraction(1),
                        height=_GeneralSizes.LABEL_HEIGHT,
                        ref_pos=ElemPos(
                            _SetupElems.RED_PANEL,
                            RelPos.END,
                            RelPos.START
                        ),
                        offset=Offset(
                            _SetupConsts.BETWEEN_PANELS // 2,
                            - _SetupConsts.ABOVE_PANELS),
                        self_align=SelfAlign(
                            RelPos.CENTER,
                            RelPos.START
                        )),
                    "Welcome to Checkers!",
                    self._ui_manager,
                    object_id=_SetupElems.WELCOME_TEXT))

            # ===============
            # START GAME BUTTON
            # ===============
            self._lib.draft(
                _SetupElems.START_GAME_BUTTON,
                UIButton(
                    self._rel_rect(
                        width=_SetupConsts.START_GAME_BUTTON_WIDTH,
                        height=_GeneralSizes.BUTTON_HEIGHT,
                        ref_pos=ScreenPos(
                            RelPos.END,
                            RelPos.END
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.START
                        )),
                    "Start game",
                    self._ui_manager,
                    object_id=_SetupElems.START_GAME_BUTTON))
            self._validate_game_setup()

            # ===============
            # NUM PLAYER ROWS
            # ===============
            self._lib.draft(
                _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT,
                UITextEntryLine(
                    self._rel_rect(
                        width=_SetupConsts.NUM_PLAYER_ROWS_WIDTH,
                        height=_GeneralSizes.BUTTON_HEIGHT,  # match button
                        ref_pos=ElemPos(
                            _SetupElems.START_GAME_BUTTON,
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        self_align=SelfAlign(
                            RelPos.START,
                            RelPos.CENTER
                        ),
                        offset=Offset(- _SetupConsts.RIGHT_OF_NUM_ROWS, 0)
                    ),
                    manager=self._ui_manager,
                    object_id=_SetupElems.NUM_PLAYER_ROWS_TEXTINPUT,
                    placeholder_text="Number...",
                    initial_text=str(self._state.num_rows_per_player)))
            self._lib.draft(
                _SetupElems.NUM_PLAYER_ROWS_TITLE,
                UILabel(
                    self._rel_rect(
                        width=180,
                        height=_GeneralSizes.LABEL_HEIGHT,
                        ref_pos=ElemPos(
                            _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT,
                            RelPos.START,
                            RelPos.START
                        ),
                        self_align=SelfAlign(
                            RelPos.END,
                            RelPos.START
                        ),
                        offset=Offset(0, - _SetupConsts.ABOVE_NUM_ROWS)
                    ),
                    "Rows per player (>= 1)",
                )
            )

    def _check_window_dimensions_changed(self) -> None:
        """
        Checks whether the window dimensions have changed. If they have,
        the UI is rebuilt accordingly.
        """
        current_dimensions_tuple = pygame.display.get_surface().get_size()
        if current_dimensions_tuple != self._get_window_resolution():
            # Window dimensions have changed since last paint:
            # store the new dimensions in memory
            self._window_options.set_dimensions(
                Dimensions.from_tuple(current_dimensions_tuple))

            # Update the window & rebuild the UI
            self._update_window(should_refresh_title=False)
            self._rebuild_ui()

    def _get_current_screen(self) -> _Screens:
        """
        Getter method for the current screen.

        Returns:
            _Screens: current screen
        """
        return self._state.screen

    def _get_current_screen_name(self) -> str:
        """
        Getter method for the string representation of the current screen.

        Returns:
            str: current screen name
        """
        return str(self._get_current_screen().value)

    def _set_current_screen(self, new_screen: _Screens) -> None:
        """
        Setter method for the current screen.

        Args:
            new_screen (_Screens): new screen
        """
        self._state.screen = new_screen

    def _open_screen(self, new_screen: _Screens) -> None:
        """
        Navigate to a different screen. If screen is already open – ignore.

        Args:
            new_screen (_Screens): screen to navigate to

        TODO: this crashes the app since removing screen_id as param across
            `GuiComponentLib`
        """
        if new_screen != self._get_current_screen():
            # Screen is not already open
            self._set_current_screen(new_screen)
            # Needs rebuild UI to clear old screen & draw new screen
            self._rebuild_ui()

    def _validate_game_setup(self) -> None:
        """
        Check whether the game is set up correctly, and enable/disable the
        start game button accordingly.
        """
        try:
            if self._state.num_rows_per_player is None:
                raise ValueError()
            if self._state.red_type == _PlayerType.HUMAN:
                if self._state.red_name == "":
                    raise ValueError()
            if self._state.black_type == _PlayerType.HUMAN:
                if self._state.black_name == "":
                    raise ValueError()

            # By this point, the game setup is all valid!
            self._lib.enable_elem(_SetupElems.START_GAME_BUTTON)
        except ValueError:
            self._lib.disable_elem(_SetupElems.START_GAME_BUTTON)

    def _process_setup_events(self, event: "Event") -> None:
        """
        Process user interactions events for the Setup screen.

        Args:
            event (Event): PyGame event
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == _SetupElems.START_GAME_BUTTON:
                # ===============
                # Clicked: START GAME BUTTON
                # ===============
                self._open_screen(_Screens.GAME)
                return  # stop processing events in Setup screen

        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_object_id == _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT:
                # ===============
                # Updated text: NUM PLAYER ROWS TEXT INPUT
                # ===============
                self._state.num_rows_per_player = self._lib.get_elem_text(
                    _SetupElems.NUM_PLAYER_ROWS_TEXTINPUT)

        def process_panel_events(
                initial_player_type: _PlayerType,
                player_type_dropdown_id: str,
                on_update_player_type: Callable[[_PlayerType], None],
                name_input_id: str,
                on_update_name: Callable[[str], None],
                initial_bot_difficulty: SmartLevel,
                bot_difficulty_dropdown_id: str,
                on_update_bot_difficulty: Callable[[SmartLevel], None]) -> None:
            """
            Process user interaction events for a given panel.

            Args:
                initial_player_type (_PlayerType): initial player type
                player_type_dropdown_id (str): player type dropdown ID
                on_update_player_type (Callable[[_PlayerType], None]): update
                    player type callback
                name_input_id (str): name text input ID
                on_update_name (Callable[[str], None]): update player name
                    callback
                initial_bot_difficulty (SmartLevel): initial bot difficulty
                    level
                bot_difficulty_dropdown_id (str): bot difficulty level
                    dropdown ID
                on_update_bot_difficulty (Callable[[SmartLevel], None]): update
                    bot difficulty level callback

            """
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_object_id == player_type_dropdown_id:
                    # ===============
                    # Selection: PLAYER TYPE DROPDOWN
                    # ===============
                    selection = self._lib.get_elem_selection(
                        player_type_dropdown_id)
                    selected_type = _PlayerType.from_string(selection)
                    if selected_type != initial_player_type:
                        # ===============
                        # Updated selection: PLAYER TYPE
                        # ===============
                        on_update_player_type(selected_type)
                        # Show elements relevant to that player type
                        self._lib.mod_elem(
                            name_input_id,
                            ModifyElemCommand.SHOW \
                                if selected_type == _PlayerType.HUMAN \
                                else ModifyElemCommand.HIDE)
                        self._lib.mod_elem(
                            bot_difficulty_dropdown_id,
                            ModifyElemCommand.SHOW \
                                if selected_type == _PlayerType.BOT \
                                else ModifyElemCommand.HIDE)
                    return
                elif event.ui_object_id == bot_difficulty_dropdown_id:
                    # ===============
                    # Selection: PLAYER BOT DIFFICULTY DROPDOWN
                    # ===============
                    selection = self._lib.get_elem_selection(
                        bot_difficulty_dropdown_id)
                    selected_difficulty = SmartLevel.from_string(selection)
                    if selected_difficulty != initial_bot_difficulty:
                        # ===============
                        # Updated selection: PLAYER BOT DIFFICULTY
                        # ===============
                        on_update_bot_difficulty(selected_difficulty)
                    return

            elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_object_id == name_input_id:
                    # ===============
                    # Updated text: PLAYER NAME
                    # ===============
                    on_update_name(self._lib.get_elem_text(name_input_id))

        # ===============
        # RED PANEL
        # ===============

        def on_update_red_player_type(new_type: _PlayerType) -> None:
            """
            Callback for when red player type is updated.

            Args:
                new_type (_PlayerType): new player type
            """
            self._state.red_type = new_type

        def on_update_red_name(new_name: str) -> None:
            """
            Callback for when red player name is updated.

            Args:
                new_name (str): new name
            """
            self._state.red_name = new_name

        def on_update_red_bot_difficulty(new_difficulty: SmartLevel) -> None:
            """
            Callback for when red bot difficulty level is updated.

            Args:
                new_difficulty (SmartLevel): new difficulty level
            """
            self._state.red_bot_level = new_difficulty

        process_panel_events(
            initial_player_type=self._state.red_type,
            player_type_dropdown_id=_SetupElems.RED_TYPE_DROPDOWN,
            on_update_player_type=on_update_red_player_type,
            name_input_id=_SetupElems.RED_NAME_TEXTINPUT,
            on_update_name=on_update_red_name,
            initial_bot_difficulty=self._state.red_bot_level,
            bot_difficulty_dropdown_id=_SetupElems.RED_BOT_DIFFICULTY_DROPDOWN,
            on_update_bot_difficulty=on_update_red_bot_difficulty
        )

        # ===============
        # BLACK PANEL
        # ===============

        def on_update_black_player_type(new_type: _PlayerType) -> None:
            """
            Callback for when black player type is updated.

            Args:
                new_type (_PlayerType): new player type
            """
            self._state.black_type = new_type

        def on_update_black_name(new_name: str) -> None:
            """
            Callback for when black player name is updated.

            Args:
                new_name (str): new name
            """
            self._state.black_name = new_name

        def on_update_black_bot_difficulty(new_difficulty: SmartLevel) -> None:
            """
            Callback for when black bot difficulty level is updated.

            Args:
                new_difficulty (SmartLevel): new difficulty level
            """
            self._state.black_bot_level = new_difficulty

        process_panel_events(
            initial_player_type=self._state.black_type,
            player_type_dropdown_id=_SetupElems.BLACK_TYPE_DROPDOWN,
            on_update_player_type=on_update_black_player_type,
            name_input_id=_SetupElems.BLACK_NAME_TEXTINPUT,
            on_update_name=on_update_black_name,
            initial_bot_difficulty=self._state.black_bot_level,
            bot_difficulty_dropdown_id=
            _SetupElems.BLACK_BOT_DIFFICULTY_DROPDOWN,
            on_update_bot_difficulty=on_update_black_bot_difficulty
        )

        # Enable/disable 'start game' button, depending on whether game
        # is set up correctly.
        self._validate_game_setup()

    def _process_events(self) -> None:
        """
        Process user interaction events. This is the planning stage for
        painting.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Quit the app
                self._state.is_alive = False
                return

            # Inform the PyGame-GUI UIManager of events
            # (e.g. updating button hover state)
            self._ui_manager.process_events(event)

            # Process events for the current screen
            if self._get_current_screen() == _Screens.SETUP:
                self._process_setup_events(event)
            elif self._get_current_screen() == _Screens.GAME:
                pass

        # In every loop, check whether the window has been resized
        self._check_window_dimensions_changed()

    def run(self) -> None:
        """
        Start the app in a GUI window.
        """
        while self._state.is_alive:
            # Check for user interaction
            self._process_events()

            # Update UI elements in memory
            time_delta = self._render_clock.tick() / 1000.0
            self._ui_manager.update(time_delta)

            # Paint all changes
            self._window_surface.blit(self._bg_surface, (0, 0))
            self._ui_manager.draw_ui(self._window_surface)

            # Update PyGame display
            pygame.display.update()


if __name__ == "__main__":
    app = GuiApp()
    app.run()
