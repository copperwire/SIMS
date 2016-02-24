from bokeh.models import HoverTool, TapTool, BoxZoomTool, BoxSelectTool, PreviewSaveTool, ResetTool
from bokeh.models.widgets import Panel, Tabs, TextInput, RadioGroup, Button
from bokeh.models.sources import ColumnDataSource
from bokeh.io import output_file, show, vform, hplot
from bokeh.palettes import Spectral11, RdPu9, Oranges9
from bokeh.plotting import figure, output_server, curdoc
from bokeh.client import push_session
from bokeh.models import Range1d, LogAxis, LinearAxis

import os
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

			class_instance = file_handler(filename)
			class_instance.file_iteration()
			data_sets = class_instance.data_conversion()

			name_check = data_sets[0]["DATA FILES"]

			attr_id = name_check[1][4][:-3] + "_" + name_check[2][2]

			self.attribute_ids.append(attr_id)
			setattr(self, attr_id, data_sets)

	def plotting(self):



		#Tools = [hover, TapTool(), BoxZoomTool(), BoxSelectTool(), PreviewSaveTool(), ResetTool()]
		TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"


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
			x_axis_units = [x["x_unit"] for x in list_of_datasets]

			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log",
			title = attr_id, tools = TOOLS)

			setattr(self, attr_id+"_"+"figure_obj",figure_obj)

			figure_obj.yaxis.axis_label = y_axis_units[0]
			figure_obj.xaxis.axis_label = x_axis_units[0]

			if not all(x == y_axis_units[0] for x in y_axis_units):
				for unit, data in zip(y_axis_units, list_of_datasets): 
					if not unit == y_axis_units[0]:
						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(data["data"]["y"]),
						end = np.amax(data["data"]["y"]))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			if not all(x == x_axis_units[0] for x in x_axis_units):
				for unit, data in zip(x_axis_units, list_of_datasets): 
					if not unit == x_axis_units[0]:
						figure_obj.extra_x_ranges =  {"bar": Range1d(start = np.amin(data["data"]["x"]),
						end = np.amax(data["data"]["x"]))}
						figure_obj.add_layout(LinearAxis(x_range_name = "bar", axis_label = unit), "above")
						break



			figure_obj.xaxis.axis_label = list_of_datasets[0]["x_unit"]
			colour_list = Spectral11 + RdPu9 + Oranges9
			colour_indices = [0, 2, 8, 10, 12, 14, 20, 22, 1, 3, 9, 11, 13, 15]

			list_of_elements = []

			for dataset, color_index in zip(list_of_datasets, colour_indices):

				self.all_elements.append(dataset["sample element"]) #strip isotope number 
				color = colour_list[color_index]

				source = ColumnDataSource(data = dataset["data"]) #Datastructure for source of plotting

				setattr(self, attr_id+"_"+dataset["sample element"]+"_source", source) #Source element generalized for all plotting				


				list_of_elements.append(dataset["sample element"])

				figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]
								+"_source"), line_width = 2, line_color = color, 
								legend = dataset["sample element"], name = dataset["sample element"],
								 )

			hover = figure_obj.select_one(HoverTool).tooltips = [("element", "@element"), ("(x,y)", "($x, $y)")]

			radio_group = RadioGroup(labels = list_of_elements, active=0)

			"""
			Need to fetch default variables from input file and replace DEFAULT

			Block of code produces the layout of buttons and callbacks
			"""

			
			
			text_input_rsf = TextInput(value = "default", title = "RSF (at/cm^3): ")
			text_input_sputter = TextInput(value = "default", title = "Sputter speed: float unit")
			text_input_crater_depth = TextInput(value = "default", title = "Depth of crater in: float")
			radio_group.on_change("active", lambda attr, old, new: None)

			text_input_xval_integral = TextInput(value = "0", title = "x-value for calibration integral ")
			text_input_yval_integral = TextInput(value = "0", title = "y-value for calibration integral ")

			do_integral_button = Button(label = "Calibration Integral")
			save_flexDPE_button = Button(label = "Save file for FlexPDE")

			do_integral_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group, x_box = text_input_xval_integral, y_box = text_input_yval_integral: self.integrate(identity, radio, x_box, y_box))

			save_flexDPE_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group: self.write_to_flexPDE(identity, radio))

			text_input_rsf.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input_rsf, which = "rsf":
								self.update_data(identity, radio, text_input, new, which))

			text_input_sputter.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input_sputter, which = "sputter":
								self.update_data(identity, radio, text_input, new, which))

			text_input_crater_depth.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input_crater_depth, which = "crater_depth":
								self.update_data(identity, radio, text_input, new, which))



			tab_plots.append(Panel(child = hplot(figure_obj, 
										   vform(radio_group, save_flexDPE_button), 
										   vform(text_input_rsf, text_input_sputter, text_input_crater_depth),
										   vform(text_input_xval_integral, text_input_yval_integral, do_integral_button)),
										   title = attr_id))


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

			colour_list = Spectral11 + RdPu9 + Oranges9
			colour_indices = [0, 2, 8, 10, 12, 14, 20, 22, 1, 3, 9, 11, 13, 15]
			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log", title = comparison_element)

			y_axis_units = []
			x_axis_units = []

			comparison_datasets = []


			for attr_id, color_index in zip(self.attribute_ids, colour_indices):

				list_of_datasets = getattr(self, attr_id)

				for dataset in list_of_datasets:

					if dataset["sample element"] == comparison_element:
						comparison_datasets.append(dataset)
						y_axis_units.append(dataset["y_unit"])
						x_axis_units.append(dataset["x_unit"])

			figure_obj.xaxis.axis_label = comparison_datasets[-1]["x_unit"]
			figure_obj.yaxis.axis_label = comparison_datasets[-1]["y_unit"]

			if not all(x == y_axis_units[-1] for x in y_axis_units):
				for unit, data in zip(y_axis_units, comparison_datasets): 
					if not unit == y_axis_units[-1]:
						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(data["data"]["y"]),
						end = np.amax(data["data"]["y"]))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			if not all(x == x_axis_units[-1] for x in x_axis_units):
				for unit, data in zip(x_axis_units, comparison_datasets): 
					if not unit == x_axis_units[-1]:
						figure_obj.extra_x_ranges =  {"bar": Range1d(start = np.amin(data["data"]["x"]),
						end = np.amax(data["data"]["x"]))}
						figure_obj.add_layout(LinearAxis(x_range_name = "bar", axis_label = unit), "above")
						break


			for attr_id, color_index in zip(self.attribute_ids, colour_indices):

				list_of_datasets = getattr(self, attr_id)

				for dataset in list_of_datasets:

					if dataset["sample element"] == comparison_element:
						color = colour_list[color_index]

						"""
						Logic that ensures that plots get put with correspoinding axes. 
						"""
						if dataset["x_unit"] != x_axis_units[-1] or dataset["y_unit"] != y_axis_units[-1]:

							if dataset["x_unit"] != x_axis_units[-1] and dataset["y_unit"] != y_axis_units[-1]:

								figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, 
								line_color = color, legend = attr_id, x_range_name = "bar", y_range_name = "foo")

							elif dataset["x_unit"] != x_axis_units[-1]:

								figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, 
								line_color = color, legend = attr_id, x_range_name = "bar")

							else: 

								figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, 
								line_color = color, legend = attr_id, y_range_name = "foo")

						else: 
							figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample element"]+"_source"), line_width = 2, 
							line_color = color, legend = attr_id)
						


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

	def integrate(self,  attrname, radio, x_box, y_box):

		element = radio.labels[radio.active]
		source_local = getattr(self, attrname+"_"+element+"_source") 

		lower_xlim = float(x_box.value)
		lower_ylim = float(y_box.value)

		x = np.array(source_local.data["x"])
		y = np.array(source_local.data["y"])

		x_change = x[x>lower_xlim]*1e-4 
		y_change = y[len(y)-len(x_change):]

		integral = np.trapz(y_change, x = x_change)

		comparsion = np.sum(y) * x[-1]*1e-4

		print(integral, comparsion)

	def write_to_flexPDE(self, attrname, radio):
		element = radio.labels[radio.active]

		source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample element"]+"_source"

		x = np.array(source_local.data["x"])
		y = np.array(source_local.data["y"])

		path_to_direct = os.getcwd()
		path_to_flex = path_to_direct + "/data_files/FlexPDE/"
		write_to_filename = path_to_flex+attrname+ "_"+element+".txt"

		file_object = open(write_to_filename, "w+")

		file_object.write("X %i \n" %len(x)) 
		
		for item in x: 
			file_object.write("%1.3f " %item) 

		file_object.write("\nData {u} \n")

		for item in y: 
			file_object.write("%1.1e " %item) 

		file_object.close()

	def write_new_datafile(self, attrname, radio):
		radio_group = radio




	def update_data(self, attrname, radio, text_input, new, which):

		if which == "rsf":
			element = radio.labels[radio.active]
			
			try:
				RSF = float(new)
			except ValueError:
				RSF = 1.
				#text_input.value = "ERROR: PLEASE INPUT NUMBER"

			source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample element"]+"_source"

			x = np.array(source_local.data["x"])
			y = np.array(source_local.data["y"])

			x = x
			y = RSF*y

			source_local.data = dict(x = x, y = y, element = [name for i in range(len(np.array(u[:,number + 1])))]) 
		
		elif which == "sputter" or which == "crater_depth":
			"""
			Should create new axis and push to active session to replace the plot? 
			Or simply append new x-axis? Need to identify if there exists a second x-axis allready
			"""


			if which == "sputter":
				try:
					sputter_speed, unit = new.split()
					sputter_speed = float(sputter_speed) 
				except ValueError:
					return

			elif which == "crater_depth":
				try: 
					sputter_speed, unit = new.split()
					sputter_speed = float(sputter_speed) / x[-1]

				except ValueError:
					return

			figure_obj = getattr(self, attrname+"_"+"figure_obj")


			for element in radio.labels: 
				source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample element"]+"_source"
				x = np.array(source_local.data["x"])
				y = np.array(source_local.data["y"])

				x = x*sputter_speed
				
				source_local.data = dict(x = x, y = y) 
				figure_obj.xaxis.axis_label = "Depth " + " " + "[" + unit + "]"
