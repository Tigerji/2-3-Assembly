# 1. Set binary neuron network (single neuron cluster)
# 2. Start pynn simulation, record spikes and neuron_matrix
# 3. next increase number from 1 to 10

import random
import time
import os
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

delay = 1.0
sim_duration = 1000
num_spike = 1  # number of spike generator and CA
num_neuron = 10  # number of neurons in each CA

random_seed = 1000
random.seed(random_seed)

weight_spike = 0.12  # weight from spike to neuron

spike_series = [100, 120, 140, 160, 180, 200, 220, 240, 260, 280]  # spike time

conn_spike_file = 'demoSpike3'
conn_neuron_file = 'demoNeuron3'

spike_matrix = []
neuron_matrix = []

for i in range(num_spike):
    # spikes to neuron
    spike_matrix[i].append([i, weight_spike])

    # neuron to neuron
    target_neurons = range(num_spike)
    target_neurons.remove(i)
    for j in target_neurons:
        if (i * j) == 0 or (i * j == 2) or (i * j == 12):  # 0>1234, 1>02, 2>01, 3>04, 4>03
            neuron_matrix[i].append([j, weight_conn])


def run_base(trial='a', run_number=0):
    import pyNN.nest as sim
    import pyNN.utility.plotting as pyplotting

    start_time = time.time()
    sim.setup(timestep=0.1)

    spike_time = spike_gen(trial, spike_series)
    spikes = sim.Population(num_spike, sim.SpikeSourceArray, spike_time)
    neurons = sim.Population((num_neuron * num_spike + num_spike), sim.IF_cond_exp, {})

    sim.reset()

    connector = connector_load(spike_matrix)
    conn_list = sim.FromListConnector(connector)
    sim.Projection(spikes, neurons, conn_list)

    connector = connector_load(neuron_matrix)
    conn_list = sim.FromListConnector(connector)
    sim.Projection(neurons, neurons, conn_list)

    spikes.record('spikes')
    neurons.record('v', sampling_interval=0.1)

    sim.run(sim_duration)
    data_spike = spikes.get_data().segments[0]
    data_neuron = neurons.get_data().segments[0]
    spike_save(data_neuron.spiketrains, conn_spike_file + '_' + trial + '.txt')
    conn_save(neuron_matrix, conn_neuron_file + '_' + trial + '.txt')
    sim.end()
    if save_fig == 1:
        pyplotting.Figure(pyplotting.Panel(data_spike.spiketrains, xticks=True, yticks=True),
                          pyplotting.Panel(data_neuron.spiketrains, xticks=True, yticks=True)).save(
            'demo ' + str(len(trial)) + ' ' + trial + '.png')

    end_time = time.time()
    print str(round(end_time - start_time, 2)) + ' seconds'


# print neuron_matrix
for i in range(1):
    run_base('a')
    run_base('b')
    run_base('c')
    run_base('d')
    run_base('e')
    run_base('ab')
    run_base('ac')
    run_base('bc')
    run_base('ad')
    run_base('ae')
    run_base('de')
    run_base('bd')
    run_base('be')
    run_base('cd')
    run_base('ce')

# print neuron_matrix
# neuron_matrix = run_analysis()
# print neuron_matrix

duration = 1  # seconds
freq = 440  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
