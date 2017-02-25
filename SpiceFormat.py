# Seo Bo Shim
# last modified: 2/25/2017 - 2:46 am
#
# Tested with:
# OrCAD Capture CIS Lite: 16.6-2015 Lite

'''
Run this program to format spice.out files to a custom format.

For each lab report:
1. DELETE .numOutputs file if it exists.
2. Specify needed values in 'class out_format(Enum)'
3. run 'python SpiceFormat.py' in directory with spice.out file
4. repeat 2 after each spice.out generation (after each simulation run)
5. Check output.txt to see all formatted, numbered spice.out outputs in one file.

'''

from enum import Enum

#user define
SKIP_LINES_MAX = 30
SPICE_OUTPUT_FILE = 'spice4.out'
TEXT_OUTPUT_FILE = 'output.txt'
NUM_OUTPUT_FILE = ".numOutputs.txt"

# 1 if desired in output
# 0 if not desired in output
class out_format(Enum):
	NUMBER = 1;		# number label: "SPICE.OUT FILE #X  "
	HEADER = 1;		# Appropriate headers specified below: "*** PSPICE Output File ..."
	VOLTAGES = 1;	# Voltage sources in netlist
	RESISTORS = 1;	# Resistors in netlist
	DIODES = 1;		# Diodes in netlist
	TRANSISTORS = 0;# Transistors in netlist
	ANALYSIS = 1;	# Analysis mode. 
	NODE_VOLTAGES = 1;
	VOLTAGE_SOURCE_CURRENTS = 1;
	TOTAL_POWER_DISSIPATION = 1;
'''
To modify output headers and output data, make sure out_sections is updated with the necessary headers. This is wh
Output:

output_header 1
out_data 1
output_header 2
out_data 2
...


'''
output_header = {
	'NUMBER': "",
 	'HEADER': "*** PSPICE Output File ***\n****  CIRCUIT DESCRIPTION",
	'VOLTAGES': "* Voltages\n",
	'RESISTORS': "* Resistor\n",
	'DIODES': "* Diodes\n",
	'TRANSISTORS': "* Transistors\n",
	'ANALYSIS': "*Analysis\n",
	'NODE_VOLTAGES': " ****   NODE VOLTAGES\n",
	'VOLTAGE_SOURCE_CURRENTS': " ****   VOLTAGE SOURCE CURRENTS\n",
	'TOTAL_POWER_DISSIPATION': " ****   TOTAL POWER DISSIPATION\n"
	}

def main():
	#include section here.
	out_sections = ['NUMBER','HEADER', 'VOLTAGES', 'RESISTORS', 'DIODES', 'TRANSISTORS', 'ANALYSIS', 'NODE_VOLTAGES', 'VOLTAGE_SOURCE_CURRENTS', 'TOTAL_POWER_DISSIPATION']
	out_data = { }
	out_data['NUMBER'] = "\n\n"
	out_data['HEADER'] = "\n"
	numbering = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20"]
	#end user defined vars here

	#start parsing file
	spice_out_num = 0
	f = open(SPICE_OUTPUT_FILE, 'r+')
	output =  open(TEXT_OUTPUT_FILE, 'a+')	#appends to file
	try:
		numfile = open(NUM_OUTPUT_FILE, "x")
	except:
		numfile = open(NUM_OUTPUT_FILE, "r+")
		line = numfile.readline()
		numfile.seek(0,0)
		numfile.truncate()
		#print(line)
		for num in numbering:
			if (num in line):
				spice_out_num = int(num) + 1
				break
			else:
				spice_out_num = 1
	else:
		spice_out_num = 1
			
	current_line = f.readline()
	#print(current_line)
	output_header['NUMBER'] = "\n\n**********SPICE.OUT FILE #" + str(spice_out_num) + "**********\n"

	skipLinesUntil(f,current_line, "*Analysis directives:")
	current_line = f.readline()
	analysis = current_line
	#analysis += '\n'
	out_data['ANALYSIS'] = analysis

	skipLinesUntil(f,current_line, "**** INCLUDING")
	current_line = f.readline()
	current_line = f.readline()

	#schematics
	R = " ";
	V = " ";	#we will assume next line of V is pulse info
	D = " ";
	T = " ";
	n = 0
	while n == 0:
		print(current_line)
		if 'R_' in current_line:
			R = R + current_line
			#R += '\n'
		elif 'V_' in current_line:
			V += current_line
			current_line = f.readline()
			V += current_line
			#V += '\n'
		elif 'D_' in current_line:
			D += current_line
			#D += '\n'
		elif 'T_' in current_line:
			T += current_line
			#T += '\n'
		else:
			n = 1
		current_line = f.readline()

	out_data['VOLTAGES'] = V
	out_data['RESISTORS'] = R
	out_data['DIODES'] = D
	out_data['TRANSISTORS'] = T

	DIODE_MODEL = "Diode MODEL"
	DM = '';
	skipLinesUntil(f,current_line, DIODE_MODEL)
	for x in range(1,7):
		current_line = f.readline()


	while ("PSpice" not in current_line):
		if (current_line != " "):
			DM += current_line
			#print(current_line)
		current_line = f.readline()

	#in diode model param, reduce # of spaces
	#append diode medel to after diode found in circuit

	#while not (ANALYSIS_EXP in current_line):
	Nvoltage = '';
	skipLinesUntil(f,current_line, "NODE")
	for x in range(1,4):
		current_line = f.readline()
		#print(current_line)
	Nvoltage += current_line			# assuming only one line of nodes
	print(current_line)
	out_data['NODE_VOLTAGES'] = Nvoltage


	for x in range(1,5):
		current_line = f.readline()
		#print(current_line)
	skipLinesUntil(f,current_line,"VOLTAGE SOURCE CURRENTS")
	VSC = '';
	current_line = f.readline()
	VSC += current_line
	current_line = f.readline()
	current_line = f.readline()
	print(current_line)
	while ("V_" in current_line):
		#print(current_line)
		VSC += current_line
		current_line = f.readline()
	out_data['VOLTAGE_SOURCE_CURRENTS'] = VSC
	current_line = f.readline()
	skipLinesUntil(f,current_line,"POWER")
	out_data['TOTAL_POWER_DISSIPATION'] = current_line

	#write to output
	for section in out_sections: #iterate through all possible sections
		if (out_format[section].value == 1):	# if section specified, 
			output.write(output_header[section])	# print header
			if (out_data[section]):
			 	output.write(out_data[section])
	
	if (spice_out_num < 10):
		numfile.write("0")
		numfile.write(str(spice_out_num))
	else:
		numfile.write(str(spice_out_num))

	f.close()
	output.close()
	numfile.close()

def skipLinesUntil(f, current_line, expression):
	i = 0;
	while not (expression in current_line):	
		current_line = f.readline()
		if (i>SKIP_LINES_MAX):
			print('expression not found')
		i+=1

if __name__=="__main__":
   main()