import numpy as np

class DTLearner(object):

	def __init__(self, leaf_size = 1, verbose = False):
		self.leaf_size = leaf_size
		self.dt = np.array([])
		pass

	def author(self):
		return 'aferrara3'

	def addEvidence(self,dataX,dataY):
		self.dt = self.build_tree(dataX,dataY)
		
	def build_tree(self,dataX,dataY):
		if	dataX.shape[0] <= self.leaf_size:	
			return	np.array([[-1,np.mean(dataY), -1, -1]])
		if	np.all(dataY == dataY[0]):	
			return	np.array([[-1, dataY[0], -1, -1]])
		else:
			i = self.best_i(dataX,dataY)
			SplitVal = np.median(dataX[:,i])
			
			#Fix for corner case in the event that all vals are <= median
			if (SplitVal == np.max(dataX[:,i])):
				SplitVal = np.min(dataX[:,i])
				
			lefttree = self.build_tree(dataX[dataX[:,i]<=SplitVal],dataY[dataX[:,i]<=SplitVal])
			righttree =	self.build_tree(dataX[dataX[:,i]>SplitVal],dataY[dataX[:,i]>SplitVal])		
			root = np.array([i, SplitVal, 1, lefttree.shape[0] + 1])	
			out = np.vstack((root, lefttree, righttree))
			return	out
	
	def best_i(self,dataX,dataY):
		max_coeff=0
		for j in range(0,dataX.shape[1]):
			col = dataX.T[j,:]
			if np.all(col == col[0]):
			 coeff = 0
			else: 
				coeff = np.corrcoef(col,dataY)[0,1]
			#Used >= to be deterministic to use rightmost column in event of tie between corrcoeff
			if (abs(coeff)>=max_coeff): 
				i = j
				max_coeff = abs(coeff)
		return i

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