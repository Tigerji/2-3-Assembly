num_spike = 2
num_neuron = 10
conn_cross = 4

sample_cross_matrix = [[] for i in range(num_spike)]
for i in range(num_spike):
    for j in range(num_neuron):
        target_neurons = []
        for k in range(conn_cross):
            if j + k < num_neuron:
                target_neurons.append(j + k)
            else:
                target_neurons.append(j + k - num_neuron)
        sample_cross_matrix[i].append(sorted(target_neurons))
print sample_cross_matrix
