#-*- coding: utf8 -*-

from math import exp
import random

class Neuro:
    """
    Представляет один нейрон
    """
    def __init__(self):
        self.in_neuros = []
        self.weights = []
        self.activation = random.random()
        
    def activation_function(self, x):
        return 1.0/(1.0 + exp(-x))
        
    def calc(self):
        return sum(self.in_neuros[x] * self.weights[x] for x in xrange(len(self.in_neuros)))
        
    def is_activated(self):
        return (self.activation_function(self.calc()) >= self.activation)
        
    def clean(self):
        self.in_neuros = []
        
    def __str__(self):
        result_str = "Neuron, input weights: %d, activity: %f" % (len(self.weights), self.activation)
        for input_weight in self.weights:
            result_str += "\n\tInput weight: %f" % input_weight
        return result_str