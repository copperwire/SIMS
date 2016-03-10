from file_handler import *

filename = "/home/solli/Documents/Prosjektoppgave/Data_files/depth_profile/151118h.dp_rpc_asc"
test = file_handler(filename)
substances, list_data = test.runtime()

for dataset in list_data:
	print(dataset["x_unit"])