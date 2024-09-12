import matplotlib.pyplot as plt

plotfolder = 'Plots'
plt.figure()
plt.plot(1, 1, 'r*')
plt.savefig(plotfolder + '/sample.png')

plt.show()

print('Update in progress')
