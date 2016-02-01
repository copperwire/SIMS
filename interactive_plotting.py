from bokeh.models.widgets import Panel, Tabs, TextInput, RadioGroup
from bokeh.models.sources import ColumnDataSource
from bokeh.io import output_file, show, vform, hplot
from bokeh.palettes import Spectral11, RdPu9
from bokeh.plotting import figure, output_server, curdoc
from bokeh.client import push_session
from bokeh.models import Range1d, LogAxis

import random
import numpy as np 
from file_handler import file_handler

class interactive_plotting:

	def __init__(self, filenames):

		self.generation = False
		self.filenames = filenames

		if not isinstance(self.filenames, (list, np.ndarray, tuple, set)):
			self.filenames = [self.filenames]

		if not self.filenames:
			raise TypeError("Filnames can't be an empty list")


	def data_generation (self):
		"""
		Evaluates all files supplied to class and sets the filename and sample id as attributes containing the list 
		of data sets from each file. e.g.:

		filename = 151118h.dp
		sample id = 600c

		then the attribute "151118h_600c" exists as a variable in the class. The attribute is a list of dictionaries
		with keys such that for each index of  the attribute:

		151118h_600c[i] for i in [number of files]:
			data = 2 x n nested list where data[0] contains all data points corresponding to the key \" x_unit \"
			x_unit = string with physical unit of data[0]
			y_unit = string with physical unit of data[1]
			sample info = nested list containing sample id, original filename, sample code etc.
			sample element = name of the element measured by the SIMS process  		 
		"""

		self.generation = True
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
		#output_file("test.html")
		self.all_elements = []
		self.elements_comparison = []

		for attr_id, i in zip(self.attribute_ids, range(len(self.attribute_ids))):
			
			"""
			create plots for each datafile and put them in a tab.
			"""
			list_of_datasets = getattr(self, attr_id)
			y_axis_units = [x["y_unit"] for x in list_of_datasets]
			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log", title = "this is a thing")

			figure_obj.yaxis.axis_label = y_axis_units[0]

			if not all(x == y_axis_units[0] for x in y_axis_units):
				for unit, data in zip(y_axis_units, list_of_datasets): 
					if not unit == y_axis_units[0]:
						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(data["data"]["y"]), end = np.amax(data["data"]["y"]))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			figure_obj.xaxis.axis_label = list_of_datasets[0]["x_unit"]
			colour_list = Spectral11 + RdPu9

			list_of_elements = []

			for dataset in list_of_datasets:

				self.all_elements.append(dataset["sample element"]) #strip isotope number 
				color = random.choice(colour_list)
				colour_list.remove(color)

				source = ColumnDataSource(data = dataset["data"]) #Datastructure for source of plotting

				setattr(self, attr_id+"_"+dataset["sample element"]+"_source", source) #Source element generalized for all plotting 

				list_of_elements.append(dataset["sample element"])

				if not dataset["y_unit"] == y_axis_units[0] : 
					"""
					Assumes one scale for Intensity and a shift of some orders of maginitude in the conversion to Concentration.
					"""
					figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, line_color = color, legend = dataset["sample element"], y_range_name = "foo", name = dataset["sample element"])
				
				else: 
					figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, line_color = color, legend = dataset["sample element"], name = dataset["sample element"])

			radio_group = RadioGroup(labels = list_of_elements, active=0)
			text_input = TextInput(value = "default", title = "RSF for selected element: ")

			radio_group.on_change("active", lambda attr, old, new: None)

			text_input.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input:
								self.update_data(identity, radio, text_input, new))

			tab_plots.append(Panel(child = hplot(figure_obj, vform(radio_group, text_input)), title = attr_id))


		"""
		Check to see if one or more element exists in the samples and creat a comparison plot for each 
		of those elements.
		"""
		
		for element in self.all_elements:
			checkers = list(self.all_elements)
			checkers.remove(element)
			if element in checkers and not element in self.elements_comparison:
				self.elements_comparison.append(element)

		"""create plots for each element that is to be compared """
	
		for comparison_element in self.elements_comparison: 

			colour_list = Spectral11 + RdPu9
			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log")

			for attr_id in self.attribute_ids:
				
				list_of_datasets = getattr(self, attr_id)

				for dataset in list_of_datasets:
					if dataset["sample element"] == comparison_element:

						color = random.choice(colour_list)
						colour_list.remove(color)
						figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, line_color = color, legend = attr_id)
			
			tab_plots.append(Panel(child = figure_obj, title = comparison_element))	

		tabs = Tabs(tabs = tab_plots)

		session = push_session(curdoc())
		session.show()
		session.loop_until_closed()

	def raw_data(self):

		if self.generation:
			y = {}
			for name in self.attribute_ids:
				y[name] = getattr(self, name)
			return y	
		else:
			self.data_generation()
			self.raw_data()

	def update_data(self, attrname, radio, text_input, new):
		element = radio.labels[radio.active]

		print("hello")
		
		try:
			RSF = float(new)
		except ValueError:
			RSF = 1.
			#text_input.value = "ERROR: PLEASE INPUT NUMBER"

		source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample element"]+"_source"

		x = source_local.data["x"]
		y = RSF*source_local.data["y"]

		source_local.data = dict(x = x, y = y) 
		

	def find_file_path(self, filename):
		return filename