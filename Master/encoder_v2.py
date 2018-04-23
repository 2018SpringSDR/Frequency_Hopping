import Tkinter, tkFileDialog
import math
import os

metadata_EOF = '>.<'
metadata_data_seperator = '<>'
EOF_sequence = '}Q1~:eof'
postamble = 'vgCuE\':{'
SAVEFILE = 'file_tx_encoded.txt'


def main():
	''' ----- OBTAIN FILES FOR WHICH THE USER IS INTERESTED IN SENDING ----- '''
	files = get_files()
	create_file_blocks(files)
	
def get_files():
	root = Tkinter.Tk()
	files = tkFileDialog.askopenfilenames(parent = root, title = 'Choose a file')
	return files

def create_file_blocks(files):
	write_fptr = open(SAVEFILE, 'w')
	for file in files:
		_write_metadata(file, write_fptr)
		_write_file_contents(file, write_fptr)
		_write_EOF_sequence(write_fptr)
	_write_postamble(write_fptr)
	_pad_files(write_fptr)
	write_fptr.close()


def _write_metadata(file, write_fptr):
	#obtain file name
	addrs = file.split('/')
	file_name = addrs[len(addrs) - 1]
	#find file length in bytes
	file_size_bytes = os.path.getsize(file)
	#write to file
	write_fptr.write(file_name + metadata_data_seperator + str(file_size_bytes) + metadata_EOF)

def _write_file_contents(file_name, write_fptr):
	#find file size
	file_size_bytes = os.path.getsize(file_name)
	#open and read all data from file into file_data variable
	read_fptr = open(file_name, 'r')
	file_data = read_fptr.read()
	#use hamming 8,4 encoding to protect data
	encoded_file_data = _hamming_encoder(file_data)
	#convert from array of bytes to array of bits
	file_data_bits = _to_bits(encoded_file_data)
	#append if necessary
	while(len(file_data_bits) % 64 != 0):
		file_data_bits.append(0)
	print len(file_data_bits)
	#form num_rows by 64 bit matrix
	num_cols = 64
	num_rows = len(file_data_bits) / num_cols
	print num_cols
	print num_rows
	bit_matrix = [[0 for x in range(num_cols)] for y in range(num_rows)]
	#load bit matrix
	for i in range(num_rows):
		for j in range(num_cols):
			bit_matrix[i][j] = file_data_bits[(num_cols * i) + j]
	#interleave data
	index = 0
	temp_arr = [0] * 8
	interleaved_data = []
	interleaved_data_index = 0
	for j in range(num_cols):
		for i in range(num_rows):
			temp_arr[index] = bit_matrix[i][j]
			index = index + 1
			if index == 8:
				temp = _from_bits(temp_arr)
				interleaved_data.append(temp)
				index = 0
				interleaved_data_index = interleaved_data_index + 1
	#write interleaved data to transfer file
	for char in interleaved_data:
		write_fptr.write(char)
	#close read file
	read_fptr.close()

def _write_EOF_sequence(write_fptr):
	write_fptr.write(EOF_sequence)

def _write_postamble(write_fptr):
	write_fptr.write(postamble)

def _pad_files(write_fptr):
	padding = '0' * 400
	write_fptr.write(padding)

def _hamming_encoder(raw_data):
	#get current data in bits
	bits = _to_bits(raw_data)
	#create array to store encoded data
	encoded_data = [0] * 2 * len(bits)

	#be sure to account for all bits
	encoder_index = 0
	bit = 0
	while bit < len(bits):
		#obtain 4 bits of interest
		b0 = bits[bit]
		b1 = bits[bit + 1]
		b2 = bits[bit + 2]
		b3 = bits[bit + 3]
		bit = bit + 4

		#convert into 8 bits by multiplying by Hamming (8,4) Encoding Matrix
		#[1 1 1 0 0 0 0 1]
		#[1 0 0 1 1 0 0 1]
		#[0 1 0 1 0 1 0 1]
		#[1 1 0 1 0 0 1 0]
		encoded_data[encoder_index] = (b1 + b2 + b3) % 2
		encoded_data[encoder_index + 1] = (b0 + b2 + b3) % 2
		encoded_data[encoder_index + 2] = (b0 + b1 + b3) % 2
		encoded_data[encoder_index + 3] = (b0 + b1 + b2) % 2
		encoded_data[encoder_index + 4] = (b0) % 2
		encoded_data[encoder_index + 5] = (b1) % 2
		encoded_data[encoder_index + 6] = (b2) % 2
		encoded_data[encoder_index + 7] = (b3) % 2
		encoder_index = encoder_index + 8

	#turn back into string to write to file
	encoded_data = _from_bits(encoded_data)

	return encoded_data

def _to_bits(s):
	result = []
	for c in s:
		bits = bin(ord(c))[2:]
		bits = '00000000'[len(bits):] + bits
		result.extend([int(b) for b in bits])
	return result

def _from_bits(bits):
	chars = []
	for b in range(len(bits) / 8):
		byte = bits[b * 8:(b + 1) * 8]
		chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
	return ''.join(chars)

if __name__ == '__main__':
	main()