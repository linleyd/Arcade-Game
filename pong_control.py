
from Tkinter import *

class controls(Frame):
    ''' This class takes user input from keys that control the paddles and it
    makes start/pause buttons and displays score. It communicates with model.'''
    def __init__(self, parent, game):
        self.parent = parent # this is tkinter root window
        self.game = game # reference to game instance to access model info
        self.running = False # used when user presses start or pause buttons
        self.startover = False # used to indicate when user presses restart

        # Bind keys so players can move paddle
        self.buttons = set()
        self.parent.bind_all("<KeyPress>", lambda e: self.buttons.add(e.keysym))
        self.parent.bind_all("<KeyRelease>", lambda e: self.buttons.discard(e.keysym))

        # Make start and puase buttons
        # Commands are lambda that uses setattr to change self.running and self.startover
        self.start_button = Button(self.parent, text="Start", 
                    command = lambda e=self: setattr(e, "running", True))
        self.start_button.grid(row=2, column = 0, columnspan = 1)

        self.pause_button = Button(self.parent, text= "Pause", 
                    command = lambda e=self: setattr(e, "running", False))
        self.pause_button.grid(row=2, column=2, columnspan = 2)
   
        self.restart = Button(self.parent, text="Restart", 
                    command = lambda e=self: setattr(e, "startover", True))
        self.restart.grid(row=2, column = 3, columnspan = 2)
        
        self.quit = Button(self.parent, text = " Quit  ", 
                    command=self.parent.quit)
        self.quit.grid(row=2, column=7, columnspan = 1)

    def set_paddle(self, paddle, button, velocity):
        # called by get_input method
        # updates paddle based on what buttons are pressed
        # paddle argument is a key in the dictionary of game pieces
        # button = [up-button, down-button]


        # uses paddle center and height to check if paddle is on screen
        y = self.game.parts[paddle].coords[1]
        height = self.game.parts[paddle].dimensions[1]


        if button[0] in self.buttons and y>(0+height):
            self.game.parts[paddle].velocity = [0, -velocity]

        elif button[1] in self.buttons and y<(300-height):
            self.game.parts[paddle].velocity = [0, velocity]

        else:
            self.game.parts[paddle].velocity = [0, 0]

    def get_input(self):
        # maps paddles, buttons and paddle velocities to set_paddle
        paddles = ["paddleA", "paddleB"] # keys of paddles in game piece dictionary
        buttons = [["e", "s"], ["Up", "Down"]]
        velocities = [2] * 2 # all velocities are 2 in the y direction
        # velocity sign is changed depending on which button is pressed.
        map(self.set_paddle, paddles, buttons, velocities)