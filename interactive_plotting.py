import bokeh as bk 
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
		sample name = name of the element measured by the SIMS process  		 
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
		return


	def find_file_path(self, filename):
		return filename