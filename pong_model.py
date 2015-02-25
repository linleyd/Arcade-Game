
import numpy as np
from numpy.linalg import norm
import random

class piece:
	# This class represents individual game pieces.
	# Other game piece classes inherit from this class
	# The game class creates instances of piece and represents the overall game.

	def __init__(self, coords, dimensions, velocity, moving = False):
		# for coords and velocity we keep a copy of the initial values to reset
		self.init_coords = np.array(coords, dtype=float) 
		self.coords = self.init_coords[:]# Center of shape
		self.init_velocity = np.array(velocity, dtype=float)
		self.velocity = self.init_velocity[:]

		self.dimensions = np.array(dimensions, dtype=float) # [width/2, height/2]
		self.get_positions() 
		
		self.moving = moving
		self.hit=None
		self.radius = self.dimensions[0]+5
		''' This has coords and positions. The coords are the center point
		of each shape. The positions are the coordinates of a box around the 
		shape based on the centerpoint and dimensions of the shape. The 
		positions get used by the view class to draw the shapes. The positions 
		are also used to identify lines of rectangular shapes that the ball 
		may bounce off of.''' 

	def get_positions(self):
		# Gets four corners of box around shape based on centerpoint and dimensions.
		x,y = self.coords
		w,h = self.dimensions
		self.positions = [x-w, y-h, x+w, y-h, x+w, y+h, x-w, y+h, x-w, y-h]

	def move(self, reset=0, coords=None):
		# called later to update each game piece
		# first updates center coordinates
		# then updates positions of shape outline
		# also used to reset piece when game is reset
		if reset == 1:
			self.coords = self.init_coords[:]
			self.velocity = self.init_velocity[:]
			self.get_positions()
		if reset == 2:
			self.coords = np.array(coords, dtype=float)
			self.get_positions()

		self.coords = np.array(self.coords, dtype = float)
		self.velocity = np.array(self.velocity, dtype = float)
		self.coords += self.velocity

		for i in range(0, len(self.positions), 2):
			self.positions[i] += self.velocity[0]
			self.positions[i+1] += self.velocity[1]

	def check_inscreen(self, bounds):
		# used by chaotic field, gravity field and portal
		# checks if center of ball is within rectangle defined by bounds
		x,y = self.coords
		left, top, right, bottom = bounds

		if y <= top or y >= bottom:
			return False
		elif x <= left or x >= right:
			return False
		else:
			return True

	def reflect2(self, line):
		if self.hit != self:
			# Find vectors from ball to line endpoints.
			p1 = np.array(line[0:2], dtype=float) # line endpoints
			p2 = np.array(line[2:4], dtype=float)
			v1 = p1 - self.coords #Vectors from ball to line end points

			# Find unit vector orthogonal to line
			x, y = p2 - p1 # vector between line endpoints
			line_norm = np.sqrt(x**2 + y**2) # norm of line
			line_orth = np.array([y, -x])/line_norm # orthogonal unit vector

			new_direction = np.dot(self.velocity, line_orth)*line_orth 
			self.velocity = self.velocity - 2*new_direction # velocity vector after reflection
			self.hit.velocity = np.array([0, 0], dtype=float)

