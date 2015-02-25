
from Tkinter import *

class board(Frame):
    def __init__(self, parent, game):
        # communicates with game class
        # uses game piece dictionary of game object to get info from model
        self.parent = parent # tkinter root window
        self.canvas = Canvas(parent, height = 300, width=600, background="black")
        self.canvas.grid(row=0, column = 0, columnspan = 8)
        
        self.game = game # reference to game to access model info
        self.initUI()
        
        self.label_p1 = Label(self.parent, text = "Player 1")
        self.label_p1.grid(row = 1, column = 0, columnspan=1)

        self.label_p2 = Label(self.parent, text = "Player 2")
        self.label_p2.grid(row = 1, column = 7, columnspan=1)

    def initUI(self):
        # makes dictionary of images of each shape

        # Clears canvas and view dictionaries so initUI can be used to reset view
        self.canvas.delete("all") 
        self.images = {} 
        self.shapes = {}

        # This is where the shapes dictionary is remade after reset
        # Then the images dictionary is made using the shapes dictionary and the draw_shape method
        self.shapes = self.game.parts
        for key, value in self.shapes.items():
            pic = self.draw_shape(key, value)
            self.images[key] = pic

        #Recreates labels with updated score after reset
        self.label_p1_score_value = Label(self.parent,text='  %s  '
                 %self.game.score_player1)
        self.label_p1_score_value.grid(row = 1, column = 2)
        
        self.label_p2_score_value = Label(self.parent,text='  %s  ' 
                 %self.game.score_player2)
        self.label_p2_score_value.grid(row = 1, column = 4)

    def draw_shape(self, name, shape):
        # used by initUI and updateUI methods to draw individual shapes
        # uses positions of box around shape to draw shape
        # tkinter create_line method draws lines that outline shape
        # circle is drawn as rectangle with rounded corners.
        # keyword smooth rounds rectangle corners.
        is_smooth = 0
        color = "white"

        # checks name of game piece to choose color
        if shape.__class__.__name__ == 'circle':
            is_smooth = 1
            color = "white"
        if shape.__class__.__name__ == 'Obstacle':
            color = "red"
        if shape.__class__.__name__ == 'chaotic_field':
            color = "yellow"
        if name[0:6] ==  "portal":
            color = "green"
        if name[0:7] == 'monster':
            color = "blue"

        # calls canvas method to create image
        image = self.canvas.create_line(*shape.positions, 
            smooth = is_smooth, fill=color)
        return image

    def update_UI(self):
        # updates images dictionary based on shapes dictionary
        for name in self.images:
            self.canvas.coords(self.images[name], *self.shapes[name].positions)