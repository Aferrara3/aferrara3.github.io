import numpy as np
from scipy import stats

class RTLearner(object):

	def __init__(self, leaf_size = 1, verbose = False):
		self.leaf_size = leaf_size
		self.dt = np.array([])
		pass

	def author(self):
		return 'aferrara3'

	def addEvidence(self,dataX,dataY):
#		breakpoint()
		self.dt = self.build_tree(dataX,dataY)

	def build_tree(self,dataX,dataY):
#		breakpoint()
		if	dataX.shape[0] <= self.leaf_size:
			#breakpoint()
			return	np.array([[-1,stats.mode(dataY)[0][0][0], -1, -1]])
#		print(dataY)
#		print(dataY.head(1))
#		print(dataY == dataY.head(1).ix[:,:].to_numpy())
		if	np.all(dataY == dataY[0]):
			return	np.array([[-1, dataY[0], -1, -1]])
		else:
			i = int(np.random.random(1)[0] * np.shape(dataX)[1])
			SplitVal = (np.random.choice(dataX[:,i])+np.random.choice(dataX[:,i]))/2
			#Fix for corner case in the event that all vals are <= SplitVal
			if (SplitVal == np.max(dataX[:,i])):
				SplitVal = np.min(dataX[:,i])
			lefttree = self.build_tree(dataX[dataX[:,i]<=SplitVal],dataY[dataX[:,i]<=SplitVal])
			righttree =	self.build_tree(dataX[dataX[:,i]>SplitVal],dataY[dataX[:,i]>SplitVal])
			root = np.array([i, SplitVal, 1, lefttree.shape[0] + 1])
			out = np.vstack((root, lefttree, righttree))
			return	out

	def query(self,points):
		out = np.array([])
		dt = self.dt
		for point in points:
			j = 0;
			while 1:
				factor = int(dt[j][0])
				SplitVal = dt[j][1]
				if factor == -1:
					out = np.append(out,SplitVal)
					break
				x = point[factor]
				if x <= SplitVal:
					j = int(j + dt[j][2])
					continue
				j = int(j + dt[j][3])
		return out

if __name__=="__main__":
	print("the secret clue is 'zzyzx'")