class rectangle(piece):
	# This class adds rectangle specific stuff to piece class
	def __init__(self, coords, dimensions, velocity, moving=False, change = False):
		self.moving = moving
		self.piece = piece.__init__(self, coords, dimensions, velocity, moving=moving)
		
		# change indicates changing the paddle shape to a pentagon
		self.change = change
		self.change_profile()
		
		self.lines = []
		self.get_lines()

	def change_profile(self):
		# changes paddle shape to pentagon
		# adds extra x,y pair to positions in appropriate index

		if self.change != 0:
			x = self.coords[0]+self.change*20 # change will be +1 or -1
			y = self.coords[1]
			
			# new point must go in correct indices
			# order of points in list affects how view draws shape
			if self.change > 0: # indices 4, 5 for left side paddle
				self.positions.insert(4, x)
				self.positions.insert(5, y)
			elif self.change < 0: # indices 8, 9 for right side paddle
				self.positions.insert(8, x)
				self.positions.insert(9, y)
			
			self.get_lines() # must get new lines based on changed outline

	def get_lines(self):
		# Gets lines of rectangles sides. 
		# [x1, y1, x2, y2] This is how each line is represented.
		# Having the coordinates of these lines is useful in collision detection.
		self.lines = []
		for i in range(4,len(self.positions)+1, 2):
			self.lines.append(self.positions[i-4:i])

	def move(self, reset=0, coords=None):
		# Uses move method of parent class.
		# Then updates lines since lines are specific to rectangle. 
		piece.move(self, reset, coords)
		if reset == 1 or reset ==2:
			self.get_lines()
		else:
			for line in self.lines:
				line[0:2] += self.velocity
				line[2:4] += self.velocity

	def hit_check(self, shape, reference = [0, 0]):
		#Uses projections of ball velocity and lines to find collision.

		self.collision = None
		for line in self.lines:

			# velocity is velocity of projectile(self) relative to wall(shape)
			velocity = shape.velocity - self.velocity
		
			vector = np.array([line[0]-line[2], line[1]-line[3]])
			unitv = vector/norm(vector)
			unormal = np.array([-unitv[1], unitv[0]])

			v1 = np.array(line[0:2]) - shape.coords #Vectors from ball to line ends.
			v2 = np.array(line[2:4]) - shape.coords

			# These projections are used to assess projectile will cross wall
			# Projections of line end point vectors onto velocity vector and vice versa
			proj_v1_v2 = np.dot(v1, v2) 
			proj_v1_velocity = np.dot(v1, velocity)
			proj_v2_v1 = np.dot(v2,v1)
			proj_v2_velocity = np.dot(v2, velocity)

			within_edges = False # See if velocity vector is between vectors from ball to line ends.
			if proj_v1_v2 < proj_v1_velocity and proj_v2_v1 < proj_v2_velocity:
				within_edges = True

			# These projections used to see how close projectile is to wall
			proj_distance_normal = np.dot(v1, unormal)
			proj_velocity_normal = np.dot(velocity, unormal)
			#See if velocity normal to paddle line exceeds ball distance normal to line.
			
			same_direction = False #See if velocity is towards the line
			if proj_distance_normal*proj_velocity_normal > 0:
				same_direction = True

			if abs(proj_velocity_normal) > abs(proj_distance_normal)-shape.radius:
				if within_edges and same_direction:
					self.collision=line

		return self.collision

class Obstacle(rectangle):
	# This is the break out wall
	def __init__(self, coords, dimensions, velocity, moving=False):
		self.moving=moving
		rectangle.__init__(self, coords, dimensions, velocity, moving=moving)

	def break_out(self):
		self.dimensions = [0,0] # shrink wall to nothing after collision
		self.get_positions() # update positions and lines after shrinking wall
		self.get_lines()

class chaotic_field(rectangle):
	def __init__(self, coords, dimensions, velocity, moving=False):
		self.moving=moving
		rectangle.__init__(self, coords, dimensions, velocity, moving=moving)
		self.count = 1
		self.perimeter = self.positions[0:3]+self.positions[5:6]

	def random_velocity(self, ball):
		# checks if ball is within field
		# counts while ball is within field
		# changes ball velocity after 20 increments
		within = False
		within = ball.check_inscreen(self.perimeter)
		
		if within:
			self.count += 1

			if self.count%20 == 0:
				x = random.uniform(-3,3)
				y = random.uniform(-3,3)
				ball.velocity = np.array([x, y])

class gravity_field(rectangle):
	def __init__(self, coords, dimensions, velocity, gravity, moving=False):
		rectangle.__init__(self, coords, dimensions, velocity, moving=moving)
		self.gravity = np.array(gravity, dtype=float)

	def force(self, shape):
		# checks if ball is within field
		# adds gravity to ball velocity every time step ball is in field
		self.perimeter = self.positions[0:3] + self.positions[5:6]
		within = False
		within = shape.check_inscreen(self.perimeter)
		if within:
			shape.velocity += self.gravity

