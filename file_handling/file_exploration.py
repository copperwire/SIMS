from file_handler import file_handler

filename = "/home/solli/Documents/Prosjektoppgave/Data_files/depth_profile/151118h.dp_rpc_asc"


test = file_handler(filename)
substances, data = test.runtime()

print(substances)
print(data[0]["calibration_params"])

