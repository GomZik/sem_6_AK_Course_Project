#-*- coding: utf8 -*-

from neuronet import generate

my_neuro_net = generate(
    (8, 3, 3, 8)
)
vectors = (
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,1,1],
)
print("Learning...")
my_neuro_net.learn(vectors, vectors)
print("Done.")
print("testing on data 11100111")
print(my_neuro_net.calc(
    [1,1,1,0,0,1,1,1],
))