class Portal:

	def __init__(self):
		# keeps list of portals (a.k.a. lines) to transport between
		# lines are actually skinny rectangles drawn on canvas
		self.lines = {}
		self.line_list = self.lines.keys()
		self.count = 0

	def add_line(self, coords, dimensions):
		self.count+=1
		line = piece(coords, dimensions, [0, 0])
		name = "portal"+str(self.count)
		self.lines[name]=line
		self.line_list.append(name)

	def transport(self, ball):
		# loops through portal list
		# checks if ball is within portal
		# shifts ball position to next portal in list
		for i in range(len(self.line_list)):
			name1 = self.line_list[i]
			name2 = self.line_list[i-1]
			line1 = self.lines[name1]
			line2 = self.lines[name2]
			perimeter = line1.positions[0:3] + line2.positions[5:6]
			if ball.check_inscreen(perimeter):
				new_coords = line2.coords-line1.coords
				new_coords = new_coords*(1+2*norm(line1.dimensions)/norm(new_coords))
				new_coords += ball.coords
				ball.move(reset=2, coords=new_coords) # move method also used to reset positions

class circle(piece):
	# This class adds circle specific stuff to piece class.
	def __init__(self, coords, dimensions, velocity, moving=False):
		self.moving=moving
		piece.__init__(self, coords, dimensions, velocity, moving=moving)

class creature(rectangle):
	def __init__(self, coords, dimensions, velocity, moving=True):
		self.moving = True
		rectangle.__init__(self, coords, dimensions, velocity, moving=moving)
		self.count = 0

	def move(self, reset=0):
		# changes velocity every 200 time steps
		# reflects off walls and paddles just like ball does
		# ball reflects off creature sides
		rectangle.move(self, reset)

		self.count +=1
		if self.count%200 == 0:
			x = random.randint(-5,5)
			y = random.randint(-5,5)
			self.velocity = np.array([x, y])

