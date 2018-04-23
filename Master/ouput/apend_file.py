

def main():

##	crc_file = open("crc_output.txt", "r")
##	crc = crc_file.read()

##	img_file = open("tx_bits_out.txt", "r")
##	img = img_file.read()
	
##	img_crc_file = open("img_crc_file.txt", "w")
##	img_crc_file.write(img)
##	img_crc_file.write(crc)

##	crc_file.close()
##	img_file.close()
##	img_crc_file.close()
	crc_file = input("crc_output.txt")
	img_file = input("tx_bits_out.txt")
	output_file = input("final_file.txt")
	fin = open(crc_file, "r")
	fin2 = open(img_file,"r")
	data2 = fin.read()
	data3 = fin2.read()
	fin2.close()
	fin.close()
	fout = 	open(output_file, "a")
	fout.write(data3)
	fout.write(data2)
	fout.close()
