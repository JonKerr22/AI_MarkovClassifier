import pygame
import sys
import math
from collections import defaultdict
from random import random
SCREEN_SIZE = (640, 480)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE  = (0,0,255)

PADDLE_HEIGHT = SCREEN_SIZE[1]*.2
MAX_PADDLE_Y = SCREEN_SIZE[1]-PADDLE_HEIGHT
MAX_BALL_Y = SCREEN_SIZE[1] - 16

MIN_BALL_VX = .03*SCREEN_SIZE[0]
PADDLE_SPEED = .04*SCREEN_SIZE[1]
GAME_SPEED = 20
def clamp(minVal, maxVal, x):
	return max(min(x,maxVal),minVal)
def between(a,b,x):
	return min(a,b)<=x<=max(a,b)
sign = lambda x: math.copysign(1, x)

"""
Does not account for case where the ball would have bounced off the wall
"""
def intersection(start_pos,velocity,x):
	end_pos = [sum(pair) for pair in zip(start_pos,velocity)]
	if not between(start_pos[0],end_pos[0],x):
		return False, None
	t=(end_pos[0]-start_pos[0])/float(velocity[0])
	intersect = end_pos[1]+t*velocity[1]
	return True, int(intersect)


class Paddle:
	def __init__(self, position, height, is_left=False):
		self.position = list(position)
		self.height = height
		self.rect = pygame.Rect(*self.position, 12,self.height)
		self.score = 0
		self.is_left = is_left
	def get_surface(self):
		if self.is_left:
			return self.position[0]+12
		else:
			return self.position[0]
	def move(self, dy):
		self.position[1] += dy
		self.position[1] = clamp(0,MAX_PADDLE_Y, self.position[1])
	def draw(self, screen):
		self.rect = pygame.Rect(*self.position, 12,self.height)
		pygame.draw.rect(screen, WHITE, self.rect)
	def intersection(self, ball):
		did_intersect, y = intersection(ball.position,ball.velocity,self.get_surface())
		if not did_intersect:
			return False, None

		#Successful bounce
		if between(self.position[1],self.position[1]+self.height,y):
			ball.position[0] = 2*self.get_surface()-ball.position[0]
			ball.velocity[0]*=-1
			u = (random()-.5)*.03*SCREEN_SIZE[0]
			v = (random()-.5)*.05*SCREEN_SIZE[1]
			ball.velocity[0]+=u
			ball.velocity[1]+=v
			self.score+=1
			return True, y
		#Miss
		return False, y

class Ball:
	def __init__(self, startPosition):
		self.position = list(startPosition)
		self.radius = 8

		self.velocity = [.03*SCREEN_SIZE[0],.01*SCREEN_SIZE[1]]
		self.rect = pygame.Rect(*self.position, 8,8)

	def draw(self, screen):
		pygame.draw.circle(screen, RED, [int(x) for x in self.position], 8)
	def move(self):
		self.check_velocity()
		self.position = [sum(pair) for pair in zip(self.position,self.velocity)]
		if self.position[1] < 0:
			self.velocity[1] *= -1
			self.position[1] *= -1
		if self.position[1] > SCREEN_SIZE[1]:
			self.velocity[1] *=-1
			self.position[1] = 2*SCREEN_SIZE[1] - self.position[1]
	def check_velocity(self):
		if self.velocity[0] < MIN_BALL_VX:
			self.velocity[0] = sign(self.velocity[0])*MIN_BALL_VX
