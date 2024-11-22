import math
import random
import numpy as np
import matplotlib.pyplot as plt


def conn_save(a, data_file="demofile3.txt"):
    # save in matrix form, check demofile3.txt for example
    with open(data_file, 'w+') as f:
        for i in a:
            for j in i:
                f.write(str(j))
            f.write('\n')


def conn_load(data_file='demofile3.txt'):
    with open(data_file, 'r') as f:
        data = []
        for i in f.readlines():
            removed = i[1:-2].replace('[', '')
            temp_matrix = []
            if len(removed) > 0:
                sub_matrix = removed.split(']')
                for j in sub_matrix:
                    temp_matrix.append([int(j.split(',')[0]), float(j.split(',')[1])])
            data.append(temp_matrix)
    return data


def spike_load(data_file='demospike3.txt'):
    with open(data_file, 'r') as f:
        data = []
        for i in f.readlines():
            removed = i[1:-2].replace(',', '')
            temp_matrix = []
            if len(removed) > 0:
                sub_matrix = removed.split(' ')
                for j in sub_matrix:
                    temp_matrix.append(int(j))
            data.append(temp_matrix)
    return data


def spike_save(spikes, spike_file='Data/SpikesDefault.txt'):
    with open(spike_file, 'w+') as f:
        for i in range(len(spikes)):
            spike_timings = str(spikes[i]).split('.')
            if len(spike_timings) > 1:
                spike_number = [int(spike_timings[0][1:])]
                for j in range(1, len(spike_timings) - 1):
                    spike_number = spike_number + [int(float(spike_timings[j]))]
            else:
                spike_number = []
            f.write(str(spike_number) + '\n')


def connector_load(a):
    # a = [[[1,0.001], [2,0.001]], [[0,0.001]], []]
    connector = []
    for i in range(len(a)):
        for j in a[i]:
            connector.append((i, j[0], j[1], 1.0))
    return connector


def spike_check(a, b, spike_margin=20):
    # a = [20, 300, 320]
    # b = []
    total_count = 0
    for i in a:
        spike_count = 0
        for j in b:
            if i > j >= i - spike_margin:
                spike_count = spike_count - 1
            if i < j <= i + spike_margin:
                spike_count = spike_count + 1
        if spike_count > 0:
            total_count = total_count + 1
        if spike_count < 0:
            total_count = total_count - 1
    return float(total_count) / len(a)


def weight_update(current=0, target=0.5, steps=20):
    if current > target:
        current = current - (current - target) * 2 / steps
    else:
        current = current + (target - current) * 2 / steps
    return round(current, 5)


def conn_update(conn_matrix, spike_matrix, spike_margin=20, weight_max=0.5, update_steps=20):
    for i in range(0, len(conn_matrix)):
        if len(conn_matrix[i]) > 0 and len(spike_matrix[i]) > 0:
            targets = []
            for j in conn_matrix[i]:
                targets.append(j[0])
            temp_weight_max = round(weight_max / len(conn_matrix[i]), 5)
            for j in range(0, len(conn_matrix[i])):
                if spike_check(spike_matrix[i], spike_matrix[conn_matrix[i][j][0]], spike_margin) >= 0.1:
                    print 'Editing' + str(i) + ' ' + str(j)
                    conn_matrix[i][j][1] = weight_update(conn_matrix[i][j][1], temp_weight_max, update_steps)
                if spike_check(spike_matrix[i], spike_matrix[conn_matrix[i][j][0]], spike_margin) <= -0.1:
                    print 'Editing' + str(i) + ' ' + str(j)
                    conn_matrix[i][j][1] = weight_update(conn_matrix[i][j][1], 0, update_steps)
    return conn_matrix


def average_short_path(network):
    # network format: [[[X, XXX],[X, XXX]], []]
    reach_matrix = [[] for i in range(len(network))]
    step_matrix = [[] for i in range(len(network))]
    for i in range(len(network)):
        target_matrix = range(len(network))
        target_matrix.remove(i)
        count = 0
        curr_top = [i]
        curr_reached = []
        while count < len(network):
            count = count + 1
            curr_branch = []
            for j in curr_top:
                for k in network[j]:
                    if k[0] not in curr_branch and k[0] != i:
                        curr_branch.append(k[0])
                    if k[0] not in curr_reached and k[0] != i:
                        curr_reached.append(k[0])
                        reach_matrix[i].append([k[0], count])
                        step_matrix[i].append(count)
            curr_top = curr_branch[:]
    data_sum = 0
    data_len = 0
    for i in reach_matrix:
        for j in i:
            data_sum = data_sum + j[1]
            data_len = data_len + 1
    return float(data_sum) / data_len


