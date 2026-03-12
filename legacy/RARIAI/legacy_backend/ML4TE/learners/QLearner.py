"""
Template for implementing QLearner  (c) 2015 Tucker Balch

Copyright 2018, Georgia Institute of Technology (Georgia Tech)
Atlanta, Georgia 30332
All Rights Reserved

Template code for CS 4646/7646

Georgia Tech asserts copyright ownership of this template and all derivative
works, including solutions to the projects assigned in this course. Students
and other users of this template code are advised not to share it with others
or to make it available on publicly viewable websites including repositories
such as github and gitlab.  This copyright statement should not be removed
or edited.

We do grant permission to share solutions privately with non-students such
as potential employers. However, sharing with other current or future
students of CS 7646 is prohibited and subject to being investigated as a
GT honor code violation.

-----do not edit anything above this line---

Student Name: Alexander Ferrara
GT User ID: aferrara3
GT ID: 902890849
"""

import numpy as np
import random as rand

class QLearner(object):

	def __init__(self, \
		num_states=100, \
		num_actions = 4, \
		alpha = 0.2, \
		gamma = 0.9, \
		rar = 0.5, \
		radr = 0.99, \
		dyna = 0, \
		verbose = False):

		self.verbose = verbose
		self.num_actions = num_actions
		self.s = 0
		self.a = 0

		self.num_states=num_states
		self.alpha = alpha
		self.gamma = gamma
		self.rar = rar
		self.radr = radr
		self.dyna = dyna

		#self.q = np.random.uniform(-1.0,1.0,size=(num_states,num_actions))
		self.q = np.zeros(shape=(num_states,num_actions)) # seems to be marginally better for early convergence + less RNGesus

		#Dyna Setup
#		T[s,a,s'] => probability that if in state s and take action a that you end up in s'
#		init TC[] = 0.00001
#		print(num_states, num_actions, num_states)
		self.TC = np.ones(shape=(num_states, num_actions, num_states)) * 0.0001
		self.T 	= np.zeros(shape=(num_states, num_actions, num_states))
#		R[s,a] expected reward for s,a
#		r immediate reward in experience tuple
		self.R 	= np.zeros(shape=(num_states, num_actions))

	def querysetstate(self, s):
		"""
		@summary: Update the state without updating the Q-table
		@param s: The new state
		@returns: The selected action
		"""
		self.s = s

		if rand.random() < self.rar:
			action = rand.randint(0, self.num_actions-1)
		else:
			action = np.argmax(self.q[s])

		if self.verbose:
			print("s =", s,"a =",action)
			print(self.q[self.s,:])

		self.a = action # should update here? Need to ask Piazza/Slack
		return action

	def query(self,s_prime,r):
		"""
		@summary: Update the Q table and return an action
		@param s_prime: The new state
		@param r: The ne state
		@returns: The selected action
		"""
		#print "S:", type(self.s)
		#print "A:", type(self.a)
		#print "R:", type(r)
		#print self.q
		# Update rule : Q'[s,a] = (1 - alpha) * Q[s, a] + alpha * (r + gamma * Q[s', argmaxa'(Q[s', a'])]) #
		self.q[self.s,self.a] = (1-self.alpha) * self.q[self.s,self.a] + self.alpha * (r + self.gamma * self.q[s_prime,np.argmax(self.q[s_prime])])

		if rand.random() < self.rar:
			action = rand.randint(0, self.num_actions-1)
		else:
			action = np.argmax(self.q[s_prime])

		if self.verbose:
			print("s =", s_prime,"a =",action,"r =",r)
			print(self.q[self.s,:])

		# Implement some dyna shit here
		if self.dyna > 0:
#			Learn model (T, R)
#			T'[s,a,s'] update
#				while executing, observe s,a,s'
#				increment TC[s,a,s']
			self.TC[self.s, self.a, s_prime] += 1
#				T[s,a,s'] = TC[s,a,s'] / SUM_i(TC[s,a,i]
			self.T[self.s, self.a, s_prime] = self.TC[self.s,self.a,s_prime] / np.sum(self.TC[self.s,self.a,:])
#			R'[s,a] update
#				R'[s,a]=(1-alpha)*R[s,a] + alpha*r
			self.R[self.s,self.a] = (1-self.alpha) * self.R[self.s,self.a] + self.alpha*r
			rndm_s = np.random.randint(self.num_states, size=(self.dyna))
			rndm_a = np.random.randint(self.num_actions, size=(self.dyna))
#			Hallucinate Experience
			for i in range(0,self.dyna):
#				s = random
				#s = rand.randint(0, self.num_states-1)
				s = rndm_s[i]
#				a = random
				#a = rand.randint(0, self.num_actions-1)
				a = rndm_a[i]
				# No sense in updating if there isn't any real experience to learn from yet
				#print np.sum(self.T[s,a,:])
				if np.sum(self.T[s,a,:])!=0:
#					s' = infer from T[]
#					Need to find most common s_prime from T (argmax?) for given <s,a>
					s_prime_dyna = np.argmax(self.T[s,a,:])
#					r = R[s,a]
					r = self.R[s,a]
#				Update Q with hallucincated tuple
					self.q[s,a] = (1-self.alpha) * self.q[s,a] + self.alpha * (r + self.gamma * self.q[s_prime_dyna,np.argmax(self.q[s_prime_dyna])])

		self.a = action
		self.s = s_prime
		self.rar = self.rar*self.radr
		return action

	def author(self):
		return 'aferrara3'

if __name__=="__main__":
	print("Remember Q from Star Trek? Well, this isn't him")
