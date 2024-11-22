# 1. Check maximum spiking rate and its relationship with t_refrac
# 2. Get weight for spike transmission

import pyNN.nest as sim
from pyNN.utility.plotting import Figure, Panel
from AutoCAFun2 import *
import os

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

spike_series = []
for i in range(100, 200, 100):
    spike_series.append(i)  # spike time
spike_time = {'spike_times': spike_series}

num_spike = 1
num_neuron = 1  # > 1
weight_spike = 1.0


def run_base(weight_neuron=0.0001):
    spike_file = 'demoSpikeTemp' + '%.4f' % weight_neuron + '.txt'

    sim.setup(timestep=1.0)
    spikes = sim.Population(num_spike, sim.SpikeSourceArray, spike_time)
    neurons = sim.Population(num_neuron, sim.IF_curr_exp, {})

    neurons.set(tau_refrac=2.0)
    sim.reset()

    conn_spike = []
    for i in range(num_neuron - 1):
        conn_spike.append((0, i, weight_spike, 1.0))
    conn_list = sim.FromListConnector(conn_spike)
    sim.Projection(spikes, neurons, conn_list)

    conn_neuron = []
    for i in range(num_neuron - 1):
        conn_neuron.append((i, num_neuron - 1, weight_neuron, 1.0))
    conn_list = sim.FromListConnector(conn_neuron)
    sim.Projection(neurons, neurons, conn_list)

    spikes.record({'spikes'})
    neurons.record({'spikes'})

    sim.run(1000)
    data_spike = spikes.get_data().segments[0]
    data_neuron = neurons.get_data().segments[0]

    spike_save(data_neuron.spiketrains, spike_file)
    sim.end()

    Figure(Panel(data_spike.spiketrains, xlabel="Spike Source", xticks=True),
           Panel(data_neuron.spiketrains, xlabel='Neuron', xticks=True)).save(
        'demo_temp ' + '%.4f' % weight_neuron + '.png')


for i in range(10, 800000, 5000):
    weight = float(i) / 100000
    run_base(weight)

duration = 1  # seconds
freq = 261  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
