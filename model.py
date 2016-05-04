from collections import defaultdict
import numpy as np
import pandas as pd
from math import log

class ModelPersist:
	score = defaultdict(lambda: 0)
	ranking_weights = np.arange(1,1.5,0.05)
	visited = set()
	def __init__(self):
		#self.score = defaultdict(lambda: 0)
		self.score[730] = 1.0
		self.bestgame = 730
		self.num_owners = 0
		self.highest_score = 1
		self.names = {730 : 'Counter-Strike: Global Offensive'}

	def update(self, df, game_count, uid):
		if( uid in self.visited):
			return
		self.visited.add(uid)
		for index, row in df.iterrows():
			incr = log(int(row['Owners']),64.0)*log(game_count,10.0)*1.0
			if index < 10:
				incr *= self.ranking_weights[index]
			self.score[row['AppId']] += incr
			self.names[row['AppId']] = row['Title']
			# print "current score: %f | current best: %f" % (self.score[row['AppId']], self.highest_score)
			# print "current game: %s | best game: %s" % (row['Title'],self.names[self.bestgame])
			# print "current num_owners: %d | best num_owners: %d" % (int(row['Owners']), self.num_owners)
			if float(self.score[row['AppId']]) > float(self.highest_score):
				self.highest_score = self.score[row['AppId']]
				self.bestgame = row['AppId']
				self.num_owners = row['Owners']
			if float(self.score[row['AppId']]) == float(self.highest_score):
				if int(row['Owners']) > self.num_owners:
					self.highest_score = self.score[row['AppId']]
					self.bestgame = row['AppId']
					self.num_owners = row['Owners']

	def get_highest_score(self):
		return self.highest_score

	def print_all_scores(self):
		for key, value in self.score.iteritems():
			print "key: %d | name: %s | value: %d" % (key, self.names[key], value)

	def get_best_game(self):
		return self.best_game

	def get_tuple(self):
		return (404, "err:nogame", self.bestgame,self.names[self.bestgame])