class game:
	''' The purpose of this class is to assemble all instances of game pieces
	and update them altogether.'''
	def __init__(self):

		self.ball = circle([300, 150], [5, 5], [-1,1], moving = True)
		self.paddleA = rectangle([50, 150], [10, 25], [0, 0], moving = True)
		self.paddleB = rectangle([550, 250], [10, 25], [0,0], moving=True)
		self.border = rectangle([300, 150], [300, 150], [0,0])

		self.switcheroo = chaotic_field([300, 150], [30, 75], [0,0])
		self.planet = gravity_field([300, 150], [50, 50], [0, 0], [0, 0.05])
		self.gate = Portal()
		self.gate.add_line([400, 250], [20, 3])
		self.gate.add_line([200, 250], [20, 3])
		self.monster = creature([120, 200], [15, 15], [1, -1])
		self.bumper = Obstacle([400, 150], [3,50], [0,0])
		self.counter = 1

		self.init_main_pieces() # create dictionaries to group game pieces
		self.init_obstacles() # create obstacle dictionary to choose obstacle

		self.hits = 0 
		
		self.score_player1 = 0
		self.score_player2 = 0

	def init_main_pieces(self):
		# dictionaries are: parts, walls and moving_parts
		# they start off with normal pieces then get updated with obstacle
		keys = ["zball", "paddleA", "paddleB", "border"]
		values = [self.ball, self.paddleA, self.paddleB, self.border]
		self.parts = dict(zip(keys, values))

		keys = ["paddleA", "paddleB", "border"]
		values = [self.paddleA, self.paddleB, self.border]
		self.walls = dict(zip(keys, values))

		keys = ["paddleA", "paddleB", "zball"]
		values = [self.paddleA, self.paddleB, self.ball]
		self.moving_parts = dict(zip(keys, values))

	def init_obstacles(self):

		keys = ["bumper", "switcheroo", "planet", "gate", "monster"]
		values = [self.bumper, self.switcheroo, self.planet, self.gate, self.monster]
		self.obstacles = dict(zip(keys, values))

		self.choose_obstacle()

	def choose_obstacle(self):
		# chooses random obstacle from obstacle dictionary
		# selects index from list of dictionary keys
		# selects index by generating random number
		# updates dictionaries according to obstacle selection
		# if random number is even, paddle shapes change to pentagons

		options = self.obstacles.keys()
		lottery = random.randint(0,len(options)-1)
		choice = options[lottery] # select obstacle
		if lottery%2 == 0: # change paddle shape if lottery is even
			self.paddleA.change = 1
			self.paddleB.change = -1
			self.paddleA.change_profile()
			self.paddleB.change_profile()

		if choice == "gate": # update dictionaries based on selected obstacle
			self.parts.update(self.gate.lines)
		elif choice == "monster":
			self.parts["monster"] = self.monster
			self.moving_parts["monster"] = self.monster
			self.walls["monster"] = self.monster
		elif choice == "bumper":
			x = random.randint(200, 400)
			y = 150
			self.bumper.dimensions = [3, 50]
			self.bumper.move(coords=[x,y], reset=2)
			self.parts["bumper"] = self.obstacles["bumper"]
			self.walls["bumper"] = self.obstacles["bumper"]
		elif choice == "planet":
			x = random.randint(200, 400)
			y = random.randint(100, 200)
			if y%2: self.planet.gravity[1] = -0.05
			self.planet.move(coords=[x, y], reset=2)
			self.parts["planet"] = self.obstacles[choice]
		else:
			self.parts[choice] = self.obstacles[choice]

	def update_score(self):
		# Updates score when ball is behind paddle.
		# Returns True to the top level run loop to indicate game reset
		if self.parts["zball"].coords[0] < 30:
			self.score_player1 += 1
			return True
		elif self.parts["zball"].coords[0] > 570:
			self.score_player2 += 1
			return True
		else:
			return False
		
	def reset_pieces(self, new_game=0):
		# clears and refills dictionaries with different obstacle
		# resets all moving parts
		# if game is to be restarted, sets score to zero
		self.parts = {}
		self.walls = {}
		self.moving_parts = {}
		self.init_main_pieces()
		for part in self.parts.values():
			if part.moving == True:
				part.move(reset=1) # update positions of each game piece.
		self.choose_obstacle()
		if new_game!=0:
			self.score_player1 = 0
			self.score_player2 = 0

	def update_pieces(self):
		''' This method loops through the game pieces to call the "move" method
		for each one. Then it loops through them again to check for collision. 
		'''	
		
		# ball_stuff is list of objects that can reflet off walls
		# usually just ball or ball and monster is in ball_stuff
		ball_stuff = self.moving_parts.copy()
		del ball_stuff["paddleA"]
		del ball_stuff["paddleB"]

		collision_line = None

		for item in ball_stuff.values():
	
			x1, y1 = item.coords
			# check_items is walls that can be reflected off of
			# if the item from ball_stuff is the monster, 
			# we want to leave monster out of check_items
			if item == self.ball:
				check_items = self.walls.copy()
			else:
				check_items = self.walls.copy()
				del check_items["monster"]

			for key, value in check_items.items():
				# this is where collision detection occurs
				collision_line = value.hit_check(item) # saves collision wall
				if value.collision != None and self.counter < 1:
					self.counter+=1
					item.hit = value
					item.reflect2(collision_line) # reflects ball (or monster)
					# keeps track of paddle hits
					# after five paddle hits, increases ball velocity
					if item == self.ball:
						if key == "paddleA" or key == "paddleB":
							self.hits+=1
							if self.hits == 5:
								self.hits = 0
								self.ball.velocity *= 1.5
					# checks if collision wall is break out wall
					# then call break_out() method
					if key == "bumper":
						self.bumper.break_out()

		if collision_line == None:
			self.counter = 0

		# these are obstacle specific methods for gravity, chaotic field and portal				
		names = self.parts.keys()
		if "switcheroo" in names:
			self.switcheroo.random_velocity(self.ball)
		elif "portal1" in names or "portal2" in names:
			self.gate.transport(self.ball)
		elif "planet" in names:
			self.planet.force(self.ball)

		for part in self.parts.values():
			if part.moving == True:
				part.move() # update positions of each game piece.