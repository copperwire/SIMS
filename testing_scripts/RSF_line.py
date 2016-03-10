import numpy as np
from file_handler import *
import matplotlib.pyplot as plt
import scipy.optimize as scp_o
from lin_reg import lin_reg 

filenames = ["/home/solli/Documents/Prosjektoppgave/data_files/RSF_estimation/ionization_potentials.txt",
"/home/solli/Documents/Prosjektoppgave/data_files/RSF_estimation/RSF_ZnO_values.txt"]

RSF_vals = []
ion_pot = []
list_objs = [RSF_vals, ion_pot]


for file, list_obj in zip(filenames, list_objs): 
	with open(file) as filename:
		for line in filename:
			if line[0] == "#":
				continue
			formatted = line.split(" ")
			list_obj.append([formatted[0], float(formatted[1])])

x = []
y = []

for element in RSF_vals:
	for other_element in ion_pot:
		if element[0] == other_element[0]:
			y.append(other_element[1])
			x.append(element[1])
			break

x = np.sort(x)
y = np.sort(y)

poly, res_, _, _, _ = np.polyfit(x, np.log10(y), 1, full = True)

lam_one = 10**poly[1]
gamm_one = poly[0]

x_num = np.linspace(5, 9, 10)

#poly_eval = np.polyval(poly, x_num)


"""
find best function on form y = lambda * a ^(gamma x)
which forms a straight line in a semi-logarithmical plot with base a, with slope gamma 
and log_a (lambda) as the vertical intercept
"""

def func(x, lamb, gamma):
	return lamb*10**(gamma*x)


popt, pcov = scp_o.curve_fit(func, x, y)

lamb = popt[0]
gamma = popt[1]

log_fit = func(x_num, lamb, gamma)
second_log_fit = func(x_num, lam_one, gamm_one)


#Error estimation

sigm_2 = np.std(np.log10(y) - np.polyval(poly, x))

new_err = 0.1


poly_own, res, del_m_sqrd, del_c_sqrd = lin_reg(x, np.log10(y), full = True).least_squares()

print("-----------Polinominals-----------")
print(poly_own)
print(poly)

print("-----------error estimates -----------")
print(np.sqrt(del_m_sqrd + del_c_sqrd))
print(sigm_2)

print("----------- Residuals -----------")
print(res)
print(res_[0])


plt.errorbar(x, np.log10(y), yerr = new_err, fmt = "-o", label = "Data points")
plt.errorbar(x_num, np.polyval(poly, x_num), yerr = sigm_2, fmt = "-o", label = "model")
plt.legend()
plt.show()


plt.errorbar(x, y, yerr = 0.1*y, fmt = "-o", label = "Data points")
plt.errorbar(x_num, second_log_fit, yerr = second_log_fit*sigm_2, fmt = "-o",label = "log(y) first order fit")
plt.semilogy(x_num, log_fit, label = "semi log line, unweighted")
plt.xlabel("Ionization Potential, [ev]")
plt.ylabel("SF")
plt.legend()
plt.show()
