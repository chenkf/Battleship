# Kaifeng Chen
# University of Michigan - Ann Arbor

from abc import ABCMeta, abstractmethod

# set appropriate height to adjust your terminal window
screen_height = 30

class Game:

	def __init__(self):
		self.players = [Player('Player 1'), Player('Player 2')]
		self.players[0].set_rival(self.players[1])
		self.players[1].set_rival(self.players[0])

	def play(self):
		raw_input("Welcome to Battleship. Press enter to start the game!")
		print("\n"*screen_height)
		self.players[0].place_ships()
		self.players[1].place_ships()
		raw_input("The ships are all set. Press enter to start the battle!")
		print("\n"*screen_height)
		game_over = False
		first_players_turn = True
		while not game_over:
			if first_players_turn:
				game_over = self.players[0].take_turn()
				if game_over:
					print("\n"*screen_height)
					print("Game over!")
					print(self.players[0].name + ' wins the game!')
			else:
				game_over = self.players[1].take_turn()
				if game_over:
					print("\n"*screen_height)
					print("Game over!")
					print(self.players[1].name + ' wins the game!')
			first_players_turn = not first_players_turn


class Player(object):

	def __init__(self, name):
		self.name = name
		self.ocean = Ocean()
		self.ships = [Carrier((1, 5)), Battleship((1, 4)), Submarine((1, 3)), Cruiser((1, 2)), Destroyer((1, 2))]
		# self.ships =  [Destroyer((1, 2))]
		# count the number of successful hit
		self.hit_count = 0
		# count the number of ships shoot down
		self.sunk_count = 0
		self.rival = None

	def set_rival(self, rival):
		self.rival = rival

	def place_ships(self):
		raw_input(self.name+", press enter to place your ships!")
		for ship in self.ships:
			print("\n"*screen_height)
			print("Now place a " + ship.get_type())

			orientation = False
			# keep looping until a valid orientation is input
			while not orientation:
				try:			
					print(self.ocean.view_to_self())
					orientation = raw_input(self.name + ", choose an orientation for the ship by entering 'v' or 'h': ").lower()
					print("\n"*screen_height)
					if (orientation != "v") and (orientation != "h"):
						raise Exception
				except:	
					print(self.name + ", you must enter a 'v' or a 'h'. Please try again.")
					orientation = False


			location = False
			# keep looping until a valid location is input
			while not location:
				try:
					print(self.ocean.view_to_self())
					location = raw_input(self.name + ", choose a bow location by entering a letter (a-j) followed by a number (0-9): ")
					print("\n"*screen_height)
					x = ord(location[0].lower()) % 32 - 1
					y = int(location[1])
					ship.set_orientation(orientation)
					ship.set_location((x, y))
					if not self.ocean.add_ship(ship):
						raise Exception
				except:
					print(self.name +", you must enter an unoccupied location on the ocean. Please try again.")
					location = False
		print(self.name + ", review your ship placement!")
		print(self.ocean.view_to_self())
		raw_input("Press enter for the next player to continue!")
		print("\n"*screen_height)

	def take_turn(self):
		raw_input(self.name + ", press enter to take your current turn!")
		print("\n"*screen_height)
		x, y = self.send_guess()
		self.receive_guess(x, y)
		if self.signal_game_over():
			return True
		else:
			raw_input("Press enter for the next player to continue!")
			print("\n"*screen_height)
			return False

	def send_guess(self):
		location = False
		# keep looping until a valid location is input
		while not location:
			try:
				print("My board:")
				print(self.ocean.view_to_self())
				print("My rival's board:")
				print(self.rival.ocean.view_to_enemy())
				location = raw_input(self.name + ', choose a location to shoot by entering a letter (a-j) followed by a number (0-9): ')
				x = ord(location[0].lower()) % 32 -1
				y = int(location[1])
				if not self.ocean.check_range(x, y, 1, 1):
					raise Exception
			except:
				print("\n"*screen_height)
				print(self.name + ", you must aim at a valid position by entering a letter (a-j) followed by a number (0-9)")
				location = False
		return (x,y)

	def receive_guess(self, x, y):
		hit = self.attack(x, y)
		print("my board:")
		print(self.ocean.view_to_self())
		print("my rival's board:")
		print(self.rival.ocean.view_to_enemy())
		self.signal_hit_or_miss(hit)
		if hit: 
			self.signal_sunk(x, y)
		

	def attack(self, x, y):
		if self.rival.ocean.field[y][x] == 1:
			self.rival.ocean.field[y][x] = 2
			self.hit_count += 1
			return True
		elif self.ocean.field[y][x] == 3:
			self.ocean.field[y][x] = 4
			return False
		else:
			return False

	def signal_hit_or_miss(self, hit):
		if hit:
			print(self.name + ", you hit a ship!")
		else:
			print(self.name + ", you missed!")
		print ("Until now you have " + str(self.hit_count) + " successful hit in total!")

	def signal_sunk(self, x, y):
		ship_type = None
		for ship in self.rival.ships:
			if (x,y) in ship.hit_condition:
				ship_type = ship.get_type()
				ship.update_hit_condition(x, y)
				for location, hit in ship.hit_condition.iteritems():
					if location!=(x, y) and hit == False:
						return
		self.sunk_count += 1
		for ship in self.rival.ships:
			if (x,y) in ship.hit_condition:
				for x, y in ship.hit_condition:
					self.rival.ocean.field[y][x] = 3
				break
		print("Your enemy (" + self.rival.name + ")'s " + ship_type + " is sunk!")
		print ("Until now you have shoot down " + str(self.sunk_count) + " ships in total!")


	def signal_game_over(self):
		if self.hit_count == sum([ship.get_size() for ship in self.ships]):
			return True
		else:
			return False
		

