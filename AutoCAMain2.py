# 1. Set neuron network parameters, spike_matrix, neuron_matrix(CAs+inhibition)
# 2. Start pynn simulation, record spikes and neuron_matrix
# 3. re-run simulation

import random
import time
import os

from AutoCAFun2 import *

random_seed = 1000
save_fig = 1

delay = 1.0
sim_duration = 1000
net_mode = 1  # 1: random; 2: small world WS; 3: small world Chris
mut_ratio = 0.03  # mutation ratio for small world
num_spike = 5  # number of spike generator, cluster and inhibitions
num_neuron = 100  # number of neurons in each cluster

conn_spike = 20  # connection from spike to neurons
conn_neuron = 8  # connections from neuron to neurons within CAs
conn_cross = 4  # connections from neuron to neurons in other CAs
inhi_mode = 1  # 1. global-global; 2. selective-global
conn_inhi = int(0.4 * num_neuron)  # selective inhibition connections

weight_spike = 0.1  # weight from spike to neuron
weight_neuron = 0.01  # starting weight between neurons
weight_max = 0.5  # maximum total weight from an excitation neuron
weight_inhi = -0.01  # inhibitory weight

spike_margin = 20
update_steps = 20

spike_series = [100, 120, 140, 160, 180, 200, 220, 240, 260, 280]  # spike time

conn_spike_file = 'demoSpike2.txt'
conn_neuron_file = 'demoNeuron2.txt'

random.seed(random_seed)

spike_matrix = [[] for i in range(num_spike)]
neuron_matrix = [[] for i in range(num_spike * (num_neuron + 1))]
neuron_group = [range(i * num_neuron, i * num_neuron + num_neuron) for i in range(num_spike)]

# random connection
if net_mode == 1:
    for i in range(num_spike):
        neuron_group = range(num_neuron)
        cross_group = range(num_spike)
        cross_group.remove(i)
        # excitation neurons within CA
        for j in neuron_group:
            target_group = neuron_group[:]
            target_group.remove(j)
            target_neurons = sorted(random.sample(target_group, conn_neuron))
            for s in target_neurons:
                neuron_matrix[j + i * num_neuron].append([s + i * num_neuron, weight_neuron])
        # excitation neurons across CA
        for j in neuron_group:
            for s in cross_group:
                target_group = neuron_group[:]
                target_neurons = sorted(random.sample(target_group, conn_cross))
                for l in target_neurons:
                    neuron_matrix[j + i * num_neuron].append([l + s * num_neuron, weight_neuron])

# small world WS within CA, random cross CA
if net_mode == 2:
    for i in range(num_spike):
        neuron_group = range(num_neuron)
        cross_group = range(num_spike)
        cross_group.remove(i)
        # excitation neurons within CA
        target_group = conn_small_ws(num_neuron, conn_neuron, mut_ratio)
        for j in neuron_group:
            target_neurons = target_group[j]
            for s in target_neurons:
                neuron_matrix[j + i * num_neuron].append([s[0] + i * num_neuron, weight_neuron])
        # excitation neurons across CA

        # for cross CA connections, small world may not work as conn_cross is too small
        # for s in cross_group:
        #     target_group = conn_small_ws(num_neuron, conn_cross, mut_ratio)
        #     for j in neuron_group:
        #         target_neurons = target_group[j]
        #         for k in target_neurons:
        #             neuron_matrix[j + i * num_neuron].append([k[0] + s * num_neuron, weight_neuron])

        for s in cross_group:
            for j in neuron_group:
                target_group = neuron_group[:]
                target_neurons = sorted(random.sample(target_group, conn_cross))
                for l in target_neurons:
                    neuron_matrix[j + i * num_neuron].append([l + s * num_neuron, weight_neuron])

# small world Chris, gradual growth mode
if net_mode == 3:
    print 'small workd chris undone'

for i in range(num_spike):
    # spikes to neuron
    for j in sorted(random.sample(neuron_group, conn_spike)):
        spike_matrix[i].append([j + i * num_neuron, weight_spike])
    # inhibition neurons
    for j in neuron_group:
        neuron_matrix[num_spike * num_neuron + i].append([j + i * num_neuron, weight_inhi])

# inhibition neuron activation
if inhi_mode == 1:
    for i in range(num_spike):
        for j in range(num_neuron):
            neuron_matrix[j + i * num_neuron].append([i + num_spike * num_neuron, weight_neuron])
if inhi_mode == 2:
    print 'inhibion selective mode undone'


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

    spike_save(data_neuron.spiketrains, conn_spike_file)
    conn_save(neuron_matrix, conn_neuron_file)
    sim.end()
    if save_fig == 1 and run_number % 5 == 0:
        pyplotting.Figure(pyplotting.Panel(data_spike.spiketrains, xticks=True, yticks=True),
                          pyplotting.Panel(data_neuron.spiketrains, xticks=True, yticks=True)).save(
            'spikes_' + trial + '_' + str(run_number) + '.png')
    end_time = time.time()
    print str(round(end_time - start_time, 2)) + ' seconds'


def run_analysis():
    spike_matrix = spike_load(conn_spike_file)
    conn_matrix = neuron_matrix[:]
    for i in range(num_spike):
        conn_matrix.pop(num_spike * num_neuron)
    for i in conn_matrix:
        i.pop(len(i) - 1)
    conn_matrix = conn_update(conn_matrix, spike_matrix, spike_margin, weight_max, update_steps)
    for i in range(len(conn_matrix)):
        conn_matrix[i].append([i / 100, weight_neuron])
    for i in range(num_spike):
        conn_matrix.append(neuron_matrix[num_neuron * num_spike + i])
    return conn_matrix


for i in range(1):
    run_base('b')
    # print neuron_matrix
    # neuron_matrix = run_analysis()
# print neuron_matrix


duration = 1  # seconds
freq = 440  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
