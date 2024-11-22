# 1. Set binary neuron network (single neuron cluster)
# 2. Start pynn simulation, record spikes and neuron_matrix
# 3. next increase number from 1 to 10

import time
import os
import numpy
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

save_fig = 0

sim_duration = 300
num_spike = 1  # number of spike generator and CA
num_neuron = 10  # number of neurons in each CA

spike_series = [100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120]  # spike time

conn_spike_file = 'demoAnalysis2'
conn_neuron_file = 'demoAnalysis3'

delays = numpy.random.normal(loc=1, scale=2, size=num_neuron)
delays = delays - min(delays)

print delays


def run_base(weight_spike=0):
    import pyNN.nest as sim
    import pyNN.utility.plotting as pyplotting

    start_time = time.time()
    sim.setup(timestep=0.1)

    spike_time = {'spike_times': spike_series}
    spikes = sim.Population(num_spike, sim.SpikeSourceArray, spike_time)
    neurons = sim.Population(num_spike, sim.IF_cond_exp, {})

    sim.reset()

    syn = [(0, 0, weight_spike, 1.0)]
    conn_list = sim.FromListConnector(syn)
    sim.Projection(spikes, neurons, conn_list)
    spikes.record('spikes')
    neurons.record(['spikes', 'v'], sampling_interval=0.1)

    sim.run(sim_duration)
    data_spike = spikes.get_data().segments[0]
    data_neuron = neurons.get_data().segments[0]
    data_neuron_v = neurons.get_data().segments[0].filter(name='v')[0]
    #    spike_save(data_neuron.spiketrains, conn_spike_file + '_' + trial + '.txt')
    sim.end()

    if save_fig == 1:
        pyplotting.Figure(pyplotting.Panel(data_spike.spiketrains, xticks=True, yticks=True),
                          pyplotting.Panel(data_neuron.spiketrains, xticks=True, yticks=True),
                          pyplotting.Panel(data_neuron.filter(name='v')[0], xticks=True, yticks=True)).save(
            'ipi 2  ' + str('%.4f' % weight_spike) + '.png')

    end_time = time.time()
    print str(round(end_time - start_time, 2)) + ' seconds'


# print neuron_matrix
for i in range(0, 2, 10):
    weight_spike = float(i) / 10000
    print weight_spike
    run_base(weight_spike)

duration = 1  # seconds
freq = 440  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