class Ocean(object):
	##						 		String Representation Table
	## encoding: meaning					Self 	Enemy
	## 1: occupied and intact--------------- X 		
	## 2: occupied and hit------------------ H 		  H
	## 3: occupied and sunk----------------- S        S
	## 4: unoccupied and intact            	  
	## 5: unoccupied and hit---------------- 		  O

	def __init__(self):
		self.field = [[4] * 10 for i in range(10)]

	def view_to_self(self):
		board_states = '  A B C D E F G H I J\n'
		for i in range(10):
			board_states += str(i)
			for j in range(10):
				if self.field[i][j] == 1:
					board_states += ' ' + 'X'
				elif self.field[i][j] == 2:
					board_states += ' ' + 'H'
				elif self.field[i][j] == 3:
					board_states += ' ' + 'S'
				else:
					board_states += '  '
			board_states += '\n'
		return board_states

	def view_to_enemy(self):
		board_states = '  A B C D E F G H I J\n'
		for i in range(10):
			board_states += str(i)
			for j in range(10):
				if self.field[i][j] == 2:
					board_states += ' ' + 'H'
				elif self.field[i][j] == 3:
					board_states += ' ' + 'S'
				elif self.field[i][j] == 5:
					board_states += ' ' + 'O'
				else:
					board_states += '  '
			board_states += '\n'
		return board_states

	# check if input are within the ocean's range
	def check_range(self, x, y, width, height):
		if not (x in range(10) and y in range(10)
				and x + width - 1 in range(10)
				and y + height - 1 in range(10)):
			return False
		return True

	# check if ocean cell is occupied
	def check_occupied(self, x, y, width, height):
		for i in range(width):
			for j in range(height):
				if self.field[y + j][x + i] == 1:
					return False
		return True

	# add a ship to the ocean if input is valid
	def add_ship(self, ship):
		height = (max(ship.size) if ship.orientation == 'v'
				   else min(ship.size))
		width = (max(ship.size) if ship.orientation == 'h'
				  else min(ship.size))
		if not self.check_range(ship.location[0], ship.location[1], width, height):
			return False
		if not self.check_occupied(ship.location[0], ship.location[1], width, height):
			return False
		for x in range(width):
			for y in range(height):
				self.field[ship.location[1] + y][ship.location[0] + x] = 1
				ship.set_hit_condition(ship.location[0] + x, ship.location[1] + y)
		return True

# virtual base class
class Ship(object):

	__metaclass__ = ABCMeta

	def __init__(self, size):
		self.size = size
		self.location = None
		self.orientation = None
		self.hit_condition = {}

	@abstractmethod
	def get_type(self):
		pass

	# get volumn of the ship
	def get_size(self):
		return self.size[0]*self.size[1]

	# set bow location coordinate pair
	def set_location(self, location):
		self.location = location

	def set_orientation(self, orientation):
		self.orientation = orientation

	def set_hit_condition(self, x, y):
		self.hit_condition[(x, y)] = False

	def update_hit_condition(self, x, y):
		self.hit_condition[(x, y)] = True

# concrete subclass
class Carrier(Ship):

	def __init__(self, size):
		super(Carrier, self).__init__(size)

	def get_type(self):
		return "Carrier"


class Battleship(Ship):

	def __init__(self, size):
		super(Battleship, self).__init__(size)

	def get_type(self):
		return "Battleship"


class Submarine(Ship):

	def __init__(self, size):
		super(Submarine, self).__init__(size)

	def get_type(self):
		return "Submarine"


class Cruiser(Ship):

	def __init__(self, size):
		super(Cruiser, self).__init__(size)

	def get_type(self):
		return "Cruiser"


class Destroyer(Ship):

	def __init__(self, size):
		super(Destroyer, self).__init__(size)

	def get_type(self):
		return "Destroyer"


if __name__ == "__main__":
	game = Game()
	game.play()




			