# spike source spike once, SMT last for some time

import time
import os
import random
from AutoCAFun2 import *

file_directory = os.path.dirname(os.path.realpath(__file__))
files_in_directory = os.listdir(file_directory)
filtered_files = [file for file in files_in_directory if file.endswith(".png")]
for file in filtered_files:
    path_to_file = os.path.join(file_directory, file)
    os.remove(path_to_file)
filtered_files = [file for file in files_in_directory if file.endswith(".txt")]
for file in filtered_files:
    path_to_file = os.path.join(file_directory, file)
    os.remove(path_to_file)

save_fig = 1

sim_duration = 2000
weight_spike = 0.9
weight_neuron = 0.001

conn_spike = 10
conn_neuron = 6

seed = 100
random.seed(seed)

num_spike = 1  # number of spike generator and CA
num_neuron = 100  # number of neurons in each CA

spike_series = [100]
conn_spike_file = 'oneSpikeSpikes'
conn_neuron_file = 'oneSpikeConn'

spike_matrix = []
neuron_matrix = []

# spikes to neuron
for i in range(conn_spike):
    spike_matrix.append([i, weight_spike])


def run_base():
    conn_temp = conn_small_ws(num_neuron, conn_neuron)  # small world
    for i in range(len(conn_temp)):
        neuron_matrix.append([])
        for j in conn_temp[i]:
            neuron_matrix[i].append([j[0], weight_neuron])

    import pyNN.nest as sim
    import pyNN.utility.plotting as pyplotting

    start_time = time.time()
    sim.setup(timestep=0.1)

    spike_time = {'spike_times': spike_series}
    spikes = sim.Population(num_spike, sim.SpikeSourceArray, spike_time)
    neurons = sim.Population(num_neuron, sim.IF_cond_exp, {})

    sim.reset()

    syn_spike = []
    for i in spike_matrix:
        syn_spike.append((0, i[0], i[1], 1.0))
    conn_list = sim.FromListConnector(syn_spike)
    sim.Projection(spikes, neurons, conn_list)

    syn_temp = []
    for i in range(len(neuron_matrix)):
        for j in neuron_matrix[i]:
            syn_temp.append((i, j[0], j[1], 1.0))
    conn_list = sim.FromListConnector(syn_temp)
    sim.Projection(neurons, neurons, conn_list)

    spikes.record('spikes')
    neurons.record('spikes')

    sim.run(sim_duration)
    data_spike = spikes.get_data().segments[0]
    data_neuron = neurons.get_data().segments[0]
    #    data_neuron_v = neurons.get_data().segments[0].filter(name='spikes')[0]
   # spike_save(data_neuron.spiketrains, conn_spike_file + str('%.3f' % weight_neuron) + '.txt')
    sim.end()

    if save_fig == 1:
        pyplotting.Figure(pyplotting.Panel(data_spike.spiketrains, xticks=True, yticks=True),
                          pyplotting.Panel(data_neuron.spiketrains, xticks=True, yticks=True)).save(
            'ipi 2 ' + str('%.3f' % weight_neuron) + '.png')

    end_time = time.time()
    print str(round(end_time - start_time, 2)) + ' seconds'


##
for i in range(100, 1000, 100):
    weight_neuron = float(i) / 10000
    print weight_neuron
    run_base()
