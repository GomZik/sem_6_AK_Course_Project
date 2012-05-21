#-*- coding: utf-8 -*-

import random
import math
import time
import exceptions

class Neuron:
    def __init__(self):
        self.inputs = []
        self.weights = []
        self.output = 0.0
        self.activation = random.random()
        self.teta = 0.5
        
    def activation_func(self, x):
        return 1.0 / (1.0 + math.exp(x))
    
    def set_inputs(self, inputs):
        self.inputs = inputs
    
    def calc(self):
        self.output = float(sum([float(self.inputs[i]) * self.weights[i] for i in xrange(len(self.inputs))]))
        return self.output
    
    def is_activated(self):
        return (self.output >= self.activation)

class NeuronLayerType:
        HIDDEN_LAYER = 1
        OUT_LAYER = 2

class NeuronLayer(list):
    def __init__(self, neurons = [], layer_type = NeuronLayerType.HIDDEN_LAYER):
        list.__init__(self)
        self += neurons
        self.type = layer_type
    
    def learn(self, delta):
        pass
    
class NeuronNetwork:
    def __init__(self):
        self.layers = []
        
    def __str__(self):
        result_str = ''
        for layer in self.layers:
            result_str += 'Layer, type: %d => %d neurons:\n' % (layer.type, len(layer))
            for neuron in layer:
                result_str += '\tNeuron => inputs %d' % len(neuron.weights) + '\n'
                for weight in neuron.weights:
                    result_str += '\t\tInput => weight: %f' % weight + '\n'
        return result_str
    
    def get_all_weights(self):
        result = []
        for layer in self.layers:
            result.append([])
            for neuron in layer:
                result[-1].append(neuron.weights)
        return result
    
    def get_decompress_weights(self):
        result = []
        for neuron in self.layers[1]:
            result.append(neuron.weights)
        return result
    
    def get_compressed_data(self):
        return list([neuron.output for neuron in self.layers[0]])
    
    def set_decompress_weights(self, weights):
        for x in xrange(len(weights)):
            self.layers[-1][x].weights = weights[x]
    
    def calculate(self, inputs):
        layer_output = inputs
        for layer in self.layers:
            tmp_layer_output = []
            for neuron in layer:
                neuron.set_inputs(layer_output)
                tmp_layer_output.append(neuron.calc())
            layer_output = tmp_layer_output
        result = []
        for neuron in self.layers[-1]:
            result.append(float(neuron.output))
        return result
    
    def learn(self, pairs, max_error = 0.01):
        for pair in pairs:
            is_done = False
            while not is_done:
                result = self.calculate(pair[0])
                delta = [float(result[i]) - float(pair[1][i]) for i in xrange(len(result))]
                alpha = 1.0 / sum([neuron.output**2 for neuron in self.layers[0]])
                for neuron_num in xrange(len(self.layers[1])):
                    for weight_num in xrange(len(self.layers[1][neuron_num].weights)):
                        self.layers[1][neuron_num].weights[weight_num] -= alpha * self.layers[0][weight_num].output * delta[neuron_num]
                alpha = 1.0 / sum([float(x)**2 for x in pair[1]])
                for neuron_num in xrange(len(self.layers[0])):
                    for weight_num in xrange(len(self.layers[0][neuron_num].weights)):
                        self.layers[0][neuron_num].weights[weight_num] -= alpha * pair[1][weight_num] * delta[weight_num] * self.layers[1][weight_num].weights[neuron_num]
                error = float(sum([x**2 for x in delta]))
                for neuron in self.layers[0]:
                    m1 = math.sqrt(sum([weight**2 for weight in neuron.weights]))
                    for weight_num in xrange(len(neuron.weights)):
                        neuron.weights[weight_num] /= m1
                for neuron in self.layers[1]:
                    m2 = math.sqrt(sum([weight**2 for weight in neuron.weights]))
                    for weight_num in xrange(len(neuron.weights)):
                        neuron.weights[weight_num] /= m2
                #print self
                #print 'error %f, max error %f' % (error, max_error)
                #time.sleep(0.1)
                if error <= max_error: is_done = True
    
def generate(layers):
    nn = NeuronNetwork()
    for layer_number in xrange(1, len(layers)):
        tmp_layer = NeuronLayer()
        if layer_number == len(layers) - 1:
            tmp_layer.type = NeuronLayerType.OUT_LAYER
        for neuron_number in xrange(layers[layer_number]):
            tmp_neuron = Neuron()
            for prev_layer_neuron_number in xrange(layers[layer_number - 1]):
                tmp_neuron.weights.append(random.random())
            tmp_layer.append(tmp_neuron)
        nn.layers.append(tmp_layer)
    return nn
        
if __name__ == '__main__':
    nn = generate(
        (8, 4, 8)
    )
    print nn
    nn.learn(
        [
            [
                [1, 0] * 4,
                [1, 0] * 4,
            ],
        ]
    )
    print nn.calculate([1,0] * 4)