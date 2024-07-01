import pygame

class Rectangle:
    def __init__(self, window, x, y, width, height, colour):
        #User interaction
        self.window = window
        self.clickable = False
        self.draggable = False

        #Drawing
        self.rect = (x, y, width, height)
        self.colour = colour

    def draw(self):
        pygame.draw.rect(self.window, self.colour, self.rect)

class Button:
    '''Coloured button with set text. Can change colours when clicked.
    Can be hidden, meaning that button is not drawn and cannot be clicked'''
    #Implementation of hide/show is overall not perfect - because when
    # hidden button is not taken out of app's z-order. So it can block
    # something below it from being clicked. However I have tried to
    # write app so that interactive objects never normally overlap, and
    # overlapping objects isn't really necessary unless showing a popup
    def __init__(self, window, x, y, width, height,
                 colour, text_colour, click_colour, click_text_colour,
                 font, text, on_click_call=lambda:None):
        #User interaction
        self.window = window
        self.clickable = True
        self.draggable = False
        self.is_being_clicked = False #automatically modified by app
        self.on_click_call = on_click_call

        #Location
        self.hidden = False
        self.rect = [x, y, width, height]

        #Colours
        self.colour = colour
        self.text_colour = text_colour
        self.click_colour = click_colour
        self.click_text_colour = click_text_colour

        #Text
        self.text = text
        __ = self._render_text_2cols(text, font, text_colour, click_text_colour, self.rect)
        self.text_surf, self.click_text_surf, self.text_pos = __
        self.text_size = self.text_surf.get_size()

    def get_text_size(self):
        return self.text_size

    @staticmethod
    def _render_text_2cols(text, font, col1, col2, btn_rect):
        '''Render the same text in two colours.
        Buttons can have a different text colour when being clicked'''
        text_surf1 = font.render(text, True, col1)
        text_surf2 = font.render(text, True, col2)
        text_pos = Button._calculate_text_pos(text_surf1.get_size(), btn_rect)
        return text_surf1, text_surf2, text_pos

    @staticmethod
    def _calculate_text_pos(text_size, btn_rect):
        '''Center text in button rect'''
        x, y, width, height = btn_rect
        return (x + (width - text_size[0]) // 2,
                y + (height - text_size[1]) // 2)
    def _recalculate_text_pos(self):
        '''Call this function whenever button pos/size/text is changed'''
        self.text_pos = self._calculate_text_pos(self.text_size, self.rect)

    def get_pos(self):
        return self.rect[0:2]
    def set_pos(self, pos):
        '''Move the button'''
        self.rect[0], self.rect[1] = pos
        self._recalculate_text_pos()
    def get_size(self):
        return self.rect[2:]
    def change_size(self, new_size):
        '''Set a new size for button (text will still be centered)'''
        self.rect[2], self.rect[3] = new_size
        self._recalculate_text_pos()

    def hide(self):
        '''When button is hidden it is not drawn and cannot be clicked.
        No effect if button is already hidden.'''
        self.hidden = True
    def show(self):
        '''Un-hide button. No effect if button is not hidden'''
        self.hidden = False

    def on_click(self, pos):
        '''Called by app when left mouse btn is clicked,
        and self.contains_coords(mouse_pos) returns True'''
        if not self.hidden:
            self.on_click_call()

    def contains_coords(self, pos):
        '''Used by app to determine if button is being clicked'''
        return (self.rect[0] <= pos[0] < self.rect[0] + self.rect[2] and
                self.rect[1] <= pos[1] < self.rect[1] + self.rect[3])

    def draw(self):
        '''Draw coloured rect and text directly on window'''
        if not self.hidden:
            if self.is_being_clicked:
                pygame.draw.rect(self.window, self.click_colour, self.rect)
                self.window.blit(self.click_text_surf, self.text_pos)
            else:
                pygame.draw.rect(self.window, self.colour, self.rect)
                self.window.blit(self.text_surf, self.text_pos)

class MultiButton(Button):
    '''A MultiButton is a button with multiple 'states' (sets of text/colours/on_click),
    but just one button rect. Can be used to eg. implement a button that can
    be disabled, or a toggle, or display a success message'''
    def __init__(self, window, x, y, width, height, num_states,
                 colours, text_colours, click_colours, click_text_colours,
                 font, texts, on_click_callables, next_state):
        '''on_click_callables is a list of length num_states; when the
        button is clicked on_click_callables[current_state] will be called.
        next_state is a list of length num_states; when clicked, the button
        will change state to next_state[current_state], unless
        next_state[current_state] is None. Functions in
        on_click_callables should not modify state. Initial state is 0'''
        #User interaction
        self.window = window
        self.clickable = True
        self.draggable = False
        self.is_being_clicked = False

        #States
        assert (len(colours) == len(text_colours) == len(click_colours)
                == len(click_text_colours) == len(texts)
                == len(on_click_callables) == len(next_state) == num_states)
        self.num_states = num_states
        self.state = 0
        self.next_state = next_state

        #Location
        self.rect = [x, y, width, height]
        self.on_click_callables = on_click_callables
        self.hidden = False

        #Colours
        self.colours = colours
        self.text_colours = text_colours
        self.click_colours = click_colours
        self.click_text_colours = click_text_colours

        #Text
        self.texts = texts
        self.text_surfs = []
        self.click_text_surfs = []
        self.text_pos = []
        self.text_sizes = []
        for text, col, click_col in zip(texts, text_colours, click_text_colours):
            text_surf, click_text_surf, text_pos = \
                Button._render_text_2cols(text, font, col, click_col, self.rect)
            self.text_surfs.append(text_surf)
            self.click_text_surfs.append(click_text_surf)
            self.text_pos.append(text_pos)
            self.text_sizes.append(text_surf.get_size())
        self.max_text_size = (max(s[0] for s in self.text_sizes),
                              max(s[1] for s in self.text_sizes))

    def get_text_size(self):
        #Max: make sure the biggest text will still fit
        return self.max_text_size
    def _recalculate_text_pos(self):
        '''Centre text for each state'''
        for i, text_size in enumerate(self.text_sizes):
            self.text_pos[i] = self._calculate_text_pos(text_size, self.rect)

    def set_state(self, state):
        '''state should be in (0 ... num_states-1)'''
        assert state in range(self.num_states)
        self.state = int(state)
    def reset_state(self):
        '''set state to 0'''
        self.state = 0

    def on_click(self, pos):
        '''Calls the relevant function, and updates state'''
        if not self.hidden:
            state = self.state
            self.on_click_callables[state]()
            next_state = self.next_state[state]
            if next_state is not None:
                self.state = next_state
    def draw(self):
        if not self.hidden:
            if self.is_being_clicked:
                btn_col = self.click_colours[self.state]
                text_surf = self.click_text_surfs[self.state]
            else:
                btn_col = self.colours[self.state]
                text_surf = self.text_surfs[self.state]
            pygame.draw.rect(self.window, btn_col, self.rect)
            self.window.blit(text_surf, self.text_pos[self.state])


class ToggleButton(MultiButton):
    '''A button with two states (0 and 1), that can act as a toggle'''
    def __init__(self, window, x, y, width, height,
                 colour, text_colour, click_colour, click_text_colour, font,
                 text0='0', on_click_0=lambda:None, text1='1', on_click_1=lambda:None):
        MultiButton.__init__(self,
            window, x, y, width, height, 2,
            2*(colour,), 2*(text_colour,), 2*(click_colour,), 2*(click_text_colour,),
            font, (text0, text1), (on_click_0, on_click_1), (1, 0)
        )

    def toggle_state(self):
        self.set_state(1 - self.state)

