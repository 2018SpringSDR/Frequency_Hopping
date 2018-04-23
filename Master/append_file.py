import math
import os

def main(file_bits, crc_file):
	print("Check1")
	first_part = open("crc_input.txt", "r")
	new_file = open("appended_file.txt", "w+")
	result = transfer_bits(first_part, new_file)	#call function where the opened file has its bits read and encoded to a different file
	if result == err:
		print("CRC was unable to be transferred to new file!")
		return 0

	second_part = open("tx_bits_out.txt", "r")
	transfer_bits(second_part, new_file)
	if result == err:
		print("File bits were unable to be transferred to new file!")
		return 0



def transfer_bits(any_file,receiving_file):  #How to make the receiving_file stay constant throughout algorithm
	while True:                #Generate while loop that will stop once it reaches the end of the file (EOF)
		file_data = fp.read(any_file)          #get bits from any_file
		if file_data == '':
			break
	receiving_file.write(file_data)          #transfer bits to receiving_file
	receiving_file.seek(0)			#checking if file write was successful
	file_check = receiving_file.read(1)
	if file_check == '':
		return err
	return receiving_file
