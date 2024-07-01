import pygame
print() #leave newline between pygame message and app text logs
from pygame.locals import *
from pygame.time import Clock
import json
import datetime

from lib.gui import *

#for debugging
from pprint import pprint

#-------------------------------------------------------------------------------

CURRENT_RULESET = 1 #written in save game files. Increment when game code changes significantly
CURRENT_SAVEFILE_FORMAT = 3 #increment if savefile format changes

BOARD_SIZE_IN_SQ = 8
#Each side will have a back row followed by a row of pawns;
# the back rows on each side mirror each other
#Below describes the back rows from left to right as seen from white's side
PIECE_LAYOUT_16 = (1, 2, 6, 3, 1, 7, 3, 4, 5, 3, 7, 1, 3, 6, 2, 1)
PIECE_LAYOUT_8 = (1, 2, 3, 4, 5, 3, 2, 1)
PIECE_LAYOUT = PIECE_LAYOUT_8
PIECE_NAMES = ('Pawn', 'Rook', 'Knight', 'Bishop',
               'Queen', 'King', 'Duck', 'Frog', 'Ghost')

SETTINGS_FILEPATH = 'settings.json'

# settings are loaded on app startup
# settings are written to file when app closed (for layout changes)
class Settings:
    def __init__(self, filepath):
        self.load_from_file(filepath)
        self.settings_filepath = filepath

    def load_from_file(self, filepath):
        #note: dimensions in layout are in pixels, so should all be +ve integers
        with open(filepath) as file:
            save_obj = json.load(file)
        self.sq_size_assumption = save_obj['layout']['sq_size_assumption']
        self.piece_size_assumption = save_obj['layout']['piece_size_assumption']
        self.sq_size = save_obj['layout']['square_size']
        self.piece_size = save_obj['layout']['piece_size']
        self.piece_size_ratio = save_obj['layout']['piece_size_ratio']
        self.heaven_width_in_sq = save_obj['layout']['heaven_width_in_sq']
        self.text_font_type = save_obj['style']['font']
        self.text_font_size = save_obj['style']['font_size']
        self.text_font = None
        self.back_col_str = save_obj['style']['background_colour']
        self.white_sq_col_str = save_obj['style']['white_sq_colour']
        self.black_sq_col_str = save_obj['style']['black_sq_colour']
        self.line_col_str = save_obj['style']['line_colour']
        self.heaven_col_str = save_obj['style']['heaven_colour']
        self.bhole_col_str = save_obj['style']['black_hole_colour']
        self.portal_cols = save_obj['style']['portal_colours']
        self.line_width = save_obj['style']['line_width']
        self.max_framerate = save_obj['display']['max_framerate']
        self.stash_game = save_obj['game']['stash_game']
        self.auto_undo_on = save_obj['game']['auto_undo_on']
        self.save_path = save_obj['other']['save_path']
        self.open_path = save_obj['other']['open_path']
        self.stash_path = save_obj['other']['stash_path']
        self.img_path = save_obj['other']['img_path']
        self.wide_spacing = save_obj['layout']['wide_spacing']
        self.narrow_spacing = save_obj['layout']['narrow_spacing']

    def save_to_file(self, filepath=None):
        if filepath is None:
            filepath = self.settings_filepath
        save_obj = {'layout' : {}, 'style' : {}, 'display' : {},
                    'game' : {}, 'other' : {} }
        save_obj['layout']['sq_size_assumption'] = self.sq_size_assumption
        save_obj['layout']['piece_size_assumption'] = self.piece_size_assumption
        save_obj['layout']['square_size'] = self.sq_size
        save_obj['layout']['piece_size'] = self.piece_size
        save_obj['layout']['piece_size_ratio'] = self.piece_size_ratio
        save_obj['layout']['heaven_width_in_sq'] = self.heaven_width_in_sq
        save_obj['layout']['wide_spacing'] = self.wide_spacing
        save_obj['layout']['narrow_spacing'] = self.narrow_spacing
        save_obj['style']['font'] = self.text_font_type
        save_obj['style']['font_size'] = self.text_font_size
        save_obj['style']['background_colour'] = self.back_col_str
        save_obj['style']['white_sq_colour'] = self.white_sq_col_str
        save_obj['style']['black_sq_colour'] = self.black_sq_col_str
        save_obj['style']['line_colour'] = self.line_col_str
        save_obj['style']['heaven_colour'] = self.heaven_col_str
        save_obj['style']['black_hole_colour'] = self.bhole_col_str
        save_obj['style']['portal_colours'] = self.portal_cols
        save_obj['style']['line_width'] = self.line_width
        save_obj['display']['max_framerate'] = self.max_framerate
        save_obj['game']['stash_game'] = self.stash_game
        save_obj['game']['auto_undo_on'] = self.auto_undo_on
        save_obj['other']['save_path'] = self.save_path
        save_obj['other']['open_path'] = self.open_path
        save_obj['other']['stash_path'] = self.stash_path
        save_obj['other']['img_path'] = 'images\\'#self.img_path
        with open(filepath, mode='w') as file:
            json.dump(save_obj, file, indent=4)

    def restore_default():
        self.sq_size_assumption = 'constant_or_max_possible'
        self.piece_size_assumption = 'ratio'
        self.sq_size = 100
        self.piece_size = 80
        self.piece_size_ratio = 0.8
        self.heaven_width_in_sq = 2
        self.text_font_type = 'bahnschrift'
        self.text_font_size = 21
        self.text_font = None
        self.back_col_str = '#eeeeff'
        self.white_sq_col_str = 'white'
        self.black_sq_col_str = '#d0d0d0'
        self.line_col_str = 'black'
        self.heaven_col_str = '#77ddff'
        self.bhole_col_str = 'black'
        self.portal_cols = (('#FF4DFF', '#D641D6'), #pinkish purple
                            ('#9C59FF', '#7C4BDE'), #lavender purple
                            ('#FF643D', '#C24C2E'), #red
                            ('#EFD64E', '#D5BF42'), #gold
                            ('#95DE43', '#7FBD39'), #green
                            )
        self.line_width = 0
        self.max_framerate = 60 #frames per second
        self.stash_game = True
        self.auto_undo_on = True
        self.save_path = "saved_games\\saved_game.json"
        self.open_path = "saved_games\\saved_game.json"
        self.stash_path = "saved_games\\stashed_game.json"
        self.img_path = "images\\"
        self.wide_spacing = 15
        self.narrow_spacing = 7

    def get_font(self):
        if self.text_font is None:
            self.text_font = pygame.font.SysFont(self.text_font_type, self.text_font_size)
        return self.text_font

# Yes, I have written a custom class to handle window layout. It's a bit clunky
class WindowLayout:
    @staticmethod
    def get_text_size(font, text : str):
        text_surf = font.render(text, True, 'black')
        return text_surf.get_size()

    def calculate_square_size(self, max_client_w, max_client_h):
        '''Calculate square size based on current settings (self.settings),
        and restrictions of screen size'''
        assert (self.settings.sq_size_assumption in
                ('constant', 'max_possible', 'constant_or_max_possible'))
        if (self.settings.sq_size_assumption in
            ('constant', 'constant_or_max_possible')):
            try:
                square_size = int(round(self.settings.sq_size))
            except (ValueError, TypeError):
                raise TypeError(f'{square_size=} : constant assumption : '
                                'should be numeric value')
            if square_size <= 0:
                raise ValueError(f'{square_size=} : constant assumption : '
                                 'should be positive')
        if (self.settings.sq_size_assumption in
            ('constant_or_max_possible', 'max_possible')):
            if max_client_w is None and max_client_h is None:
                raise TypeError('max_window_width and max_window_height both None'
                                f' : {assumption} : min 1 should be given')
            horiz = float('inf')
            vert = float('inf')
            if max_client_w is not None:
                try:
                    #square size is always total square size, incl line width in board
                    #one line width extra on side of board
                    horiz = (int(max_client_w)
                             - 4 * self.settings.wide_spacing
                             - self.settings.line_width)
                    horiz //= (self.board_size_in_sq
                               + 2 * self.settings.heaven_width_in_sq)
                except (ValueError, TypeError):
                    raise TypeError(f'{max_window_width=} : should be numeric value')
            if max_client_h is not None:
                try:
                    vert = (int(max_client_h)
                            - self.top_bar_height
                            - self.settings.wide_spacing
                            - self.settings.line_width)
                    vert //= self.board_size_in_sq
                except (ValueError, TypeError):
                    raise TypeError(f'{max_window_height=} : should be numeric value')
            max_poss_sq_size = min(horiz, vert)
        if self.settings.sq_size_assumption == 'max_possible':
            square_size = max_poss_sq_size
        elif self.settings.sq_size_assumption == 'constant_or_max_possible':
            square_size = min(square_size, max_poss_sq_size)
        return square_size

    def calculate_piece_size(self):
        '''Calculates piece size based on self.settings, and self.square_size'''
        assert self.settings.piece_size_assumption in ('constant', 'ratio')
        #Ratio piece size assumption : piece size is [ratio] times the square size
        # - this means the pieces can be slightly smaller than the squares
        # which looks nice
        if self.settings.piece_size_assumption == 'constant':
            assert self.settings.piece_size is not None
            try:
                piece_size = int(self.settings.piece_size)
            except (ValueError, TypeError):
                raise TypeError(f'{piece_size=} : constant assumption : '
                                'should be integer')
            if piece_size <= 0:
                raise ValueError(f'{piece_size=} : constant assumption : '
                                 'should be positive integer')
        elif self.settings.piece_size_assumption == 'ratio':
            assert self.settings.piece_size_ratio is not None
            try:
                piece_size_ratio = float(self.settings.piece_size_ratio)
            except (ValueError, TypeError):
                raise TypeError(f'{piece_size_ratio=} : ratio assumption : '
                                'ratio should be numeric')
            if piece_size_ratio < 0.1 or piece_size_ratio > 1.0:
                raise ValueError(f'{piece_size_ratio=} : ratio assumption : '
                                 'ratio should be positive and within 0.1 to 1.0')
            piece_size = int(round(self.square_size * piece_size_ratio))
        return piece_size

    def __init__(self, settings, board_size_in_sq, max_client_w, max_client_h):
        self.settings = settings
        self.board_size_in_sq = board_size_in_sq
        self.font = settings.get_font()
        #Used 'Ffp' as it ought to be the maximum height text in any font ...?
        self.top_bar_height = (self.get_text_size(self.font, 'Ffp')[1]
                               + 2 * settings.narrow_spacing
                               + settings.wide_spacing)
        self.square_size = self.calculate_square_size(max_client_w, max_client_h)
        self.piece_size = self.calculate_piece_size()
        self.window_width = (self.square_size *
                               (board_size_in_sq + 2*settings.heaven_width_in_sq)
                             + 4 * settings.wide_spacing)
        self.window_height = (self.top_bar_height
                             + self.square_size * board_size_in_sq
                             + settings.wide_spacing)
        #top bar buttons
        self.left_buttons = []
        self.last_left_btn_end = 0
        self.middle_buttons = []
        self.middle_btn_width = 0
        self.middle_btn_right_end = self.window_width // 2
        self.right_buttons = []
        self.last_right_btn_end = 0
    def get_left_heaven_coords(self):
        return (self.settings.wide_spacing, self.top_bar_height)
    def get_board_coords(self):
        return (2 * self.settings.wide_spacing + 2 * self.square_size,
                self.top_bar_height)
    def get_right_heaven_coords(self):
        return (3 * self.settings.wide_spacing
                + (self.board_size_in_sq+2)*self.square_size,
                self.top_bar_height)
    def get_heaven_size_in_sq(self):
        return (self.settings.heaven_width_in_sq, self.board_size_in_sq)
    def get_button_size(self, text_size):
        '''Determines button size given text size by adding padding'''
        return (text_size[0] + 2 * self.settings.narrow_spacing,
                text_size[1] + self.settings.narrow_spacing)
    def add_button(self, button, loc):
        '''loc is 'left', 'middle', or 'right'
        Button should already be initialised with correct text
        This function sets button's size and location'''
        button.change_size(
            self.get_button_size(button.get_text_size())
        )
        if loc == 'left':
            x = self.last_left_btn_end + self.settings.narrow_spacing
            button.set_pos((x, self.settings.narrow_spacing))
            self.left_buttons.append(button)
            self.last_left_btn_end += button.rect[2] + self.settings.narrow_spacing
        elif loc == 'middle':
            move_left_by = (button.rect[2] + self.settings.narrow_spacing) // 2
            x = self.middle_btn_right_end + self.settings.narrow_spacing - move_left_by
            button.set_pos((x, self.settings.narrow_spacing))
            for b in self.middle_buttons:
                x, y = b.get_pos()
                b.set_pos((x - move_left_by, y))
            self.middle_buttons.append(button)
            self.middle_btn_width += button.rect[2] + self.settings.narrow_spacing
            self.middle_btn_right_end = button.rect[0] + button.rect[2]
        elif loc == 'right':
            x = (self.window_width
                 - self.last_right_btn_end
                 - self.settings.narrow_spacing
                 - button.rect[2])
            button.set_pos((x, self.settings.narrow_spacing))
            self.right_buttons.append(button)
            self.last_right_btn_end += button.rect[2] + self.settings.narrow_spacing
        else:
            raise ValueError("loc should be 'left', 'middle', or 'right', not {loc}")

