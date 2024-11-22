# build a spike-CA simple connection with only excitation connections
# with gradual learning, the CA should reach saturation or a stable state

# 1. Set neuron network parameters, spike_matrix, neuron_matrix(CAs+inhibition)
# 2. Start pynn simulation, record spikes and neuron_matrix
# 3. re-run simulation

inhibitory = 0

import random
import time
import os

from AutoCAFun2 import *

random_seed = 1000
save_fig = 1

delay = 1.0
sim_duration = 1000

net_mode = 2  # 1: random; 2: small world WS; 3: small world Chris
mut_ratio = 0.3  # mutation ratio for small world
num_neuron = 20  # number of neurons in each cluster

conn_spike = 4  # connection from spike to neurons
conn_neuron = 8  # connections from neuron to neurons within CAs

weight_spike = 0.1  # weight from spike to neuron
weight_neuron = 0.01  # starting weight between neurons

weight_max = 0.5  # maximum total weight from an excitation neuron

spike_margin = 20  # checking whether there are spikes within 20 ms
update_steps = 20  # determines how fast weight updates

spike_series = [100, 120, 140, 160, 180, 200, 220, 240, 260, 280]  # spike time

conn_spike_file = 'demoSpikeAutoCA.txt'
conn_neuron_file = 'demoNeuronAutoCA.txt'

neuron_group = range(num_neuron)

if net_mode == 2:
    neuron_group = range(num_neuron)

    # excitation connections within CA
    target_group = conn_small_ws(num_neuron, conn_neuron, mut_ratio)
    print target_group
    for j in neuron_group:
        target_neurons = target_group[j]
        for s in target_neurons:
            neuron_matrix[j + i * num_neuron].append([s[0] + i * num_neuron, weight_neuron])

    # inhibition connections
