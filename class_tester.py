from plotting_module import *
from interactive_plotting import *
"""
filename = "/home/solli/Documents/Prosjektoppgave/Data_files/depth_profile/151118h.dp_rpc_asc"
test = plotter(filename)
test.plot_machine()


filename_2 = "/home/solli/Documents/Prosjektoppgave/Data_files/mass_spectrometry/ITO_mass-spectra_A.ms_rpc_asc"
test_2 = plotter(filevname_2)
test_2.plot_machine()
"""

filename = "/home/solli/Documents/Prosjektoppgave/Data_files/depth_profile/151118h.dp_rpc_asc"
test = interactive_plotting(filename)
test.data_generation()
