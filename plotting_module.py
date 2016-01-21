from file_handler import file_handler
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np

class plotter:

	def __init__(self, filename):
		self.filename = filename

	def pathfinder(self):
		"""Find full path to filename """


	def plot_machine(self): 

		class_instance = file_handler(self.filename)
		class_instance.file_iteration()
		data_sets = class_instance.data_conversion()
		names = getattr(class_instance, "substances") 

		if len(names) > 2:			

			host = host_subplot(111, axes_class = AA.Axes)
			plt.subplots_adjust(right = 0.75)

			par1 = host.twinx()
			par2 = host.twinx()

			host.set_yscale("log")
			par1.set_yscale("log")
			par2.set_yscale("log")

			offset = 60 
			new_fixed_axis = par2.get_grid_helper().new_fixed_axis
			par2.axis["right"] = new_fixed_axis(loc="right",
			                                    axes=par2,
			                                    offset=(offset, 0))

			par2.axis["right"].toggle(all = True)

			host.set_xlabel(data_sets[0]["x_unit"])
				
			plotty_things = [host, par1, par2]

			for data_set, name, things in zip(data_sets, names, plotty_things):
				x_val = data_set["data"][0]
				y_val = data_set["data"][1]

				x_unit = data_set["x_unit"]
				y_unit = data_set["y_unit"]

				things.set_ylabel(y_unit)
				things.plot(x_val, y_val, label = data_set["sample element"])
				plt.legend()

			plt.show()
		
		else:

			data_set = data_sets[0]

			x_val = data_set["data"][0]
			y_val = data_set["data"][1]

			x_val = x_val.copy(order = "C")

			x_unit = data_set["x_unit"]
			y_unit = data_set["y_unit"]
		
			plt.semilogy(x_val, y_val, label = data_set["sample info"][2], nonposy = "clip")
			plt.xlabel(x_unit)
			plt.ylabel(y_unit)
			plt.legend()
			plt.show()




