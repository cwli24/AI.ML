import numpy, random, math
from scipy.optimize import minimize
import matplotlib.pyplot as plt

classA = numpy.concatenate((
    numpy.random.randn(20, 2) * 0.2 + [0.0, -1.0],
    numpy.random.randn(20, 2) * 0.2 + [-1.0, 0.0],
    numpy.random.randn(20, 2) *0.2 + [1.5,2]))
classB = numpy.random.randn(40, 2) * 0.2 + [0.0 , -0.5]

inputs = numpy.concatenate((classA , classB))
targets = numpy.concatenate(
(numpy.ones(classA.shape[0]), 
-numpy.ones(classB.shape[0])))

N = inputs.shape[0] # Number of rows (samples)
C = 100.0

permute=list (range(N))
random.shuffle(permute)
inputs = inputs[permute, :]
targets = targets [permute]

def linearKernel(xArr, yArr):
    return numpy.dot(xArr, yArr)

def polynomialKernel(xArr, yArr, p):
	return (numpy.dot(xArr, yArr) + 1)**p

def radialBFKernel(xArr, yArr, sigma):
	return math.exp(-numpy.linalg.norm(xArr - yArr)**2 / (2*sigma**2))

def kernelFunc(a, b):
	return radialBFKernel(a, b, 2)	#change this line to whichever kernel to use
P = numpy.array([[targets[i]*targets[j] * kernelFunc(inputs[i], inputs[j]) for j in range(N)] for i in range(N)]) 

def objective(alpha):
    return .5 * numpy.dot(alpha, numpy.dot(P, alpha)) - numpy.sum(alpha)

def zerofun(alpha):
    return numpy.dot(alpha, targets)

def b(alpha):
    svs = alpha[alpha > 10**-7]
    sv_indices = numpy.array(range(N))[alpha > 10**-7]

    is_on_margin = ~numpy.isclose(svs, [C]*len(svs))
    svom_ind = sv_indices[is_on_margin]
    svnom_ind = sv_indices[~is_on_margin]

    b = 0.0
    for i in sv_indices:
    	b += alpha[i] * targets[i] * kernelFunc(inputs[svom_ind[0]], inputs[i])

    return b - targets[svom_ind[0]]

def indicator(alpha, s, b):
    supportVectors = numpy.logical_and(alpha > 10**-5, alpha < (C - 10**-10))

    r = numpy.array(range(N))
    indices = r[supportVectors]
    
    ind = .0
    for i in indices:
        ind += alpha[i] * targets[i] * kernelFunc(s, inputs[i])

    return ind - b

start = numpy.zeros(N)
B = [(0, C) for i in range(N)]
XC = {'type':'eq', 'fun':zerofun}

ret = minimize(objective, start, bounds=B, constraints=XC)
alpha = ret['x']

bVal = b(alpha)

# for i in range(len(classB)):
#     print(indicator(alpha, classB[i]))

plt.plot([p[0] for p in classA], [p[1] for p in classA], 'b.')
plt.plot([p[0] for p in classB], [p[1] for p in classB], 'r.')

plt.axis('equal')

xgrid=numpy.linspace(-5, 5) 
ygrid=numpy.linspace(-4, 4)

grid=numpy.array([[indicator(alpha, (x, y), bVal) for x in xgrid ] for y in ygrid])

plt.contour(xgrid, ygrid, grid, 
            (-1.0, 0.0, 1.0),
            colors=('red', 'black', 'blue'),
            linewidths=(1, 3, 1))

#plt.savefig('svmplot.pdf')
plt.show()
