import sys
import os 
import numpy as np
import matplotlib.pyplot as plt

class file_handler:

	def __init__(self, filename):
		self.filename = filename 

	def file_location(self):
		thing = os.walk(os.getcwd())
		print thing
		path_to_file = os.path.join(thing[0], self.filename)

		print path_to_file

	def file_iteration(self, delim = "***"):
		"""
		Method to get data from the SIMS output files. 
		The data is collected in groups by the delimiters in the data file, e.g. **** DATA START*** contains all numerical data. 
		Operations are then preformed to convert the data to human and machine readable formats. 

		The class can easily be changed to take an arbitrary data file with a known delimiter between types of parameters. 
		If there are several data sets, submit a list with strings denoting the start of the dataset and the corresponding
		attribute of the class will be a dictionary with the denoted rows as keys with substance as the first element
		and the x and y axis as the second and third element.  
		"""
		num_lines = sum(1 for line in open(self.filename))

		
		#full_file_path = self.file_location()
		with open(self.filename) as self.file_object:
			line_indices = np.arange(0, num_lines, 1, dtype = int)

			data_type_indices = []
			lines = []

			for line, i in zip(self.file_object, line_indices):
				decoded = " ".join(line.split())
				lines.append(decoded)
				if line[:3] == delim:
					data_type_indices.append(i)

			self.attribute_names = []


			for index_of_data_type, i in zip(data_type_indices, np.arange(0, len(data_type_indices)-1, 1,  dtype = int)): 
				self.attribute_names.append(str(lines[index_of_data_type][4:-4]))
				setattr(self, str(lines[index_of_data_type][4:-4]), lines[index_of_data_type + 1: data_type_indices[i + 1 ] - 1]) 
			
		
	def data_conversion(self, data_name = "DATA START", key_row= [2, 3]):

		data_set = getattr(self, data_name)
		substances = data_set[key_row[0]].split(" ")
		units = data_set[key_row[1]].split(" ")

		x = []
		for line in data_set[key_row[1] + 1:] :
			dat = line.split(" ")
			a = [float(c) for c in dat]
			x.append(a)

		reshaping = np.shape(x)
		u = np.reshape(x, (reshaping[0], reshaping[1]))
	
		variables_per_substance = len(x[0])/len(substances)


		for name, number in zip(substances, np.arange(0, len(x[0]), 2, dtype = int)):
			y = {}
			if variables_per_substance == 2 and x[0][0] != 0 :
				units = [x for x in units if x != "Time"]

			y["data"] = [u[:,number], u[:,number +1]]





