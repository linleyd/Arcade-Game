
import Tkinter
from pong_view import *
from pong_model import *
from pong_control import *

class top_level(Frame):
	'''This class makes instances of game, board and controls (model, view,
	 controller). It also defines a tkinter frame shared by board and controls.
	 The run method recursively calls the update methods. Its parent is the
	 tkinter root widget'''
	def __init__(self, parent):
		
		# Creates frame to contain canvas from view and control buttons from controls
		Frame.__init__(self, parent)
		self.parent = parent # parent is tkinter root
		
		# Creates game, controls and board objects
		# Note: the parent (tkinter root) is sent to the controls and board objects
		self.match = game()
		self.director = controls(self.parent, self.match)
		self.field = board(self.parent, self.match) 

	def run(self):

		if self.director.running: # check if user has pushed start button
			self.match.update_pieces() # update model
			self.field.update_UI() # update view
			self.director.get_input() # get user input fron keys to set paddles
			
			# tally score and reset if player has scored
			if self.match.update_score(): 
				self.match.reset_pieces() # resets game pieces in model
				self.field.initUI() # resets canvas and canvas images
			
			# Restart game - does same as reset but also changes score to zero
			if self.director.startover: # check if user has pushed restart button
				self.match.reset_pieces(new_game=1) # resets game pieces in model and sets score to zero
				self.field.initUI()
				self.director.startover = False
				self.director.running = False
		
		root.after(5, self.run) # Recursive run after 5 millisecond delay


root = Tkinter.Tk()
main_window = top_level(root)
main_window.run()

root.mainloop()