#-------------------------------------------------------------------------------

class Board:
    '''Draws board on the screen.
    Also contains helper funcs for user interaction'''
    def __init__(self, window, x, y, size_in_sq, square_size, settings):
        '''square_size is size of one square in pixels.
        colours and line_width in settings used when drawing'''
        self.settings = settings

        #user interaction
        self.window = window
        self.clickable = False
        self.draggable = False

        #drawing on screen
        self.left, self.top = x, y
        self.size_in_sq = size_in_sq #how many squares along side of board
        self.set_square_size(square_size)

    def set_square_size(self, new_square_size):
        '''square_size is the size of one square in pixels'''
        self.square_size = new_square_size
        self.total_px_size = (self.size_in_sq * new_square_size
                              + self.settings.line_width)
        self.right = self.left + self.total_px_size
        self.bottom = self.top + self.total_px_size

    def contains_coords(self, pos):
        return (self.left <= pos[0] < self.right and
                self.top  <= pos[1] < self.bottom)
    def square_at(self, pos):
        '''Assumes the window coordinates x, y are on the board'''
        return ((pos[0] - self.left) // self.square_size,
                (pos[1] - self.top) // self.square_size)
    def coords_of(self, square):
        '''Assumes square is a valid square on the board
        Return window coords of top left corner of square'''
        return (self.left + square[0] * self.square_size,
                self.top  + square[1] * self.square_size)

    def draw(self):
        #draw squares
        x = self.left
        for i in range(self.size_in_sq):
            y = self.top
            for j in range(self.size_in_sq):
                colour = (self.settings.black_sq_col_str if (i+j)%2
                          else self.settings.white_sq_col_str)
                pygame.draw.rect(self.window, colour,
                                 (x, y,
                                  self.square_size,
                                  self.square_size))
                y += self.square_size
            x += self.square_size
        #draw lines
        if self.settings.line_width:
            x = self.left
            y = self.top
            half_width, parity = divmod(self.settings.line_width, 2)
            horiz_start = self.left - half_width + (1 - parity)
            horiz_end = self.right - half_width - parity
            vert_start = self.top - half_width + (1 - parity)
            vert_end = self.bottom - half_width - parity
            for i in range(self.size_in_sq+1):
                pygame.draw.line(self.window, self.settings.line_col_str,
                                 (x, vert_start), (x, vert_end),
                                 self.settings.line_width)
                pygame.draw.line(self.window, self.settings.line_col_str,
                                 (horiz_start, y), (horiz_end, y),
                                 self.settings.line_width)
                x += self.square_size
                y += self.square_size
        #draw river, old style
        river_width = 0
        river_pos = self.size_in_sq // 2
        if False:
            y = self.top + river_pos * self.square_size
            pygame.draw.line(self.window, self.settings.river_col_str,
                             (self.left, y), (self.right, y),
                             river_width)
        #draw river, new style
        river_cols = ('#8888ff', '#7777ee')
        river_squares = [(i,8) for i in range(9)] + [(i,7) for i in range(7, 16)]
        if False:
            for sq in river_squares:
                x, y = self.coords_of(sq)
                pygame.draw.rect(self.window, river_cols[sum(sq)%2],
                                 (x, y, self.square_size, self.square_size))

# The UI element that renders captured ('dead') pieces
class PieceHeaven:
    def __init__(self, window, x, y, square_size,
                 width_in_sq, height_in_sq,
                 colour):
        self.window = window
        self.clickable = False
        self.draggable = False

        px_width = square_size * width_in_sq
        px_height = square_size * height_in_sq
        self.square_size = square_size
        self.rect = (x, y, px_width, px_height)
        self.left, self.top = x, y
        self.right, self.bottom = x + px_width, y + px_height
        self.colour = colour

        self.width_in_sq = width_in_sq
        self.height_in_sq = height_in_sq

    def contains_coords(self, pos):
        return (self.left <= pos[0] < self.rect[0] + self.right and
                self.top  <= pos[1] < self.rect[1] + self.bottom)

    def square_at(self, pos):
        return ((pos[0] - self.left) // self.square_size,
                (pos[1] - self.top ) // self.square_size)

    def coords_of(self, square):
        return (self.left + self.square_size * square[0],
                self.top  + self.square_size * square[1])

    def draw(self):
        pygame.draw.rect(self.window, self.colour, self.rect)

# Used to order pieces inside a PieceHeaven
class ColumnOrdering:
    '''Column-first ordering for squares in a square_based grid.
    Relies on coordinate 2-tuples which go (across, up).
    If it was (up, across) this would give ordering by rows.
    Also assumes that we start at (0, 0) corner.'''
    def __init__(self, horiz_size, vert_size):
        self.horiz_size = horiz_size
        self.vert_size = vert_size
    def first(self):
        return (0, 0)
    def last(self):
        return (self.horiz_size - 1, self.vert_size - 1)
    def previous(self, square):
        '''return None if square is (0, 0)'''
        if square[1] == 0:
            if square[0] == 0:
                return None
            return (square[0] - 1, self.vert_size - 1)
        return (square[0], square[1] - 1)
    def next(self, square):
        '''return None if square is (self.horiz_size, self.vert_size)'''
        if square[1] + 1 == self.vert_size:
            if square[0] + 1 == self.horiz_size:
                return None
            return (square[0] + 1, 0)
        return (square[0], square[1] + 1)
    def index(self, square):
        '''Assume square is within bounds'''
        return square[0] * self.vert_size + square[1]

class PieceHandler:
    '''This class handles the game code, setting up the board, and moving the pieces'''
    PLACE_I_BOARD = 0
    PLACE_I_WHITE_HEAVEN = 1
    PLACE_I_BLACK_HEAVEN = 2
    WHITE_PIECE = 1
    BLACK_PIECE = 2
##    MODE_MOVE_PIECES = 0
##    MODE_EDIT_BLACK_HOLES = 1
##    MODE_EDIT_PORTALS = 2
##    MODE_EDIT_PIECES = 3

    def __init__(self, window, win_layout, board, left_heaven, right_heaven,
                 img_path, piece_layout,
                 portal_colours, black_hole_colour,
                 app, object_name):
        self.window = window
        self.window_layout = win_layout
        self.clickable = True
        self.draggable = True
        self.is_being_clicked = False
        self.app = app
        self.name = object_name

        self.board = board
        self.left_heaven = left_heaven
        self.right_heaven = right_heaven
        self.white_heaven = left_heaven #*
        self.black_heaven = right_heaven #this isn't racism i promise
        self.white_heaven_ordering = ColumnOrdering(
            self.white_heaven.width_in_sq,
            self.white_heaven.height_in_sq)
        self.black_heaven_ordering = ColumnOrdering(
            self.black_heaven.width_in_sq,
            self.black_heaven.height_in_sq)
        self.right_heaven_ordering = self.black_heaven_ordering #*
        # init piece types
        self.img_path = img_path
        s = win_layout.piece_size
        l = self._load_piece_img
        p = self._prepare_piece_type
        self.piece_types = (
            p('Pawn',   l('white_pawn.png',s),   l('black_pawn.png',s)),
            p('Rook',   l('white_rook.png',s),   l('black_rook.png',s)),
            p('Kinght', l('white_knight.png',s), l('black_knight.png',s)),
            p('Bishop', l('white_bishop.png',s), l('black_bishop.png',s)),
            p('Queen',  l('white_queen.png',s),  l('black_queen.png',s)),
            p('King',   l('white_king.png',s),   l('black_king.png',s)),
            p('Duck',   l('white_duck.png',s),   l('black_duck.png',s)),
            p('Frog',   l('white_frog.png',s),   l('black_frog.png',s)),
            p('Ghost',  l('white_ghost.png',s),  l('black_ghost.png',s))
        )

        #for drawing portals/black holes
        self.portal_cols = portal_colours
        self.black_hole_col = black_hole_colour
        #account for board line width when drawing environment
        line_w = settings.line_width
        sq_size = win_layout.square_size
        self.board_sq_offset = line_w // 2
        self.board_sq_size = sq_size - line_w
        self.get_board_sq_rect = lambda pos: (pos[0]+self.board_sq_offset,
                                              pos[1]+self.board_sq_offset,
                                              sq_size,
                                              sq_size)
        #for editing portals - colour selection in right heaven
        self.portal_col_at = {}
        sq = self.right_heaven_ordering.first()
        for i, col in enumerate(portal_colours):
            self.portal_col_at[sq] = i
            sq = self.right_heaven_ordering.next(sq)
        self.selected_portal_col = 0

        # init portals and env_at
        self.black_holes = [] #contains board square coordinates (2-tuples)
        self.portals = [[] for i in range(len(self.portal_cols))]
        self._env_at = {} #key is board square coordinate 2-tuple, value is a tuple:
                          # black-hole=(1,), portal=(2,group_id)
        self.is_reset_portals = True
        # init pieces & their layout
        self.piece_layout = piece_layout
        self.reset_pieces()
        self.is_reset_portals = True
        #dragging pieces
        self.drag_piece = None
        self.drag_piece_index = None
        self.drag_loc_from = None
        self.drag_offset = None
        self.drag_mouse_pos = None
        #format: same as undo/redo
        #allows for planning for things to happen once a piece is
        # drag-and-dropped
        self.actions_on_drop = [] #currently unused

        #0: move pieces, 1: edit black holes, 2: edit portals, 3: edit pieces
        self.mode = 0

        self.mark_is_reset_pieces_action = ['pass', (),
                                            'mark_is_reset_pieces', ()]
        self.mark_is_reset_portals_action = ['pass', (),
                                             'mark_is_reset_portals', ()]

    def _load_piece_img(self, img_name, piece_size):
        img = pygame.image.load(self.img_path+img_name).convert_alpha()
        img_w, img_h = img.get_size()
        if img_w > img_h:
            h = round(piece_size * img_h / img_w)
            return pygame.transform.scale(img, (piece_size, h))
        else:
            w = round(piece_size * img_w / img_h)
            return pygame.transform.scale(img, (w, piece_size))
    def _prepare_piece_type(self, name, white_img, black_img):
        '''Encapsulates calculating required offset of piece
        image from top left corner of square, in order to center it.
        Assumes white and black image have the same dimensions'''
        img_w, img_h = white_img.get_size()
        x_offset = (self.window_layout.square_size - img_w) // 2
        y_offset = (self.window_layout.square_size - img_h) // 2
        return (name, white_img, black_img, x_offset, y_offset)

    def get_name(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def get_undo_able_funcs(self):
        return (
            ('mark_is_reset_pieces', self.mark_is_reset_pieces),
            ('mark_is_reset_portals', self.mark_is_reset_portals),
            ('_move_up_white_heaven', self._move_up_white_heaven),
            ('_move_down_white_heaven', self._move_down_white_heaven),
            ('_move_up_black_heaven', self._move_up_black_heaven),
            ('_move_down_black_heaven', self._move_down_black_heaven),
            ('set_mode', self.set_mode),
            ('add_piece', self.add_piece),
            ('remove_piece', self.remove_piece),
            ('change_piece_type', self.change_piece_type),
            ('move_piece', self.move_piece),
            ('kill_piece', self.kill_piece),
            ('set_black_hole', self.set_black_hole),
            ('remove_black_hole', self.remove_black_hole),
            ('set_portal', self.set_portal),
            ('remove_portal', self.remove_portal),
            ('select_portal_col', self.select_portal_col),
            ('reset_pieces', self.reset_pieces),
            ('reset_portals', self.reset_pieces),
            ('restore_state', self.restore_state),
        )
    def add_undo(self, actions):
        self.app.add_to_undo_stack(actions, self.name)

    def set_mode(self, mode):
        assert mode in (0, 1, 2, 3), 'check valid mode'
        self.mode = mode

    def mark_is_reset_pieces(self):
        self.is_reset_pieces = True
    def mark_is_reset_portals(self):
        self.is_reset_portals = True
    def _disturb_pieces(self):
        '''called whenever pieces or black holes are modified;
        sets is_reset_pieces to False
        Returns redo/undo actions
        '''
        if self.is_reset_pieces:
            self.is_reset_pieces = False
            return [self.mark_is_reset_pieces_action[:]]
        return []
    def _disturb_portals(self):
        '''called whenever portals are modified;
        sets is_reset_portals to False
        Returns redo/undo actions
        '''
        if self.is_reset_portals:
            self.is_reset_portals = False
            return [self.mark_is_reset_portals_action[:]]
        return []

    def reset_pieces(self):
        '''Reset pieces and black holes (back to starting pos)
        Caller responsible for adding to undo stack'''
        #list of pieces (piece -> position)
        self.pieces = []
        size = self.board.size_in_sq
        for i, typee in enumerate(self.piece_layout):
            #back row
            self.pieces.append([typee, 1, i, size-1, True, False])
            self.pieces.append([typee, 2, i, 0,  True, False])
            #pawns
            self.pieces.append([0, 1, i, size-2, True, False])
            self.pieces.append([0, 2, i, 1,  True, False])
        #dict: self.piece_at[3-position] = piece_index
        self.piece_at = self.generate_piece_at(self.pieces, self.portals)
        #heaven management
        self.white_heaven_next_place = self.white_heaven_ordering.first()
        self.black_heaven_next_place = self.black_heaven_ordering.first()
        #reset black holes
        for black_hole_square in self.black_holes:
            del self._env_at[black_hole_square]
        self.black_holes = []
        #mark that we are reset
        self.is_reset_pieces = True
    def reset_portals(self):
        '''Caller responsible for adding to undo stack'''
        for group in self.portals:
            for sq in group:
                del self._env_at[sq]
        self.portals = [[] for i in range(len(self.portal_cols))]
        self.is_reset_portals = True
    def is_reset_all(self):
        return self.is_reset_pieces and self.is_reset_portals

    @staticmethod
    def generate_piece_at(pieces, portals):
        #dict: self.piece_at[3-position] = piece_index
        piece_at = {}
        portal_colour_at = {}
        for i, group in enumerate(portals):
            for sq in group:
                portal_colour_at[sq] = i
        for i, piece in enumerate(pieces):
            loc = PieceHandler.get_loc_from_piece(piece)
            piece_at[loc] = i
            if loc[0] == PieceHandler.PLACE_I_BOARD and loc[1:] in portal_colour_at:
                group = portals[portal_colour_at[loc[1:]]]
                for sq in group:
                    piece_at[(0, *sq)] = i
        return piece_at
    @staticmethod
    def generate_env_at(black_holes, portals):
        #dict: self._env_at[2-position on board] = tuple describing env obj
        _env_at = {}
        for sq in black_holes:
            _env_at[sq] = (1,)
        for i, group in enumerate(portals):
            for sq in group:
                _env_at[sq] = (2,i)
        return _env_at
    @staticmethod
    def get_loc_from_piece(piece):
        #place_i: 0 is board, 1 is white heaven, 2 is black heaven
        place_i = 0 if piece[4] else piece[1]
        return (place_i, piece[2], piece[3])

    @staticmethod
    def _duplicate_state(pieces, black_holes, portals,
                        white_heaven_next_place, black_heaven_next_place):
        #deepcopy all objects
        pieces_ = [p[:] for p in pieces]
        black_holes_ = black_holes[:]
        portals_ = [p[:] for p in portals]
        return (pieces_, black_holes_, portals_,
                white_heaven_next_place, black_heaven_next_place)
    def copy_state(self):
        return self._duplicate_state(self.pieces,
                self.black_holes, self.portals,
                self.white_heaven_next_place, self.black_heaven_next_place)
    @staticmethod
    def format_state_as_dict(state):
        '''For converting to json'''
        d = {}
        d['pieces'] = state[0]
        d['black_holes'] = state[1]
        d['portals'] = state[2]
        d['white_heaven_next_place'] = state[3]
        d['black_heaven_next_place'] = state[4]
        return d
    @staticmethod
    def state_from_dict(d):
        '''For loading from json'''
        return (d['pieces'],
                d['black_holes'],
                d['portals'],
                d['white_heaven_next_place'],
                d['black_heaven_next_place'])
    def restore_state(self, pieces, black_holes, portals,
                      white_heaven_next_place, black_heaven_next_place):
        '''Caller responsible for adding to undo stack'''
        #ensure we have tuples where they will be used as keys for env_at
        bholes = [tuple(sq) for sq in black_holes]
        portals = [[tuple(sq) for sq in group] for group in portals]
        self.pieces = pieces
        self.piece_at = self.generate_piece_at(pieces, portals)
        self.black_holes = bholes
        self.portals = portals
        self._env_at = self.generate_env_at(bholes, portals)
        self.white_heaven_next_place = white_heaven_next_place
        self.black_heaven_next_place = black_heaven_next_place
        #assume position is not the default pos (could check but meh)
        self.is_reset_pieces = self.is_reset_portals = False

    def add_piece(self, piece_type, colour, loc, is_being_dragged=False):
        '''piece_type is an integer, colour is 1 for white or 2 for black,
        loc is (place_i, sq_x, sq_y)
        Assumes square is within bounds & there isn't a piece already there
        Returns undo/redo action'''
        loc = tuple(loc)
        square = loc[1:]
        i = len(self.pieces) #will be index of new piece
        #add to piece_at
        self._add_to_piece_at(loc, i)
        #add to pieces
        alive = (loc[0] == 0)
        self.pieces.append([piece_type, colour, loc[1], loc[2], alive,
                            is_being_dragged])
        undo_actions = [['add_piece', (piece_type, colour, loc, is_being_dragged),
                         'remove_piece', (loc,)]]
        undo_actions.extend(self._disturb_pieces())
        return undo_actions
    def remove_piece(self, loc):
        '''loc is (place_i, sq_x, sq_y)
        Piece can be removed from board or from either heaven
        Assumes that square is valid and there is a piece there
        Returns undo/redo action'''
        #Note: state will not be perfectly restored of you remove a piece
        # which does not have the last index, then undo. This is because the
        # indices of the other pieces are shifted down, and on undo the piece
        # you removed is added back on the end. However the new state will be
        # functionally the same, only with a different numbering of the pieces
        loc = tuple(loc)
        i = self.piece_at[loc]
        piece = self.pieces[i]
        #remove from piece_at
        self._remove_from_piece_at(loc)
        #adjust indices greater than this piece in piece_at
        if i < len(self.pieces) - 1:
            for sq in self.piece_at:
                if self.piece_at[sq] > i:
                    self.piece_at[sq] -= 1
        #remove from pieces
        self.pieces.pop(i)
        undo_actions = [['remove_piece', (loc,),
                         'add_piece', (piece[0], piece[1], loc)]]
        #move up other dead pieces if removing from heaven
        if loc[0] != 0:
            undo_actions.extend(self._move_up_dead_pieces(loc))
        undo_actions.extend(self._disturb_pieces())
        return undo_actions
    def change_piece_type(self, piece_index, new_type):
        '''Changes type of a piece, keeps colour the same (eg pawn->queen)
        Assumes piece_index and new_type are valid
        Returns redo/undo action'''
        piece = self.pieces[piece_index]
        current_type = piece[0]
        piece[0] = new_type
        undo_actions [['change_piece_type', (piece_index, new_type),
                       'change_piece_type', (piece_index, current_type)]]
        undo_actions.extend(self._disturb_pieces())
        return undo_actions
    def move_piece(self, piece_index, loc_to, loc_from=None):
        '''sq_from and sq_to are triples of numbers as in piece_at
        Assumes this is a valid move (wont check if there is another piece
        there, or for black piece going into white heaven etc)
        Sets piece[4] (is_alive) based on where moved to
        If moved out of heaven will move up rest of pieces
        If sq_from is not specified it will be worked out from piece
        Return redo/undo actions'''
        piece = self.pieces[piece_index]
        loc_to = tuple(loc_to)
        if loc_from is None:
            loc_from = self.get_loc_from_piece(piece)
        else:
            loc_from = tuple(loc_from)
        #modify piece_at
        self._remove_from_piece_at(loc_from)
        self._add_to_piece_at(loc_to, piece_index)
        #modify square coords in piece
        piece[2], piece[3] = loc_to[1], loc_to[2]
        #set is_alive based on where moved to
        if loc_to[0] != 0:
            piece[4] = False
        else:
            piece[4] = True
        undo_actions = [['move_piece', (piece_index, loc_to, loc_from),
                         'move_piece', (piece_index, loc_from, loc_to)]]
        #piece has been moved: probably not default layout (could check but meh)
        #therefore set self.is_reset_pieces = False
        #and add corresponding undo action if reqd
        undo_actions.extend(self._disturb_pieces())
        #move up dead pieces (to fill gap when dead piece is moved back out of heaven)
        if self.mode == 0 and loc_from[0] != 0 and loc_to[0] == 0:
            undo_actions.extend(self._move_up_dead_pieces(loc_from))
        return undo_actions
    def kill_piece(self, piece_index, loc_from=None):
        '''Return redo/undo actions'''
        if loc_from is None:
            loc_from = self.get_loc_from_piece(self.pieces[piece_index])
        else:
            loc_from = tuple(loc_from)
        if self.pieces[piece_index][1] == 1: #white piece
            new_sq = self.white_heaven_next_place
            if new_sq is None:
                return [] #if no more space, just don't do anything
            self.white_heaven_next_place = self.white_heaven_ordering.next(new_sq)
        else: #black piece
            new_sq = self.black_heaven_next_place
            if new_sq is None:
                return [] #if no more space, just don't do anything
            self.black_heaven_next_place = self.black_heaven_ordering.next(new_sq)
        new_loc = (self.pieces[piece_index][1], *new_sq)
        self.move_piece(piece_index, new_loc, loc_from)
        return [['kill_piece', (piece_index, loc_from),
                 'move_piece', (piece_index, loc_from, new_loc)]]
    def kill_piece_at_pos(self, pos):
        '''If there is a piece on the board at these coords in window, kill it
        Returns redo/undo actions'''
        if self.board.contains_coords(pos):
            sq_x, sq_y = self.board.square_at(pos)
            loc = (0, sq_x, sq_y)
            try:
                piece_i = self.piece_at[loc]
                return self.kill_piece(piece_i, sq_from=loc)
            except KeyError:
                pass
        return []
    def _add_to_piece_at(self, loc, piece_i):
        '''Add piece of index piece_i to piece_at,
        adding duplicate entries for portals
        loc is (place_i, sq_x, sq_y)'''
        if (loc[0] == 0 and
            (portal_group_id := self.portal_at(loc[1:])) is not None):
            for sq in self.portals[portal_group_id]:
                self.piece_at[(0,*sq)] = piece_i
        else:
            self.piece_at[loc] = piece_i
    def _remove_from_piece_at(self, loc):
        '''Remove piece at location loc from piece_at,
        removing duplicate entries for portals
        loc is (place_i, sq_x, sq_y)
        Assumes that there is a piece at loc,
        and that piece_at is updated correctly'''
        if (loc[0] == 0 and
            (portal_group_id := self.portal_at(loc[1:])) is not None):
            for sq in self.portals[portal_group_id]:
                del self.piece_at[(0,*sq)]
        else:
            del self.piece_at[loc]
    def _move_up_dead_pieces(self, removed_piece_loc):
        '''Return redo/undo action'''
        undo_actions = []
        place_i = removed_piece_loc[0]
        assert place_i in (1, 2), 'removed_piece_loc should be in a heaven'
        if place_i == 1:
            ordering = self.white_heaven_ordering
            if self.white_heaven_next_place is None:
                #heaven is full
                last_square = ordering.last()
                self.white_heaven_next_place = last_square
            else:
                last_square = self.white_heaven_next_place
                last_square = ordering.previous(last_square)
                self._move_up_white_heaven()
            undo_actions.append(['pass', (),
                                 '_move_down_white_heaven', ()])
        elif place_i == 2:
            ordering = self.black_heaven_ordering
            if self.black_heaven_next_place is None:
                #heaven is full
                last_square = ordering.last()
                self.black_heaven_next_place = last_square
            else:
                last_square = self.black_heaven_next_place
                last_square = ordering.previous(last_square)
                self._move_up_black_heaven()
            undo_actions.append(['pass', (),
                                 '_move_down_black_heaven', ()])
        piece_square = removed_piece_loc[1:]
        #last square is constant while piece_square is modified in this loop
        while last_square != piece_square:
            next_sq = ordering.next(piece_square)
            loc = (place_i, *piece_square)
            next_loc = (place_i, *next_sq)
            undo_actions.append(
                ['pass', (),
                 'move_piece', (self.piece_at[next_loc], next_loc, loc)]
            )
            self.move_piece(self.piece_at[next_loc], loc, next_loc)
            piece_square = next_sq
        return undo_actions
    def _move_up_white_heaven(self):
        self.white_heaven_next_place = \
            self.white_heaven_ordering.previous(self.white_heaven_next_place)
    def _move_down_white_heaven(self):
        self.white_heaven_next_place = \
            self.white_heaven_ordering.next(self.white_heaven_next_place)
    def _move_up_black_heaven(self):
        self.black_heaven_next_place = \
            self.black_heaven_ordering.previous(self.black_heaven_next_place)
    def _move_down_black_heaven(self):
        self.black_heaven_next_place = \
            self.black_heaven_ordering.next(self.black_heaven_next_place)

    def black_hole_at(self, square):
        '''Returns whether there is a black hole at square (2-coords)'''
        return tuple(square) in self.black_holes
    def set_black_hole(self, square):
        '''square is (sq_x, sq_y)
        Return redo/undo actions'''
        square = tuple(square)
        if square not in self.black_holes:
            self.black_holes.append(square)
        self._env_at[square] = (1,)
        undo_actions = [['set_black_hole', (square,),
                         'remove_black_hole', (square,)]]
        undo_actions.extend(self._disturb_pieces())
        return undo_actions
    def remove_black_hole(self, square):
        '''square is (sq_x, sq_y)
        Return redo/undo actions'''
        square = tuple(square)
        undo_actions = []
        if square in self.black_holes:
            self.black_holes.remove(square)
            del self._env_at[square]
            undo_actions.append(['remove_black_hole', (square,),
                                 'set_black_hole', (square,)    ])
        undo_actions.extend(self._disturb_pieces())
        return undo_actions
    def select_portal_col(self, col):
        self.selected_portal_col = col
    def portal_at(self, square):
        '''Returns colour (int) of portal at square, or None
        square is (sq_x, sq_y)'''
        square = tuple(square)
        if square in self._env_at:
            if self._env_at[square][0] == 2:
                return self._env_at[square][1]
        return None
    def set_portal(self, square, colour):
        '''square is (sq_x, sq_y)
        colour (int) is the index of the portal group
        Return redo/undo actions'''
        square = tuple(square)
        if square not in self.portals[colour]:
            #if already piece on that colour, put it here as well
            if self.portals[colour]:
                other_loc = (0,*self.portals[colour][0])
                if other_loc in self.piece_at:
                    self.piece_at[(0,*square)] = self.piece_at[other_loc]
            self.portals[colour].append(square)
        self._env_at[square] = (2, colour)
        undo_actions = [['set_portal', (square, colour),
                         'remove_portal', (square,)]]
        undo_actions.extend(self._disturb_portals())
        return undo_actions
    def remove_portal(self, square):
        '''square is (sq_x, sq_y)
        Return redo/undo actions'''
        square = tuple(square)
        if (col := self.portal_at(square)) is not None:
            del self._env_at[square]
        self.portals[col].remove(square)
        #if was piece standing on this square, and was duplicate due to portal,
        #remove it from piece_at
        if (0, *square) in self.piece_at and self.portals[col]:
            del self.piece_at[(0, *square)]
        undo_actions = [['remove_portal', (square,),
                         'set_portal', (square,col)]]
        undo_actions.extend(self._disturb_portals())
        return undo_actions

    def contains_coords(self, pos):
        #THIS IS SLIGHTLY JANKY, it works as long as there is nothing
        # else in the window apart from the app as i wrote it
        #The piece handler manages all clicking and dragging of pieces,
        # so its reach covers the board, as well as the areas for dead pieces
        return pos[1] > self.window_layout.top_bar_height

    def _start_dragging(self, piece_i, place, loc, mouse_pos):
        self.drag_piece_index = piece_i
        self.drag_piece = self.pieces[piece_i]
        self.drag_piece[5] = True #is_being_dragged
        self.drag_loc_from = loc
        #work out offset of piece image from mouse pos
        #(to make things smooth)
        sq_top_left = place.coords_of(loc[1:])
        piece_type = self.drag_piece[0]
        x_offset = (sq_top_left[0] - mouse_pos[0]
                    + self.piece_types[piece_type][3])
        y_offset = (sq_top_left[1] - mouse_pos[1]
                    + self.piece_types[piece_type][4])
        self.drag_offset = (x_offset, y_offset)
        self.drag_mouse_pos = mouse_pos
    def _stop_drag(self):
        self.drag_piece[5] = False
        self.drag_piece = None
        self.drag_piece_index = None
        self.drag_loc_from = None
        self.drag_offset = None
        self.drag_mouse_pos = None
        self.actions_on_drop = []

    def on_click(self, pos):
        undo_actions = []
        place = None
        place_i = None
        if self.board.contains_coords(pos):
            place = self.board
            place_i = 0
        elif self.white_heaven.contains_coords(pos):
            place = self.white_heaven
            place_i = 1
        elif self.black_heaven.contains_coords(pos):
            place = self.black_heaven
            place_i = 2
        if self.mode == 0 and place is not None:
            #MODE 0 : MOVE PIECES
            piece_square = place.square_at(pos)
            loc = (place_i, *piece_square)
            try: #if there is a piece here
                piece_i = self.piece_at[loc]
                self._start_dragging(piece_i, place, loc, pos)
            except KeyError:
                pass #do nothing if no piece is in that square
        elif self.mode == 1 and place_i == 0:
            #MODE 1 : EDIT BLACK HOLES
            square = self.board.square_at(pos)
            #Toggle black hole at this square
            #Note black hole & portal cant share square
            #so if there is a portal here, remove portal and place bhole
            #if there are only two portals of that colour, remove both
            if self.black_hole_at(square):
                undo_actions.extend(self.remove_black_hole(square))
            elif (portal_col := self.portal_at(square)) is not None:
                undo_actions.extend(self.remove_portal(square))
                if len(self.portals[portal_col]) == 1:
                    sq = self.portals[portal_col][0]
                    undo_actions.extend(self.remove_portal(sq))
                undo_actions.extend(self.set_black_hole(square))
            else:
                undo_actions.extend(self.set_black_hole(square))
        elif self.mode == 2:
            #MODE 2 : EDIT PORTALS
            if place_i == 0:
                #on board: toggle portal in this pos
                #unless black hole or piece is there
                square = self.board.square_at(pos)
                if not (self.black_hole_at(square) or (0,*square) in self.piece_at):
                    if (portal_col := self.portal_at(square)) is not None:
                        undo_actions.extend(self.remove_portal(square))
                    else:
                        sel_col = self.selected_portal_col
                        undo_actions.extend(self.set_portal(square, sel_col))
            elif place is self.right_heaven:
                #in right heaven:
                # select different portal col
                square = place.square_at(pos)
                try:
                    new_col = self.portal_col_at[square]
                    if new_col != self.selected_portal_col:
                        undo_actions.append(
                            ['select_portal_col', (new_col,),
                             'select_portal_col', (self.selected_portal_col,)] )
                        self.selected_portal_col = new_col
                except KeyError:
                    pass
        elif self.mode == 3:
            #MODE 3: edit pieces
            if place_i == 0:
                #pick up a piece on the board to move it, or remove it
                # if it is then dropped in heaven
                square = self.board.square_at(pos)
                loc = (0, square[0], square[1])
                try:
                    piece_i = self.piece_at[loc]
                    self._start_dragging(piece_i, place, loc, pos)
                except KeyError:
                    pass
            else:
                #pick new piece up from rack (which is in each heaven)
                ordering = (self.white_heaven_ordering if place_i == 1
                            else self.black_heaven_ordering)
                square = place.square_at(pos)
                piece_type = ordering.index(square)
                if piece_type < len(self.piece_types):
                    #some location juggling so that redo/undo works correctly
                    piece_loc = (place_i, -1, -1)
                    drag_from_loc = (place_i, *square)
                    piece_i = len(self.pieces)
                    self.add_piece(piece_type, place_i, piece_loc)
                    self._start_dragging(piece_i, place, drag_from_loc, pos)
                    self.drag_loc_from = piece_loc
        if undo_actions:
            self.add_undo(undo_actions)
    def on_drag(self, pos):
        self.drag_mouse_pos = pos
    def on_drop(self, pos):
        if self.drag_piece_index is not None:
            undo_actions = []
            drag_piece_i = self.drag_piece_index
            loc_from = self.drag_loc_from
            moved = False
            #check on board
            if self.board.contains_coords(pos):
                #Code here works for both mode 0 and mode 3
                # (normal moves, and editing pieces)
                # The difference is that in mode 3, we only accept moves
                # onto the board - either pieces already on the board, or
                # 'dead' pieces, onto empty squares
                # (since the code in on_click creates new pieces with
                # sq_from being in heaven). In mode 0 meanwhile, any piece can
                # be moved onto any empty square, and a piece on the board can
                # additionally take a piece of the opposite colour, or be
                # killed by moving it into heaven
                loc_to = (0, *self.board.square_at(pos))
                #If there isn't a piece on this square:
                if loc_to not in self.piece_at:
                    if self.mode == 0 or (self.mode == 3 and self.drag_piece[4]):
                        #move piece
                        undo_actions.extend(
                            self.move_piece(drag_piece_i, loc_to, loc_from))
                        moved = True
                    else:
                        #mode 3 and piece is 'dead' - ie new
                        #move piece but redo/undo action has to be adding a piece
                        self.move_piece(drag_piece_i, loc_to, loc_from)
                        undo_actions.append([
                            'add_piece', (self.drag_piece[0], self.drag_piece[1], loc_to),
                            'remove_piece', (loc_to,)
                        ])
                        moved = True
                elif self.mode == 0:
                    #piece already there, and we are in mode 0
                    #If coming from heaven do nothing: dead piece cant take live piece
                    #If coming from board, take the piece that's there
                    # We can tell if a piece was dead because we didn't change
                    # piece[4] on pickup or drag
                    if self.drag_piece[4]: #alive
                        piece_there = self.pieces[self.piece_at[loc_to]]
                        if self.drag_piece[1] != piece_there[1]:
                            #dragged piece alive and different colour: take
                            kill_actions = self.kill_piece(self.piece_at[loc_to], loc_to)
                            if kill_actions: #if heaven is full, kill_piece will do nothing
                                undo_actions.extend(kill_actions)
                                undo_actions.extend(
                                    self.move_piece(drag_piece_i, loc_to, loc_from)
                                )
                                moved = True
                        #dragged piece alive and same colour: do nothing
                    else: #dragged piece dead: return to where it came from
                        pass # ie do nothing
            elif (self.white_heaven.contains_coords(pos) or
                  self.black_heaven.contains_coords(pos)):
                #if piece wasn't already dead to begin with
                if self.drag_piece[4]:
                    if self.mode == 0:
                        #normal mode. kill piece if moved into heaven
                        undo_actions.extend(self.kill_piece(drag_piece_i, loc_from))
                    elif self.mode == 3:
                        #edit pieces mode. delete piece if moved into heaven
                        undo_actions.extend(self.remove_piece(loc_from))
                    moved = True
                #edit pieces mode, and piece was a new one taken from heaven
                elif self.mode == 3:
                    #need to delete this piece, as we created it pre-emptively
                    #in on_click so it could be dragged onto the board
                    #See self.clean_state()
                    assert self.drag_piece_index == len(self.pieces) - 1
                    del self.piece_at[loc_from]
                    del self.pieces[-1]
            else: #piece not dropped on board, or in either heaven
                if self.mode == 3:
                    #need to delete this piece, as we created it pre-emptively
                    #in on_click so it could be dragged onto the board
                    #See self.clean_state()
                    assert self.drag_piece_index == len(self.pieces) - 1
                    del self.piece_at[self.drag_loc_from]
                    del self.pieces[-1]
            if moved:
                #currently not used, but allows for extra actions to happen
                # once a piece is dropped
                while self.actions_on_drop:
                    action = self.actions_on_drop.pop()
                    action[0](*action[1])
                    undo_actions.extend(action)
            self._stop_drag()
            if undo_actions:
                self.add_undo(undo_actions)

    def draw(self):
        #draw environment first: portals then black holes
        for cols, portal_group in zip(self.portal_cols, self.portals):
            for portal_sq in portal_group:
                colour = cols[sum(portal_sq) % 2] #different colour for black/white sq
                top_left = self.board.coords_of(portal_sq)
                pygame.draw.rect(self.window, colour,
                                 self.get_board_sq_rect(top_left))
        for black_hole_sq in self.black_holes:
            top_left = self.board.coords_of(black_hole_sq)
            pygame.draw.rect(self.window, self.black_hole_col,
                             self.get_board_sq_rect(top_left))
        #draw all the pieces on the board
        #use piece_at so that we can draw duplicates on portals
        for loc in self.piece_at:
            piece = self.pieces[self.piece_at[loc]]
            if not piece[5]: #if not being dragged
                if piece[4]: #alive (on board)
                    #window coords of square piece is on
                    x, y = self.board.coords_of(loc[1:])
                else: #dead (in heaven)
                    heaven = self.white_heaven if piece[1]==1 else self.black_heaven
                    x, y = heaven.coords_of(loc[1:])
                #dont draw dead pieces if editing portals/pieces
                if piece[4] or (self.mode not in (2, 3)):
                    img = self.piece_types[piece[0]][piece[1]]
                    #add offsets so piece is centered in square
                    x += self.piece_types[piece[0]][3]
                    y += self.piece_types[piece[0]][4]
                    self.window.blit(img, (x,y))
        #if editing portals: draw portal colour selection
        if self.mode == 2:
            sq = self.right_heaven_ordering.first()
            sq_size = self.right_heaven.square_size
            for i, col in enumerate(self.portal_cols):
                pos = self.right_heaven.coords_of(sq)
                if i == self.selected_portal_col:
                    pygame.draw.rect(self.window, '#ff0000',
                                     (pos[0], pos[1], sq_size, sq_size))
                pygame.draw.rect(self.window, col[0],
                                 (pos[0]+7, pos[1]+7, sq_size-14, sq_size-14))
                sq = self.right_heaven_ordering.next(sq)
        #if editing pieces: draw piece selection
        if self.mode == 3:
            heavens = (self.white_heaven, self.black_heaven)
            orderings = (self.white_heaven_ordering, self.black_heaven_ordering)
            cols = (1, 2)
            for col, heaven, ordering in zip(cols, heavens, orderings):
                sq = ordering.first()
                for piece_type in self.piece_types:
                    x, y = heaven.coords_of(sq)
                    img = piece_type[col]
                    x += piece_type[3]
                    y += piece_type[4]
                    self.window.blit(img, (x, y))
                    sq = ordering.next(sq)
        #draw piece being dragged last so is on top
        if self.drag_piece_index is not None:
            img = self.piece_types[self.drag_piece[0]][self.drag_piece[1]]
            x = self.drag_mouse_pos[0] + self.drag_offset[0]
            y = self.drag_mouse_pos[1] + self.drag_offset[1]
            self.window.blit(img, (x,y))
            

    def clean_state(self):
        '''Returns to a state where there is nothing being dragged
        (equivalent to releasing the mouse pointer outside the window)
        Call this function before undo/redo/save'''
        if self.drag_piece_index is not None:
            if self.mode == 3 and not self.drag_piece[4]:
                #if editing pieces and in process of adding a piece,
                # we pre-emptively create a new piece to drag in.
                # Since this piece hasn't really been added to the board yet,
                # we need to remove it from self.pieces again
                #This piece should have just been added so should be the last
                assert self.drag_piece_index == len(self.pieces) - 1
                #bypassing self.remove_piece(loc) since we know exactly
                # where everything is
                del self.piece_at[self.drag_loc_from]
                self._stop_drag()
                del self.pieces[-1]
            else:
                self._stop_drag()


#-------------------------------------------------------------------------------

class UndoStack:
    MAX_STACK_LEN = 300 #prevent excessive memory leakage
    
    #A naming system is used rather than storing function pointers directly
    #name_to_func is populated by the App calling add_func for each function
    # it intends to potentially use in the undo stack
    #This is so that the undo stack can be easily serialized into json
    # when saving a game
    name_to_func = {'pass':(lambda:None)}
    def add_func(self, name, func):
        '''A second call with same `name` will overwrite the first'''
        UndoStack.name_to_func[name] = func

    def __init__(self, stack = [], index = -1):
        '''Optional arguments intended for loading undo stack from savefile'''
        self.stack = stack
        self.index = index
    def can_undo(self):
        return self.index >= -len(self.stack)
    def can_redo(self):
        return self.index < -1
    def add(self, actions):
        '''actions is list of (func_name, args, unfunc_name, unargs) tuples
        (Because one 'action' can involve multiple function calls)
        Undo results in calling
            UndoStack.name_to_func[unfunc_name](*unargs)
            for each action in reverse order
        Redo results in calling
            UndoStack.name_to_func[func_name](*args)
            for each action in order
        Keyword arguments are not currently supported'''
        #truncate after current index
        del self.stack[(len(self.stack) + self.index + 1):]
        self.stack.append(actions)
        self.index = -1
        #prevent excessive memory leakage
        if len(self.stack) > UndoStack.MAX_STACK_LEN:
            self.stack.pop(0)
    def undo(self):
        if self.can_undo():
            for action in reversed(self.stack[self.index]):
                self.name_to_func[action[2]](*action[3])
            self.index -= 1
    def redo(self):
        if self.can_redo():
            self.index += 1
            for action in self.stack[self.index]:
                self.name_to_func[action[0]](*action[1])

# Puts the various elements together into a single-window application
class App:
    class SavegameError(Exception):
        pass
    def __init__(self, window, settings, window_layout,
                 piece_layout):
        self.undo_stack = UndoStack()
        self.window_layout = window_layout
        self.window = window
        self.settings = settings

        self.window_objects = []
        heaven_width_sq, heaven_height_sq = window_layout.get_heaven_size_in_sq()
        self.left_heaven = PieceHeaven(
            window, *window_layout.get_left_heaven_coords(),
            window_layout.square_size,
            heaven_width_sq, heaven_height_sq, settings.heaven_col_str
        )
        self.board = Board(
            window, *window_layout.get_board_coords(),
            window_layout.board_size_in_sq,
            window_layout.square_size,
            settings
        )
        self.right_heaven = PieceHeaven(
            window, *window_layout.get_right_heaven_coords(),
            window_layout.square_size,
            heaven_width_sq, heaven_height_sq, settings.heaven_col_str
        )
        self.piece_handler = PieceHandler(
            window, window_layout, self.board,
            self.left_heaven, self.right_heaven,
            settings.img_path, piece_layout,
            settings.portal_cols, settings.bhole_col_str,
            self, 'piece_handler'
        )
        #putting zeroes for location and size because they will be
        #automatically calculated using functions from self.window_layout
        #when self.add_button is called
        self.quit_btn = ToggleButton(
            window, 0, 0, 0, 0,
            '#ff8888', 'black', '#ee7777', 'black', window_layout.font,
            'Quit', self.press_quit, 'Sure?', self.send_quit_signal
        )
        self.reset_btn = Button(
            window, 0, 0, 0, 0,
            '#ff8888', 'black', '#ee7777', 'black', window_layout.font,
            'Reset game', self.reset_game
        )
        self.save_btn = MultiButton(
            window, 0, 0, 0, 0,
            4,
            4*('#8888ff',), 4*('black',), 4*('#7777ee',), 4*('black',),
            window_layout.font, ('Save game', 'Saving...', 'Saved!', 'Stashed!'),
            (self.save_game, lambda:None, lambda:None, lambda:None),
            (1, 1, 0, 0)
        )
        self.open_savegame_btn = MultiButton(
            window, 0, 0, 0, 0,
            4,
            4*('#8888ff',), 3*('black',)+('red',),
            4*('#7777ee',), 3*('black',)+('red',),
            window_layout.font, ('Open game', 'Opening...', 'Done!', 'Error'),
            (self.open_saved_game, lambda:None, lambda:None, lambda:None),
            (1, 1, 0, 0)
        )
        self.undo_btn = MultiButton( #two states, 0=disabled, 1=enabled
            window, 0, 0, 0, 0,
            2,
            ('#cccccc','#88ff88'), ('#888888','black'),
            ('#cccccc','#77ee77'), ('#888888','black'),
            window_layout.font, ('Undo', 'Undo'), (lambda:None, self.undo),
            (0, 1)
        )
        self.redo_btn = MultiButton( #two states, 0=disabled, 1=enabled
            window, 0, 0, 0, 0,
            2,
            ('#cccccc','#88ff88'), ('#888888','black'),
            ('#cccccc','#77ee77'), ('#888888','black'),
            window_layout.font, ('Redo', 'Redo'), (lambda:None, self.redo),
            (0, 1)
        )
        self.black_hole_btn = ToggleButton(
            window, 0, 0, 0, 0,
            '#888888', 'black', '#777777', 'black', window_layout.font,
            'Edit black holes', self.edit_black_holes,
            'Done', self.done_editing
        )
        self.portal_btn = ToggleButton(
            window, 0, 0, 0, 0,
            '#ff99ff', 'black', '#ee88ee', 'black', window_layout.font,
            'Edit portals', self.edit_portals,
            'Done', self.done_editing
        )
        self.reset_portals_btn = Button(
            window, 0, 0, 0, 0,
            '#ff99ff', 'black', '#ee88ee', 'black', window_layout.font,
            'Reset portals', self.reset_portals
        )
        self.edit_pieces_btn = ToggleButton(
            window, 0, 0, 0, 0,
            '#ffffff', 'black', '#eeeeee', 'black', window_layout.font,
            'Edit pieces', self.edit_pieces,
            'Done', self.done_editing
        )
##        self.add_button(self.quit_btn, 'quit_btn', loc='left')
        self.add_button(self.reset_btn, 'reset_btn',                 loc='left')
        self.add_button(self.save_btn, 'save_btn',                   loc='left')
        self.add_button(self.open_savegame_btn, 'open_savegame_btn', loc='left')
        self.add_button(self.undo_btn, 'undo_btn',                   loc='middle')
        self.add_button(self.redo_btn, 'redo_btn',                   loc='middle')
##        self.add_button(self.reset_portals_btn, 'reset_portals_btn', loc='right')
        self.add_button(self.portal_btn, 'portal_btn',               loc='right',
                        add_undo_funcs=True)
        self.add_button(self.black_hole_btn, 'black_hole_btn',       loc='right',
                        add_undo_funcs=True)
        self.add_button(self.edit_pieces_btn, 'edit_pieces_btn',     loc='right',
                        add_undo_funcs=True)
        self.window_objects.append(self.board)
        self.window_objects.append(self.left_heaven)
        self.window_objects.append(self.right_heaven)
        self.window_objects.append(self.piece_handler)

        #for user interaction in mainloop
        self.dragged_obj = None
        #special code for quit button:
        #have to click it twice to close the app
        #if you click it once and then click somewhere else/press a key,
        # it resets
        self.quit_stage = 0

        for name, func in self.piece_handler.get_undo_able_funcs():
            self.undo_stack.add_func('piece_handler.'+name, func)

        #[time_left_ms, callable, arguments]
        #time_left_ms milliseconds after action added, =
        # callable(*arguments) will be executed
        self.delayed_actions = []

        self.quitting = False

    def add_button(self, button, name, loc, add_undo_funcs=False):
        self.window_layout.add_button(button, loc)
        self.window_objects.append(button)
        if add_undo_funcs:
            self.undo_stack.add_func(name+'.show', button.show)
            self.undo_stack.add_func(name+'.hide', button.hide)
            self.undo_stack.add_func(name+'.toggle_state', button.toggle_state)
            self.undo_stack.add_func(name+'.set_state', button.set_state)
            self.undo_stack.add_func(name+'.reset_state', button.reset_state)

    def add_to_undo_stack(self, actions, caller_name):
        '''(actions : Iterable of actions, caller_name : str) -> None
        Each action is a 4-list (or equivalent mutable structure) as in UndoStack'''
        if caller_name:
            for action in actions:
                if action[0] != 'pass':
                    action[0] = caller_name + '.' + action[0]
                if action[2] != 'pass':
                    action[2] = caller_name + '.' + action[2]
        #TODO: Add undo elision / auto undo code
        self.undo_stack.add(actions)
        self.undo_btn.set_state(1) #enable undo btn
        self.redo_btn.set_state(0) #disable redo btn - we are now at front of stack
    def undo(self):
        self.piece_handler.clean_state()
        self.undo_stack.undo()
        if not self.undo_stack.can_undo():
            #disable undo btn if at bottom of stack
            #since this function can be called on pressing the undo btn
            #we need to do this on the next frame
            self.delayed_actions.append([0, self.undo_btn.set_state, (0,)])
        if self.undo_stack.can_redo():
            self.redo_btn.set_state(1) #enable redo btn
    def redo(self):
        self.piece_handler.clean_state()
        self.undo_stack.redo()
        if not self.undo_stack.can_redo():
            #disable redo btn if at top of stack
            self.delayed_actions.append([0, self.redo_btn.set_state, (0,)])
        if self.undo_stack.can_undo():
            self.undo_btn.set_state(1) #enable undo btn

    def send_quit_signal(self):
        self.quitting = True
    def press_quit(self):
        self.quit_stage = 1
    def reset_portals(self):
        if not self.piece_handler.is_reset_portals:
            self.add_to_undo_stack( [
                ['piece_handler.reset_portals', (),
                 'piece_handler.restore_state', self.piece_handler.copy_state() ]
            ], '')
            self.piece_handler.reset_portals()
    def reset_game(self):
        undo = []
        if not self.piece_handler.is_reset_pieces:
            undo.append(
                ['piece_handler.reset_pieces', (),
                 'piece_handler.restore_state', self.piece_handler.copy_state() ]
            )
            self.piece_handler.reset_pieces()
        if self.piece_handler.mode != 0:
            undo.append(
                ['piece_handler.set_mode', (0,),
                 'piece_handler.set_mode', (self.piece_handler.mode,) ]
            )
            self.piece_handler.set_mode(0)
        if self.portal_btn.hidden:
            undo.append(
                ['portal_btn.show', (),
                 'portal_btn.hide', ()] )
            self.portal_btn.show()
        if self.black_hole_btn.hidden:
            undo.append(
                ['black_hole_btn.show', (),
                 'black_hole_btn.hide', ()] )
            self.black_hole_btn.show()
        if self.portal_btn.state == 1:
            undo.append(
                ['portal_btn.reset_state', (),
                 'portal_btn.set_state', (1,)] )
            self.portal_btn.reset_state()
        if self.black_hole_btn.state == 1:
            undo.append(
                ['black_hole_btn.reset_state', (),
                 'black_hole_btn.set_state', (1,)] )
            self.black_hole_btn.reset_state()
        if undo:
            self.add_to_undo_stack(undo, '')

    def save_game(self, filepath=None, stash=False):
        #no multithreading because it shouldn't take too long
        # (saving is done in main thread so pauses mainloop)
        if filepath is None:
            filepath = (self.settings.stash_path if stash
                        else self.settings.save_path)
        #build json state object, including game state and undo stack
        now = datetime.datetime.utcnow()
        datetime_readable = now.strftime('%a, %d %b %Y, %H:%M:%S UTC')
        self.piece_handler.clean_state()
        game_state = self.piece_handler.format_state_as_dict(
            self.piece_handler.copy_state()
        )
        undo_stack = {'stack':self.undo_stack.stack, 'index':self.undo_stack.index}
        save_object = {'game_state':game_state,
                       'undo_stack':undo_stack,
                       'ruleset':CURRENT_RULESET,
                       'savefile_format':CURRENT_SAVEFILE_FORMAT,
                       'board_size_in_sq':self.window_layout.board_size_in_sq,
                       'save_time':datetime_readable}
        #save
        with open(filepath, mode='w') as file:
            json.dump(save_object, file)
        if not stash: #maybe add `or verbose` when i implement logging properly...
            print('saved to < {} >'.format(filepath))
        #update save button to say 'Saved!' or 'Stashed!' on next frame
        new_state = 3 if stash else 2
        self.delayed_actions.append([0, self.save_btn.set_state, (new_state,)])
        #TODO: check for saving error
    def open_saved_game(self, filepath=None):
        if filepath is None:
            filepath = self.settings.open_path
        error = ''
        try:
            #load from savefile
            try:
                with open(filepath) as file:
                    save_object = json.load(file)
            except FileNotFoundError:
                error = 'No savefile found. Tried < {} >'
                error = error.format(filepath)
                raise App.SavegameError
            #check savefile format is compatible
            if save_object['savefile_format'] != CURRENT_SAVEFILE_FORMAT:
                error = 'Savefile has outdated format {}, expected {}'
                error = error.format(save_object['savefile_format'],
                                     CURRENT_SAVEFILE_FORMAT)
                raise App.SavegameError
            #check if game rules are compatible
            if save_object['ruleset'] != CURRENT_RULESET:
                print('Warning: game was last played using old ruleset')
            #check board size is the same : currently no way to change board
            # size while app is loaded (todo!)
            if save_object['board_size_in_sq'] != self.window_layout.board_size_in_sq:
                error = 'Savefile has incompatible board size {}'
                error = error.format(save_object['board_size_in_sq'])
                raise App.SavegameError
            #save current game into savefile so it is not lost
            if self.settings.stash_game:
                self.save_game(stash=True)
            #parse object into game state
            self.undo_stack.stack = save_object['undo_stack']['stack']
            self.undo_stack.index = save_object['undo_stack']['index']
            if self.undo_stack.can_undo():
                self.delayed_actions.append(
                    [0, self.undo_btn.set_state, (1,)]
                )
            if self.undo_stack.can_redo():
                self.delayed_actions.append(
                    [0, self.redo_btn.set_state, (1,)]
                )
            game_state = save_object['game_state']
            game_state = self.piece_handler.state_from_dict(game_state)
            self.piece_handler.restore_state(*game_state)
            #update button to say 'Done!' on next frame
            self.delayed_actions.append([0, self.open_savegame_btn.set_state, (2,)])
            #print info
            print('Loaded <', filepath, '> from', save_object['save_time'])
        except App.SavegameError:
            print('Error:', error)
            #update button to say 'Error' on next frame
            self.delayed_actions.append([0, self.open_savegame_btn.set_state, (3,)])


    def edit_black_holes(self):
        self.add_to_undo_stack(
        [
            ['piece_handler.set_mode', (1,),
             'piece_handler.set_mode', (self.piece_handler.mode,)
             ],
            ['black_hole_btn.set_state', (1,),
             'black_hole_btn.reset_state', (),
             ],
            ['portal_btn.hide', (),
             'portal_btn.show', ()
             ],
            ['edit_pieces_btn.hide', (),
             'edit_pieces_btn.show', ()
             ]
        ], '')
        self.piece_handler.set_mode(1)
        if not self.black_hole_btn.state:
            self.black_hole_btn.set_state(1)
        self.portal_btn.hide()
        self.edit_pieces_btn.hide()
    def edit_portals(self):
        self.add_to_undo_stack(
        [
            ['piece_handler.set_mode', (2,),
             'piece_handler.set_mode', (self.piece_handler.mode,)
             ],
            ['portal_btn.set_state', (1,),
             'portal_btn.reset_state', (),
             ],
            ['black_hole_btn.hide', (),
             'black_hole_btn.show', ()
             ],
            ['edit_pieces_btn.hide', (),
             'edit_pieces_btn.show', ()
             ]
        ], '')
        self.piece_handler.set_mode(2)
        if not self.portal_btn.state:
            self.portal_btn.set_state(1)
        self.black_hole_btn.hide()
        self.edit_pieces_btn.hide()
    def edit_pieces(self):
        self.add_to_undo_stack(
        [
            ['piece_handler.set_mode', (3,),
             'piece_handler.set_mode', (self.piece_handler.mode,)
             ],
            ['edit_pieces_btn.set_state', (1,),
             'edit_pieces_btn.reset_state', (),
             ],
            ['black_hole_btn.hide', (),
             'black_hole_btn.show', ()
             ],
            ['portal_btn.hide', (),
             'portal_btn.show', ()
             ]
        ], '')
        self.piece_handler.set_mode(3)
        if not self.edit_pieces_btn.state:
            self.edit_pieces_btn.set_state(1)
        self.black_hole_btn.hide()
        self.portal_btn.hide()
    def done_editing(self):
        undo = [
            ['piece_handler.set_mode', (0,),
             'piece_handler.set_mode', (self.piece_handler.mode,)
             ]
        ]
        if self.portal_btn.hidden:
            undo.append(
                ['portal_btn.show', (),
                 'portal_btn.hide', ()]
            )
        if self.black_hole_btn.hidden:
            undo.append(
                ['black_hole_btn.show', (),
                 'black_hole_btn.hide', ()]
            )
        if self.edit_pieces_btn.hidden:
            undo.append(
                ['edit_pieces_btn.show', (),
                 'edit_pieces_btn.hide', ()]
            )
        if self.portal_btn.state == 1:
            self.delayed_actions.append([0, self.portal_btn.set_state, (0,)])
            undo.append(
                ['portal_btn.toggle_state', (),
                 'portal_btn.toggle_state', ()]
            )
        if self.black_hole_btn.state == 1:
            self.delayed_actions.append([0, self.black_hole_btn.set_state, (0,)])
            undo.append(
                ['black_hole_btn.toggle_state', (),
                 'black_hole_btn.toggle_state', ()]
            )
        if self.edit_pieces_btn.state == 1:
            self.delayed_actions.append([0, self.edit_pieces_btn.set_state, (0,)])
            undo.append(
                ['edit_pieces_btn.toggle_state', (),
                 'edit_pieces_btn.toggle_state', ()]
            )
        self.add_to_undo_stack(undo,'')
        self.piece_handler.set_mode(0)
        self.portal_btn.show()
        self.black_hole_btn.show()
        self.edit_pieces_btn.show()

    def release_drag(self, obj):
        obj.is_being_clicked = False
        if self.dragged_obj is obj:
            self.dragged_obj = None
    def clear_temp_messages(self):
        #reset the quit button (you have to press it 2x in a row to close the game)
        if self.quit_stage:
            self.quit_stage = 0
            self.quit_btn.reset_state()
        #reset save and open buttons, if they are showing a success/error msg
        if self.save_btn.state in (2, 3):
            self.save_btn.set_state(0)
        if self.open_savegame_btn.state in (2, 3):
            self.open_savegame_btn.set_state(0)

    def on_keydown(self, key, ctrl, shift, alt, mouse_pos):
        self.clear_temp_messages()
        if (not (ctrl or shift or alt)): #no modifiers
            if key == K_k:
                #K : kill piece
                undo_actions = self.piece_handler.kill_piece_at_pos(mouse_pos)
                if undo_actions:
                    self.add_to_undo_stack(undo_actions, 'piece_handler')
            elif key == K_b:
                #B : edit black holes
                if self.piece_handler.mode == 0:
                    self.edit_black_holes()
                elif self.piece_handler.mode == 1:
                    self.done_editing()
                else:
                    self.done_editing()
                    self.edit_black_holes()
            elif key == K_p:
                #P : edit portals
                if self.piece_handler.mode == 0:
                    self.edit_portals()
                elif self.piece_handler.mode == 2:
                    self.done_editing()
                else:
                    self.done_editing()
                    self.edit_portals()
            elif key == K_i:
                #I : edit pieces
                if self.piece_handler.mode == 0:
                    self.edit_pieces()
                elif self.piece_handler.mode == 3:
                    self.done_editing()
                else:
                    self.done_editing()
                    self.edit_pieces()
            elif key == K_ESCAPE:
                #ESC : done editing / return to mode 0
                if self.piece_handler.mode != 0:
                    self.done_editing()
        elif (ctrl) and (not shift) and (not alt): #just CTRL
            if key == K_z:
                #CTRL-Z : undo
                self.undo()
            elif key == K_y:
                #CTRL-Y : redo
                self.redo()
            elif key == K_s:
                #CTRL-S : save
                self.save_game()
            elif key == K_o:
                #CTRL_O : open
                self.open_saved_game()
    def on_keyup(self, key, ctrl, shift, alt, mouse_pos):
        pass
    def on_mousedown(self, mouse_button, pos):
        #if temporary messages should be removed, clear_temp_messages
        # should be True. This could depend on where and how the user clicks
        #At the moment, any click will do
        clear_temp_messages = True
        if mouse_button == BUTTON_LEFT:
            #implement z-order by only acting on
            # last clickable object in this pos
            last_obj = None
            for obj in self.window_objects:
                if obj.clickable and obj.contains_coords(pos):
                    last_obj = obj
            if last_obj is not None:
                if last_obj is self.quit_btn:
                    clear_temp_messages = False
                last_obj.on_click(event.pos)
                last_obj.is_being_clicked = True
                self.dragged_obj = last_obj
        if clear_temp_messages:
            self.clear_temp_messages()

    def on_mousemove(self, pos):
        if self.dragged_obj is not None:
            if self.dragged_obj.draggable:
                self.dragged_obj.on_drag(event.pos)
            elif not self.dragged_obj.contains_coords(event.pos):
                self.dragged_obj.is_being_clicked = False
    def on_mouseup(self, button, pos):
        if event.button == BUTTON_LEFT:
            if self.dragged_obj is not None:
                if self.dragged_obj.draggable:
                    self.dragged_obj.on_drop(event.pos)
                self.dragged_obj.is_being_clicked = False
                self.dragged_obj = None

    def update(self, time_passed_ms):
        '''Return 0 or False to keep mainloop going,
        return True or any other number to exit the app'''
        i = 0
        while i < len(self.delayed_actions):
            delayed_action = self.delayed_actions[i]
            delayed_action[0] -= time_passed_ms
            if delayed_action[0] <= 0:
                delayed_action[1](*delayed_action[2])
                self.delayed_actions.pop(i)
            else:
                i += 1
        return self.quitting

    def draw(self):
        self.window.fill(self.settings.back_col_str)
        for obj in self.window_objects:
            obj.draw()

    def quit(self):
        if self.settings.stash_game:
            self.save_game(stash=True)
        self.settings.save_to_file()


#-------------------------------------------------------------------------------

#Load settings from file
settings = Settings(SETTINGS_FILEPATH)

#### BEGIN WINDOWS 10 SHENANIGANS

#set dpi awareness to fix pygame blurriness with high DPI
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)

#Get maximum client area size (assume single display??):
##screen_info = pygame.display.Info() #actually doesnt work - this func is kinda useless lol
# get work area (finally figured out how yay)
from ctypes import wintypes
SM_CYFRAME = 33
SM_CXPADDEDBORDER = 92
SM_CYCAPTION = 4
work_area_rect = wintypes.RECT()
ctypes.windll.user32.SystemParametersInfoA(0x30, 0, ctypes.pointer(work_area_rect), 0)
# get default caption bar height (non-client area at top of window)
#https://stackoverflow.com/a/28524464/9133950
#https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getsystemmetrics
cap_h = (ctypes.windll.user32.GetSystemMetrics(SM_CYFRAME)
         + ctypes.windll.user32.GetSystemMetrics(SM_CXPADDEDBORDER)
         + ctypes.windll.user32.GetSystemMetrics(SM_CYCAPTION))
del ctypes, wintypes
max_w = work_area_rect.right - work_area_rect.left
max_h = work_area_rect.bottom - work_area_rect.top - cap_h

#### END WINDOWS 10 SHENANIGANS

#init pygame
pygame.init()
#Enable key repeats
pygame.key.set_repeat(500, 35) #(delay, repeat) in milliseconds
#init frame timer
clock = Clock()

#Init window layout
#This class abstracts away most layout calculations,
# including working out the actual window width / height based on settings,
# and scaling / positioning everything else
window_layout = WindowLayout(settings, BOARD_SIZE_IN_SQ, max_w, max_h)
#Create the window
window = pygame.display.set_mode((window_layout.window_width, window_layout.window_height))
window.fill(settings.back_col_str)
pygame.display.set_caption('Portal Chess')
pygame.display.update()

#Init app
app = App(window, settings, window_layout, PIECE_LAYOUT)
#Note: from now on the app object controls settings and window_layout
# eg. settings are saved in app.quit()

#MAINLOOP
#try-except catches any runtime exceptions, and allows app to close gracefully
# once the exception is displayed on the console (or, in future, logged):
# -> game state is stashed
# -> window is closed normally via pygame
try:
    go = True
    while go:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                go = False
                break

            #handle keypresses
            elif event.type == KEYDOWN:
                mods = pygame.key.get_mods()
                ctrl, shift, alt = mods & KMOD_CTRL, mods & KMOD_SHIFT, mods & KMOD_ALT
                app.on_keydown(event.key, ctrl, shift, alt, pygame.mouse.get_pos())

            elif event.type == KEYUP:
                mods = pygame.key.get_mods()
                ctrl, shift, alt = mods & KMOD_CTRL, mods & KMOD_SHIFT, mods & KMOD_ALT
                app.on_keyup(event.key, ctrl, shift, alt, pygame.mouse.get_pos())

            #handle mouse movement/buttons
            elif event.type == MOUSEMOTION:
                app.on_mousemove(event.pos)

            elif event.type == MOUSEBUTTONDOWN:
                app.on_mousedown(event.button, event.pos)

            elif event.type == MOUSEBUTTONUP:
                app.on_mouseup(event.button, event.pos)

        if (not go) or app.update(clock.get_time()):
            break

        #Note: the app has a reference to window so can draw to it independently
        app.draw()
        pygame.display.update()

        clock.tick(settings.max_framerate)

except Exception as e:
    import traceback, sys
    print(''.join(traceback.format_exception(type(e), e, e.__traceback__)),
          file=sys.stderr)

app.quit()
pygame.quit()
