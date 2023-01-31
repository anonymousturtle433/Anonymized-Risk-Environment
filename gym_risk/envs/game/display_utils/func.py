import pygame, sys
import gym_risk.envs.game.display_utils.textrect as textrect
import gym_risk.envs.game.display_utils.constants_new as constants
from pygame.locals import *
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
pygame.init()
DISPLAYSURF = pygame.display.set_mode((1300,1000))

x = 0
y = 0

class DisplayFunc(object):
	'''
	The majority of the code in this class was taken from the following Github Repository
	https://github.com/happy96026/cmput275-project
	'''
	def __init__(self):
		pygame.init()
		self.background = pygame.image.load(cur_dir + '/' + "images/background_light.png").convert_alpha()
		self.background = pygame.transform.scale(self.background, (1300, 1000))
		self.r_map = pygame.image.load(cur_dir + '/' + "images/Risk_Empty_Map.png").convert_alpha()
		self.r_map = pygame.transform.scale(self.r_map, (1280, 920))
		self.pink_bubble = pygame.image.load(cur_dir + '/' + "images/pink_bubble.png").convert_alpha()
		self.orange_bubble = pygame.image.load(cur_dir + '/' + "images/orange_bubble.png").convert_alpha()
		self.teal_bubble = pygame.image.load(cur_dir + '/' + "images/teal_bubble.png").convert_alpha()
		self.grey_bubble = pygame.image.load(cur_dir + '/' + "images/grey_bubble.png").convert_alpha()
		self.pink_bubble = pygame.transform.scale(self.pink_bubble, (40, 40))
		self.orange_bubble = pygame.transform.scale(self.orange_bubble, (40, 40))
		self.teal_bubble = pygame.transform.scale(self.teal_bubble, (40, 40))
		self.grey_bubble = pygame.transform.scale(self.grey_bubble, (40, 40))
		self.rect = pygame.image.load(cur_dir + '/' + "images/round_rect.png").convert_alpha()
		self.text_rect = pygame.Rect((0, 0, 800, 150))
		self.text1 = None

		# Variables for printing legend
		self.legend = pygame.image.load(cur_dir + '/' + "images/round_rect.png").convert_alpha()
		self.legend = pygame.transform.scale(self.legend, (270, 125))
		self.name = pygame.Rect((0, 0, 130, 125))
		self.territories = pygame.Rect((0, 0, 70, 125))
		self.forces = pygame.Rect((0, 0, 70, 125))
		self.at = 0
		self.af = 0
		self.bt = 0
		self.bf = 0
		self.ct = 0
		self.cf = 0

		self.click = None
		self.TERRITORIES = constants.TERRITORIES
		self.FONT = pygame.font.Font(None, 35)
		self.FONT_country = pygame.font.Font(None, 25)
		self.FONT_legend = pygame.font.Font(None, 20)
		self.current_player = 3

	# ray casting algorithm
	# http://stackoverflow.com/questions/16625507/python-checking-if-point-is-inside-a-polygon
	def point_in_poly(self, x, y, poly):
		n = len(poly)
		inside = False

		p1x, p1y = poly[0]
		for i in range(n + 1):
			p2x, p2y = poly[i % n]
			if y > min(p1y, p2y):
				if y <= max(p1y, p2y):
					if x <= max(p1x, p2x):
						if p1y != p2y:
							xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
						if p1x == p2x or x <= xints:
							inside = not inside
			p1x, p1y = p2x, p2y
		return inside

	# checks if click down and click up
	def if_click(self):
		global click
		if pygame.mouse.get_pressed()[0] == 1:
			click = True
		if click and pygame.mouse.get_pressed()[0] == 0:
			click = False
			return True
		return False

	def print_legend(self):
		string = "Name\n\nALPHA\n\nBRAVO\n\nCHARLIE"
		legend_heading = textrect.render_textrect(string, self.FONT_legend, self.name, constants.WHITE)
		string = "Territories\n\n" + str(self.at) + '\n\n' + str(self.bt) + '\n\n' + str(self.ct)
		territories = textrect.render_textrect(string, self.FONT_legend, self.territories, constants.WHITE)
		string = "Forces\n\n" + str(self.af) + '\n\n' + str(self.bf) + '\n\n' + str(self.cf)
		forces = textrect.render_textrect(string, self.FONT_legend, self.forces, constants.WHITE)

		DISPLAYSURF.blit(legend_heading, (1010, 60))
		DISPLAYSURF.blit(territories, (1130, 60))
		DISPLAYSURF.blit(forces, (1200, 60))


	# prints in prompt
	def prompt_print(self, string):
		text = textrect.render_textrect(string, self.FONT, self.text_rect, constants.WHITE)
		DISPLAYSURF.blit(text, (60, 950))

	def display_country(self):
		for territory in self.TERRITORIES:
			text = self.FONT_country.render(str(territory["Country"]), 1, constants.WHITE)
			DISPLAYSURF.blit(text, territory["Country_Coordinates"])

	def army_size_print(self, territory):
		if territory["Player"] == 2:
			DISPLAYSURF.blit(self.teal_bubble, territory["Bubble"])
		elif territory["Player"] == 1:
			DISPLAYSURF.blit(self.pink_bubble, territory["Bubble"])
		elif territory["Player"] == 0:
			DISPLAYSURF.blit(self.orange_bubble, territory["Bubble"])
		else:
			DISPLAYSURF.blit(self.grey_bubble, territory["Bubble"])
		text = self.FONT.render(str(territory["Infantry"]), 1, constants.WHITE)
		if territory["Infantry"] < 10:
			DISPLAYSURF.blit(text, (territory["Bubble"][0] + 14, territory["Bubble"][1] + 8))
		else:
			DISPLAYSURF.blit(text, (territory["Bubble"][0] + 8, territory["Bubble"][1] + 7))

	# changes color of territory when mouse on territory
	def hover_color(self, territory, color):
		if type(territory["Coordinates"][0]) is tuple:
			pygame.draw.polygon(DISPLAYSURF, color, territory["Coordinates"])
		else:
			for subterritory in territory["Coordinates"]:
				pygame.draw.polygon(DISPLAYSURF, color, subterritory)

	# checks if mouse position is on territory
	def in_territory(self, x, y):
		for territory in self.TERRITORIES:
			if type(territory["Coordinates"][0]) is tuple:
				if self.point_in_poly(x, y, territory["Coordinates"]):
					return territory
			else:
				in_subterritory = False
				for subterritory in territory["Coordinates"]:
					if self.point_in_poly(x, y, subterritory):
						return territory
						break
		return None

	# no selection of territory
	def selection_screen(self):
		for territory in self.TERRITORIES:
			if territory["Player"] == 2:
				self.hover_color(territory, constants.TEAL)
			elif territory["Player"] == 1:
				self.hover_color(territory, constants.PINK)
			elif territory["Player"] == 0:
				self.hover_color(territory, constants.ORANGE)
			else:
				self.hover_color(territory, constants.GREY)
		for territory in self.TERRITORIES:
			self.army_size_print(territory)

	# Main loop
	def select(self):
		global x, y
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
			DISPLAYSURF.blit(self.background, (0, 0))
			DISPLAYSURF.blit(self.r_map, (0, 0))
			DISPLAYSURF.blit(self.rect, (40, 900))
			DISPLAYSURF.blit(self.legend, (1000, 50))
			self.selection_screen()
			self.display_country()
			self.print_legend()
			(x, y) = pygame.mouse.get_pos()

			territory = self.in_territory(x, y)
			if territory is None:
				self.prompt_print(self.text1)
			# mouse on territory
			else:
				self.hover_color(territory, territory["Color"])
				self.army_size_print(territory)
				self.prompt_print("The territory is " + territory["Name"])
				if self.if_click():
					return territory
			pygame.display.update()

	def refresh(self):
		global x, y
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
		DISPLAYSURF.blit(self.background, (0, 0))
		DISPLAYSURF.blit(self.r_map, (0, 0))
		DISPLAYSURF.blit(self.rect, (40, 900))
		DISPLAYSURF.blit(self.legend, (1000, 50))
		self.selection_screen()
		self.display_country()
		self.print_legend()
		(x, y) = pygame.mouse.get_pos()

		territory = self.in_territory(x, y)
		if territory is not None:
			self.army_size_print(territory)
		self.prompt_print(self.text1)
		pygame.display.update()

	def get_key(self):
		''' Based off www.pygame.org/pcr/inputbox
			Credit to Timothy Downs '''
		while True:
			event = pygame.event.poll()
			if event.type == KEYDOWN:
				return event.key
			else:
				pass

	def yes_no(self, question):
		''' Based off www.pygame.org/pcr/inputbox
			Credit to Timothy Downs '''
		while True:
			DISPLAYSURF.blit(self.background, (0, 0))
			DISPLAYSURF.blit(self.r_map, (0, 0))
			DISPLAYSURF.blit(self.rect, (40, 900))
			DISPLAYSURF.blit(self.legend, (1000, 50))
			self.selection_screen()
			self.display_country()
			self.print_legend()
			current_string = ""
			self.prompt_print(question + " (y or n): " + current_string)
			pygame.display.update()
			while True:
				events = pygame.event.get()
				for event in events:
					if event.type == QUIT:
						pygame.quit()
						sys.exit()
				DISPLAYSURF.blit(self.background, (0, 0))
				DISPLAYSURF.blit(self.r_map, (0, 0))
				DISPLAYSURF.blit(self.rect, (40, 900))
				DISPLAYSURF.blit(self.legend, (1000, 50))
				self.selection_screen()
				self.display_country()
				self.print_legend()
				(x, y) = pygame.mouse.get_pos()

				inkey = self.get_key()
				if inkey == K_BACKSPACE:
					current_string = current_string[0:-1]
				elif inkey == K_RETURN:
					break
				elif inkey <= 127:
					current_string += chr(inkey)
				self.prompt_print(question + " (y or n): " + current_string)
				pygame.display.update()

			self.prompt_print(" ")
			pygame.display.update()
			current_string.lower()
			if current_string == "" or (current_string[0] != 'y' and current_string[0] != 'n'):
				self.prompt_print("ERROR: Invalid letter!\nOnly enter y or n")
				pygame.display.update()
				pygame.time.delay(1500)
				continue
			elif current_string[0] == 'y':
				return True
			else:  # n
				return False

	def number(self, question):
		''' Based off www.pygame.org/pcr/inputbox
			Credit to Timothy Downs '''

		DISPLAYSURF.blit(self.background, (0, 0))
		DISPLAYSURF.blit(self.r_map, (0, 0))
		DISPLAYSURF.blit(self.rect, (40, 900))
		DISPLAYSURF.blit(self.legend, (1000, 50))
		self.selection_screen()
		self.display_country()
		self.print_legend()
		current_string = ""
		self.prompt_print(question + ": " + current_string)
		pygame.display.update()
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
			DISPLAYSURF.blit(self.background, (0, 0))
			DISPLAYSURF.blit(self.r_map, (0, 0))
			DISPLAYSURF.blit(self.rect, (40, 900))
			DISPLAYSURF.blit(self.legend, (1000, 50))
			self.selection_screen()
			self.display_country()
			self.print_legend()
			(x, y) = pygame.mouse.get_pos()

			inkey = self.get_key()
			if inkey == K_BACKSPACE:
				current_string = current_string[0:-1]
			elif inkey == K_RETURN:
				break
			elif inkey <= 127:
				current_string += chr(inkey)
			self.prompt_print(question + ": " + current_string)
			pygame.display.update()

		self.prompt_print(" ")
		pygame.display.update()
		try:
			num = int(current_string)
		except:
			return 0
		return num

click = False
