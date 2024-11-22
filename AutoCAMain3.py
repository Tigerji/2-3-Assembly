# 1. Set neuron network parameters, spike_matrix, neuron_matrix(CAs+inhibition)
# 2. Start pynn simulation, record spikes and neuron_matrix
# 3. re-run simulation

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
net_mode = 2  # 1: random; 2: small world WS; 3: small world Chris
mut_ratio = 0.03  # mutation ratio for small world
num_spike = 5  # number of spike generator and CA
num_neuron = 40  # number of neurons in each CA

random_seed = 1000
random.seed(random_seed)

conn_spike = 4  # connection from spike to neurons
conn_neuron = 4  # connections from a neuron to neurons within CAs
conn_cross = 2  # connections from a neuron to neurons in other CAs
# inhi_mode = 1  # 1. global-global; 2. selective-global
# conn_inhi = int(0.4 * num_neuron)  # selective inhibition connections

weight_spike = 0.08  # weight from spike to neuron
weight_neuron = 0.008  # starting weight between neurons
weight_conn = 0.0002  # starting weight between connecting CAs
# weight_inhi = -0.01  # inhibitory weight

# weight_max = 0.5  # maximum weight for each connection
# spike_margin = 20
# update_steps = 20

spike_series = [100, 120, 140, 160, 180, 200, 220, 240, 260, 280]  # spike time

conn_spike_file = 'demoSpike3'
conn_neuron_file = 'demoNeuron3'

spike_matrix = [[] for i in range(num_spike)]
neuron_matrix = [[] for i in range(num_spike * num_neuron)]

for i in range(num_spike):
    # spikes to neuron
    for j in sorted(random.sample(range(num_neuron), conn_spike)):
        spike_matrix[i].append([j + i * num_neuron, weight_spike])

# fixed input network
sample_cross_matrix = []
for j in range(num_neuron):
    target_neurons = []
    for k in range(conn_cross):
        if j + k < num_neuron:
            target_neurons.append(j + k)
        else:
            target_neurons.append(j + k - num_neuron)
    sample_cross_matrix.append(sorted(target_neurons))

# small world WS within CA, random cross CA
if net_mode == 2:
    for i in range(num_spike):  # current CA
        # excitation neurons within CA
        target_group = conn_small_ws(num_neuron, conn_neuron, mut_ratio)
        for j in range(num_neuron):
            target_neurons = target_group[j]
            for s in target_neurons:
                neuron_matrix[j + i * num_neuron].append([s[0] + i * num_neuron, weight_neuron])
        # excitation neurons across CA
        cross_group = range(num_spike)
        cross_group.remove(i)
        for j in cross_group:  # other CA
            if (i * j) == 0 or (i * j == 2) or (i * j == 12):  # A>(BCDE), B>(AC), C>(AB), D>(AE), E>(AD)
                for k in range(num_neuron):  # neuron in current CA
                    target_neurons = sample_cross_matrix[k]  # get sample cross neurons
                    for l in target_neurons:  # neuron in other CA
                        if i == 0:
                            neuron_matrix[k + i * num_neuron].append([l + j * num_neuron, float(weight_neuron) / 2])
                        else:
                            neuron_matrix[k + i * num_neuron].append([l + j * num_neuron, weight_neuron])


def run_base(trial='a', run_number=0):
    import pyNN.nest as sim
    import pyNN.utility.plotting as pyplotting

    start_time = time.time()
    sim.setup(timestep=1.0)

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

    spikes.record({'spikes'})
    neurons.record({'spikes'})

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