class AI:
	def __init__(self, player_index):
		"""
		State:
			Ball x: Index from 0 to 11
			Ball y: Index from 0 to 11
			Vel x: -1 or +1
			Vel y: -1, 0, 1
			Pos: 	Index from 0 to 11
		
		Actions:
			0:  Move up
			1:  Stay still
			2:  Move down
		"""
		# Learning rate
		self.alpha = .5
		# Discount factor
		self.gamma = .6
		self.player_index = player_index
		
		self.qmatrix = defaultdict(lambda:[0,0,0])
		self.reset()		
		
	def reset(self):
		self.state = (5,5,-1,1,5)
		self.prev_state = self.state
		self.prev_action = 1

	def interpret_state(self,pong):
		self.prev_state = self.state
		self.state = [0,0,0,0,0]
		self.state[0] = int(pong.ball.position[0]/SCREEN_SIZE[0]*12)
		self.state[1] = int(pong.ball.position[1]/SCREEN_SIZE[1]*12)
		self.state[2] = sign(pong.ball.velocity[0])
		if abs(pong.ball.velocity[1]) < .015*SCREEN_SIZE[1]:
			self.state[3] = 0
		else:
			self.state[3] = sign(pong.ball.velocity[1])
		self.state[4] = int(pong.players[self.player_index].position[1]/SCREEN_SIZE[1]*12) 
		self.state = tuple(self.state)
	def choose_action(self):
		q = self.qmatrix[tuple(self.state)]
		q = [action+random()*.001 for action in q]
		a = q.index(max(q))
		self.prev_action = a
		return a
		#q = (1-self.alpha) + gamma*max(q_old)
	def reward(self,pong,r):
		self.interpret_state(pong)
		self.qmatrix[self.prev_state][self.prev_action]+= (1-self.alpha)*(r+self.gamma*self.QMax(self.state)-self.qmatrix[self.prev_state][self.prev_action])
	def lookup(self, state, action):
		return self.qmatrix(tuple(state))[action]
	def QMax(self, state):
		return max(self.qmatrix[state])
	def eq_constraint(self):
		return

class Pong:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((640,480))
		pygame.display.set_caption("Pong")
		self.clock = pygame.time.Clock()
		self.players = []
		self.AI = AI(0)
		self.iteration = 0;
		self.scores = []
		self.init_game()
	def init_game(self):
		old_scores = []
		#if self.players:
		#	old_scores = [player.score for player in self.players]
		self.players = [Paddle((SCREEN_SIZE[0]-12,210),PADDLE_HEIGHT), 
						Paddle((0,0),480,True)]
		#if old_scores:
		#	for i, score in enumerate(old_scores):
		#		self.players[i].score = score
		self.ball = Ball((320,240))
		self.AI.reset()
	def draw_objects(self):
		for paddle in self.players:
			paddle.draw(self.screen)
		self.ball.draw(self.screen)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			self.clock.tick(GAME_SPEED)
			self.screen.fill(BLACK)
			self.handle_inputs()
			self.handle_physics()
			self.draw_objects()
			pygame.display.flip()
	def handle_AI(self):
		#self.AI.interpret_state(self)
		return self.AI.choose_action()
	def handle_inputs(self):
		global GAME_SPEED
		action = self.handle_AI()-1
		self.players[0].move(action*.04*SCREEN_SIZE[1])
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]:
			self.players[0].move(-5)
		if keys[pygame.K_DOWN]:
			self.players[0].move(5)
		if keys[pygame.K_b]:
			print(self.ball.position)
		if keys[pygame.K_LEFTBRACKET]:
			GAME_SPEED=GAME_SPEED*1.1
		if keys[pygame.K_RIGHTBRACKET]:
			GAME_SPEED=GAME_SPEED*.9
		return
	def handle_physics(self):
		self.ball.move()
		for i,player in enumerate(self.players):
			caught, y = player.intersection(self.ball)

			if (not caught and y != None) or (self.ball.position[0] > SCREEN_SIZE[0]*1.1):
				if i == 0:
					self.AI.reward(self,-1)
					self.iteration+=1
					self.scores.append(self.players[0].score)
					print("Iteration {0}: {1}".format(self.iteration, self.players[0].score))
				self.init_game()
			elif caught:
				if i == 0:
					self.AI.reward(self,1)
			else:
				self.AI.reward(self,0)
def print_dict(d):
	for key, value in d.items():
		print("{0}:{1}".format(key,value))
if __name__ == "__main__":
	Pong().run()