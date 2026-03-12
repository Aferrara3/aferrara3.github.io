import numpy as np
from ML4TE.learners import DTLearner as dt


#import LinRegLearner as lrl

class BagLearner(object):
	#learner = bl.BagLearner(learner = al.ArbitraryLearner, kwargs = {"argument1":1, "argument2":2}, bags = 20, boost = False, verbose = False)
	def __init__(self, learner = dt.DTLearner, kwargs={}, bags = 1, boost = False, verbose = False):
		self.bags = bags
		self.learners = []
		for i in range(0,bags):
			self.learners.append(learner(**kwargs))
		pass

	def author(self):
		return 'aferrara3'
	
	#learner.addEvidence(Xtrain, Ytrain)
	def addEvidence(self,dataX,dataY):
		for learner in self.learners:
			#3 lines below come from modification of code from below SO forum to arrive at this approach to random selection with replacement:
			#https://stackoverflow.com/questions/14262654/numpy-get-random-set-of-rows-from-2d-array
			#Idk if needed since pretty modified and 3 lines but figured better safe than sorry
			n = dataX.shape[0]
			indices = np.random.randint(n, size=n)
			learner.addEvidence(dataX[indices,:],dataY[indices])		

	#Y = learner.query(Xtest)
	def query(self,points):
		outArr = np.zeros(np.shape(points)[0])
		for learner in self.learners:
			outArr = np.vstack((outArr, learner.query(points)))
		outArr = outArr[1:][:]
		out = np.mean(outArr, axis=0)
		return out
		
if __name__=="__main__":
	print("the secret clue is 'zzyzx'")