def conn_small_ws(num_neuron=10, num_conn=4, mut_ratio=0.03):
    conn_net = []
    if num_conn % 2 == 1 or num_conn * 2 >= num_neuron or num_neuron < num_conn:
        print 'Network Construction Error - connSmallWS'
    else:
        for i in range(num_neuron):
            curr_net = []
            for j in range(1, num_conn / 2 + 1):
                if i - j >= 0:
                    curr_net.append([i - j])
                else:
                    curr_net.append([i - j + num_neuron])
                if i + j < num_neuron:
                    curr_net.append([i + j])
                else:
                    curr_net.append([i + j - num_neuron])
            mut_target = range(num_neuron)
            mut_target.remove(i)
            for j in curr_net:
                if j[0] in mut_target:
                    mut_target.remove(j[0])
            for j in range(len(curr_net)):
                if random.random() < mut_ratio:
                    new_target = random.sample(mut_target, 1)
                    if [new_target] not in curr_net:
                        curr_net[j] = new_target
            conn_net.append(sorted(curr_net))
    return conn_net


def conn_random(num_neuron=10, num_conn=4):
    conn_net = [[] for i in range(num_neuron)]
    for i in range(num_neuron):
        targets = range(num_neuron)
        targets.remove(i)
        curr_net = random.sample(targets, num_conn)
        for j in sorted(curr_net):
            conn_net[i].append([j])
    return conn_net


def spike_gen(string, spike_series=[100, 120, 140, 160, 180, 200], num_spike=5):
    spike_time = [[] for i in range(num_spike)]
    if 'a' in string:
        spike_time[0] = spike_series
    if 'b' in string:
        spike_time[1] = spike_series
    if 'c' in string:
        spike_time[2] = spike_series
    if 'd' in string:
        spike_time[3] = spike_series
    if 'e' in string:
        spike_time[4] = spike_series
    spikes = {'spike_times': spike_time}
    return spikes


def clustering_coef(matrix):
    # matrix = [[1,2,3], [4,5,6,7,8], ...]
    clusters = [[] for i in range(len(matrix))]
    connecting = [[] for i in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i in matrix[j]:
                connecting[i].append(j)
        connecting[i].sort()

    for i in range(len(matrix)):  # A>B, A>C, B<>C
        conn_temp = matrix[i][:]
        for j in matrix[i]:
            conn_temp.remove(j)
            for s in conn_temp:
                triangle = []
                if s in matrix[j] or j in matrix[s]:
                    triangle.append(i)
                    triangle.append(j)
                    triangle.append(s)
                    if sorted(triangle) not in clusters[i]:
                        clusters[i].append(sorted(triangle))

    for i in range(len(matrix)):  # A>B, C>A, B<>C
        conn_temp = connecting[i]
        for j in matrix[i]:
            if j in conn_temp:
                conn_temp.remove(j)
            for s in conn_temp:
                triangle = []
                if s in matrix[j] or j in matrix[s]:
                    triangle.append(i)
                    triangle.append(j)
                    triangle.append(s)
                    if sorted(triangle) not in clusters[i]:
                        clusters[i].append(sorted(triangle))

    for i in range(len(matrix)):  # A<B, A<C, B<>C
        conn_temp = connecting[i]
        for j in connecting[i]:
            conn_temp.remove(j)
            for s in conn_temp:
                triangle = []
                if s in matrix[j] or j in matrix[s]:
                    triangle.append(i)
                    triangle.append(j)
                    triangle.append(s)
                    if sorted(triangle) not in clusters[i]:
                        clusters[i].append(sorted(triangle))
    average_cluster = []

    all_connect = []
    for i in range(len(matrix)):
        temp_connect = []
        for j in matrix[i]:
            if j not in temp_connect:
                temp_connect.append(j)
        for j in connecting[i]:
            if j not in temp_connect:
                temp_connect.append(j)
        all_connect.append(temp_connect)

    for i in range(len(matrix)):
        average_cluster.append(float(len(clusters[i])) / (0.5 * len(all_connect[i]) * (len(all_connect[i]) - 1)))
    return average_cluster


def shortest_length(matrix):
    # matrix = [[1,2,3], [4,5,6,7,8], ...]
    average_length = [len(matrix) + 1 for i in range(len(matrix))]
    for i in range(len(matrix)):
        reached = [i]  # reached nodes
        reached_hash = {0: [i]}  # hash map of steps
        curr_targets = [i]
        count = 0
        while len(reached) < len(matrix):
            count = count + 1
            new_targets = []
            for j in curr_targets:
                for s in matrix[j]:
                    if s not in reached:
                        reached.append(s)
                        new_targets.append(s)
            reached_hash[count] = new_targets
            curr_targets = new_targets
        for j in range(len(reached_hash)):
            average_length[i] = average_length[i] + j * len(reached_hash[j])
        average_length[i] = average_length[i] / (len(matrix) - 1)
    return average_length


def plot_spiketrains(segment, title='Demo'):
    plt.figure(title)
    for spiketrain in segment.spiketrains:
        y = np.ones_like(spiketrain) * spiketrain.annotations['source_id']
        #  print spiketrain
        plt.plot(spiketrain, y, '.')
