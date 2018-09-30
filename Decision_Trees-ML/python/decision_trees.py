#!/usr/bin/env python
import monkdata as df
import dtree as pf
import drawtree_qt5 as qt5
import random
import matplotlib.pyplot as plt

def partition(data, fraction):
	ldata = list(data)
	random.shuffle(ldata)
	breakPoint = int(len(ldata) * fraction)
	return ldata[:breakPoint], ldata[breakPoint:]

# print("MONK1")
# for i in range(6):
# 	print "A%d = %f" %(i+1, pf.averageGain(df.monk1, df.attributes[i]))
# print("MONK2")
# for i in range(6):
# 	print "A%d = %f" %(i+1, pf.averageGain(df.monk2, df.attributes[i]))
# print("MONK3")
# for i in range(6):
# 	print "A%d = %f" %(i+1, pf.averageGain(df.monk3, df.attributes[i]))

# for j in range(1, 5):
# 	subtree = pf.select(df.monk1, df.attributes[4], j)
# 	print "SUBTREE FOR A5=%d" % j
# 	for i in range(6):
# 		print "A%d = %f" % (i+1, pf.averageGain(subtree, df.attributes[i]))
# 	print "Most common class for %d subtree: %d" % (j, pf.mostCommon(subtree))
# qt5.drawTree(pf.buildTree(df.monk1, df.attributes, 2))

# t1 = pf.buildTree(df.monk1, df.attributes)
# print(1-pf.check(t1, df.monk1test))
# t2 = pf.buildTree(df.monk2, df.attributes)
# print(1-pf.check(t2, df.monk2test))
# t3 = pf.buildTree(df.monk3, df.attributes)
# print(1-pf.check(t3, df.monk3test))

# print "MONK1"
# for rate in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
# 	runsResults = []
# 	for i in range(10):
# 		monk1train, monk1val = partition(df.monk1, rate)
# 		trainedTree = pf.buildTree(monk1train, df.attributes)
# 		maxCorrectRate = pf.check(trainedTree, monk1val)

# 		while True:
# 			maxCRTIdx = -1
# 			lstTrees = pf.allPruned(trainedTree)
# 			for idx, subtree in enumerate(lstTrees):
# 				if pf.check(subtree, monk1val) >= maxCorrectRate:
# 					maxCorrectRate = pf.check(subtree, monk1val)
# 					maxCRTIdx = idx

# 			if maxCRTIdx == -1:
# 				break
# 			trainedTree = lstTrees[maxCRTIdx]

# 		runsResults.append(round(1-pf.check(trainedTree, df.monk1test), 4))
# 	print "Misclassification fracs for 10 runs of %.1f: " % (rate), runsResults

# print "MONK3"
# for rate in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
# 	runsResults = []
# 	for i in range(10):
# 		monk3train, monk3val = partition(df.monk3, rate)
# 		trainedTree = pf.buildTree(monk3train, df.attributes)
# 		maxCorrectRate = pf.check(trainedTree, monk3val)

# 		while True:
# 			maxCRTIdx = -1
# 			lstTrees = pf.allPruned(trainedTree)
# 			for idx, subtree in enumerate(lstTrees):
# 				if pf.check(subtree, monk3val) >= maxCorrectRate:
# 					maxCorrectRate = pf.check(subtree, monk3val)
# 					maxCRTIdx = idx

# 			if maxCRTIdx == -1:
# 				break
# 			trainedTree = lstTrees[maxCRTIdx]

# 		runsResults.append(round(1-pf.check(trainedTree, df.monk3test), 4))
# 	print "Misclassification fracs for 10 runs of %.1f: " % (rate), runsResults


m1_3 = [0.2222, 0.1944, 0.25, 0.2917, 0.1944, 0.3056, 0.1944, 0.213, 0.2685, 0.1667]
m1_4 = [0.25, 0.125, 0.1759, 0.2917, 0.1667, 0.1944, 0.1806, 0.1667, 0.2083, 0.2083]
m1_5 = [0.1111, 0.1759, 0.1667, 0.25, 0.1944, 0.1944, 0.2639, 0.1319, 0.2569, 0.1667]
m1_6 = [0.2431, 0.1111, 0.2222, 0.2454, 0.1944, 0.1389, 0.1944, 0.2222, 0.2083, 0.213]
m1_7 = [0.2037, 0.25, 0.2037, 0.1111, 0.2222, 0.2222, 0.1667, 0.2037, 0.2407, 0.2639]
m1_8 = [0.2222, 0.1944, 0.1667, 0.2546, 0.1667, 0.2222, 0.2083, 0.1944, 0.1944, 0.2431]
m3_3 = [0.0278, 0.0278, 0.0278, 0.0278, 0.0278, 0.0278, 0.2222, 0.125, 0.0278, 0.1852]
m3_4 = [0.0694, 0.0833, 0.0694, 0.0556, 0.0278, 0.0278, 0.0833, 0.0278, 0.0278, 0.0278]
m3_5 = [0.0278, 0.0278, 0.1111, 0.037, 0.0278, 0.0833, 0.0833, 0.0926, 0.0278, 0.0278]
m3_6 = [0.0556, 0.0556, 0.0278, 0.0278, 0.0278, 0.0278, 0.0278, 0.0833, 0.0556, 0.0926]
m3_7 = [0.0278, 0.1111, 0.0278, 0.0278, 0.0278, 0.0556, 0.0278, 0.0278, 0.037, 0.0833]
m3_8 = [0.0, 0.1296, 0.0, 0.0278, 0.1296, 0.0278, 0.0278, 0.0278, 0.0278, 0.0278]
x = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)

for i in range(10):
	y = (m1_3[i], m1_4[i], m1_5[i], m1_6[i], m1_7[i], m1_8[i])
	plt.plot(x, y,)
plt.xlabel('Train-Validation Partition')
plt.ylabel('Fraction of Misclassifications')
plt.show()
