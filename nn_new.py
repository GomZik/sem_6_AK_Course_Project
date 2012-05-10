#-*- coding: utf-8 -*-

import random
import math

#from PyQt4.QtCore import *
#from PyQt4.QtGui import *
#import sys

class Neuron:
    def __init__(self):
        self.inputs = [1, ]
        self.weights = [random.random(), ]
        self.output = 0.0
        
    def activation_func(x):
        return math.tanh(x)
        
    def learn(koef):
        pass
    
class NeuronNetwork:
    def __init__(self):
        self.neurons = []
        self.learn_koef = 1.0
        
def generate(layers):
    pass
        
if __name__ == '__main__':
    pass
#    app = QApplication(sys.argv)
#    window = QWidget()
#    window.show()
#    app.exec_()