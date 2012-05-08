#-*- coding: utf8 -*-

from neuro import Neuro
from exceptions import Exception
import random
import time
import math

class NeuroNet():
    """
    Представляет нейронную сеть
    """
    def __init__(self):
        self.neuros = []
        self.teta = 1
        
    def learn(self, input_vectors, output_vectors):
        for i in xrange(len(input_vectors)):
            print('\n' * 8 + 'NEW VECTOR!\n' * 8)
            next_vector = False
            self.teta = 1.0
            delta = [0 for x in xrange(len(self.neuros[-1]))]
            old_delta = [0 for x in xrange(len(self.neuros[-1]))]
            error = 0.0
            while not next_vector:
                #For DEBUG
                print(error)
                print(delta)
                #time.sleep(1)
                #---------
                returned = self.calc(input_vectors[i])
                delta = [output_vectors[i][j] - returned[j] for j in xrange(len(returned))]
                norm = sum([math.sqrt(delta[y]) for y in xrange(len(delta))])
                error = max([delta[x] / norm for x in xrange(len(delta))])
                #old_delta = delta
                if math.fabs(error) < 0.001:
                    self.teta /= 2
                if self.teta <= 0.001:
                    next_vector = True
                else:
                    self.recalc(delta, len(self.neuros) - 1)
    
    def recalc(self, delta, neuron_layer_number):
        if (neuron_layer_number == -1): return
        new_delta_vector = []
        for neuron_number in xrange(len(self.neuros[neuron_layer_number])):
            for weight_number in xrange(len(self.neuros[neuron_layer_number][neuron_number].weights)):
                weight = self.neuros[neuron_layer_number][neuron_number].weights[weight_number]
                sigma = weight * (1 - weight) * (delta[neuron_number] - weight)
                new_delta = self.teta * sigma * weight
                try:
                    new_delta_vector[weight_number] += new_delta
                except Exception:
                    new_delta_vector.append(new_delta)
                self.neuros[neuron_layer_number][neuron_number].weights[weight_number] += new_delta
        print("New Epoch: ")
        print(self)
        self.recalc(new_delta_vector, neuron_layer_number - 1)
    
    def calc(self, input_bites):
        self.cleaning()
        for x in xrange(len(self.neuros[0])):
            self.neuros[0][x].in_neuros = input_bites
        for neuro_level in xrange(len(self.neuros)):
            try:
                for neuro in self.neuros[neuro_level]:
                    for neuro_from_next_level in self.neuros[neuro_level + 1]:
                        neuro_from_next_level.in_neuros.append(int(neuro.is_activated()))
            except Exception:
                return [int(x.is_activated()) for x in self.neuros[neuro_level]]
    
    def cleaning(self):
        for neuro_level in self.neuros:
            for neuro in neuro_level:
                neuro.clean()
    
    def __str__(self):
        result_string = ''
        for neuro_layer in self.neuros:
            result_string += "Layer => "
            for neuro in neuro_layer:
                result_string += neuro.__str__() + '\n'
        return result_string
    
    
def generate(layers):
    nn = NeuroNet()
    for layer_num in xrange(len(layers) - 1):
        nn.neuros.append([])
        for i in xrange(layers[layer_num + 1]):
            nn.neuros[layer_num].append(Neuro())
            nn.neuros[layer_num][i].weights = [random.random() for x in xrange(layers[layer_num])]
    return nn