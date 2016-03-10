from file_handler import file_handler
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np

filename =  "/home/solli/Documents/Prosjektoppgave/Data_files/mass_spectrometry/ITO_mass-spectra_A.ms_rpc_asc"
test = file_handler(filename)
names, data_sets = test.runtime()

data_set = data_sets[0]
plt.plot(data_set["data"][0], data_set["data"][1])
plt.yscale("log")
plt.show()