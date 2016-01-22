from bokeh.models.widgets import Panel, Tabs
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import Range1d, LogAxis

import numpy as np 
from file_handler import file_handler

class interactive_plotting:

	def __init__(self, filenames):

		self.filenames = filenames

		if not isinstance(self.filenames, (list, np.ndarray, tuple, set)):
			self.filenames = [self.filenames]


	def data_generation (self):
		"""
		Evaluates all files supplied to class and sets the filename and sample id as attributes containing the list 
		of data sets from each file. e.g.:

		filename = 151118h.dp
		sample id = 600c

		then the attribute "151118h_600c" exists as a variable in the class. The attribute is a list of dictionaries
		with keys:
		data = 2 x n nested list where data[0] contains all data points corresponding to the key \" x_unit \"
		x_unit = string with physical unit of data[0]
		y_unit = string with physical unit of data[1]
		sample info = nested list containing sample id, original filename, sample code etc.
		sample element = name of the element measured by the SIMS process  		 
		"""

		self.attribute_ids = []

		for filename in self.filenames:
			full_path_to_file = self.find_file_path(filename)

			class_instance = file_handler(full_path_to_file)
			class_instance.file_iteration()
			data_sets = class_instance.data_conversion()

			name_check = data_sets[0]["sample info"]
			attr_id = name_check[1].split(" ")[4][:-3] + "_" + name_check[2].split(" ")[2]

			self.attribute_ids.append(attr_id)
			setattr(self, attr_id, data_sets)

	def plotting(self):

		tab_plots = []
		output_file("test.html")

		for attr_id in self.attribute_ids:
	
			list_of_datasets = getattr(self, attr_id)
			y_axis_units = [x["y_unit"] for x in list_of_datasets]
			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log")
			figure_obj.yaxis.axis_label = y_axis_units[0]

			if not all(x == y_axis_units[0] for x in y_axis_units):
				for unit in y_axis_units: 
					if not unit == y_axis_units[0]:
						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(y_data), end = np.amax(y_data))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			figure_obj.line(list_of_datasets[0]["data"][0], list_of_datasets[0]["data"][1], legend = list_of_datasets[0]["sample element"])
			figure_obj.xaxis.axis_label = list_of_datasets[0]["x_unit"]

			for dataset in list_of_datasets[1:]:

				x_data = dataset["data"][0]
				y_data = dataset["data"][1]
				
				if not dataset["y_unit"] == y_axis_units[0] : 
					"""
					Assumes one scale for Intensity and a shift of some orders of maginitude in the conversion to Concentration.
					"""
					figure_obj.line(x_data, y_data, line_width = 2, legend = dataset["sample element"], y_range_name = "foo")

				else: 
					figure_obj.line(x_data, y_data, line_width = 2, legend = dataset["sample element"])	
					#figure_obj.yaxis[0].axis_label = dataset["y_unit"]
			tab_plots.append(Panel(child = figure_obj, title = attr_id))

		tabs = Tabs(tabs = tab_plots)
		show(tabs)






	def find_file_path(self, filename):
		return filename