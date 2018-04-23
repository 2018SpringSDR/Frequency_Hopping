import Tkinter, tkFileDialog
import math

metadata_EOF = '>.<'
metadata_data_seperator = '<>'
EOF_sequence = '}Q1~:eof'
postamble = 'vgCuE\':{'

H = [[1, 0, 0, 0, 0, 1, 1, 1], [0, 1, 0, 0, 1, 0, 1, 1], [0, 0, 1, 0, 1, 1, 0, 1], [0, 0, 0, 1, 1, 1, 1, 0]]
H_tranposed = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]]

def main():
	#generate syndrome matrix
	syndrome_matrix = single_bit_syndrome_codes()

	#obtain file to decode
	fptr = choose_file_to_decode()

	#while the postamble has not been detected
	last_pos = fptr.tell()
	while(postamble_detected(fptr) != 1):
		#extract file name from hamming encoded file metadata
		fptr.seek(last_pos)
		[file_name, file_size] = get_metadata(fptr, syndrome_matrix)
		if file_name == 'error':
			print 'Error obtaining filename.\n'
			sys.exit()

		#generate files via hamming decoding
		create_file(file_name, fptr, syndrome_matrix, file_size)
		#update last_pos
		last_pos = fptr.tell()

def choose_file_to_decode():
	root = Tkinter.Tk()
	file = tkFileDialog.askopenfilename(parent = root, title = 'Choose a file')
	fptr = open(file, 'r')
	return fptr

def postamble_detected(fptr):
	data_check = fptr.read(8)
	if data_check == postamble:
		return 1
	return 0

def get_metadata(fptr, s):
	#get file_name
	file_name = ''
	data_check = fptr.read(1)
	while data_check != metadata_data_seperator[0]:
		file_name = file_name + data_check
		data_check = fptr.read(1)

	data_check = fptr.read(1)
	if data_check == metadata_data_seperator[1]:
		rtn_file_name = file_name

	#get file size
	file_size = ''
	data_check = fptr.read(1)
	while data_check != metadata_EOF[0]:
		file_size = file_size + data_check
		data_check = fptr.read(1)

	data_check = fptr.read(1)
	data_check2 = fptr.read(1)
	if data_check == metadata_EOF[1] and data_check2 == metadata_EOF[2]:
		rtn_file_size = int(file_size)

	return rtn_file_name, rtn_file_size

def create_file(file_name, r_fptr, s, file_size):
	w_fptr = open(file_name, 'w')
	
	file_contents = ''

	#CURRENTLY VERY INEFFICIENT DETECTION
	while eof_seq_detected(r_fptr) != 1:
		file_contents = file_contents + r_fptr.read(1)

	#fix interleaving
	file_contents = _fix_interleaving(file_contents, file_size)
	#decode hamming encoding
	decoded_file_contents = _hamming_decoder(file_contents, s)
	w_fptr.write(decoded_file_contents)
	w_fptr.close()

#THIS IS INCREDIBLY INEFFICIENT, NEEDS WORK
def eof_seq_detected(fptr):
	data_check = fptr.read(8)
	if data_check == EOF_sequence:
		return 1
	fptr.seek(-8, 1)
	return 0

def _fix_interleaving(file_contents, file_size):
	#convert retreived file contents to bits
	file_contents_bits = _to_bits(file_contents)
	#form bit matrix
	num_cols = 64
	num_rows = int(math.ceil(float(file_size) * 8 * 2 / num_cols))
	bit_matrix = [[0 for x in range(num_cols)] for y in range(num_rows)]
	#load bit matrix
	index = 0
	for j in range(num_cols):
		for i in range(num_rows):
			bit_matrix[i][j] = file_contents_bits[index]
			index = index + 1
	#convert into hamming encoded un-interleaved data
	temp_arr = [0] * 8
	encoded_data = ['a'] * file_size * 2
	index = 0
	for i in range(num_rows):
		for m in range(8):
			temp_arr[0] = bit_matrix[i][8*m]
			temp_arr[1] = bit_matrix[i][8*m + 1]
			temp_arr[2] = bit_matrix[i][8*m + 2]
			temp_arr[3] = bit_matrix[i][8*m + 3]
			temp_arr[4] = bit_matrix[i][8*m + 4]
			temp_arr[5] = bit_matrix[i][8*m + 5]
			temp_arr[6] = bit_matrix[i][8*m + 6]
			temp_arr[7] = bit_matrix[i][8*m + 7]
			#check to see if it was padding
			if index < file_size * 2:
				encoded_data[index] = _from_bits(temp_arr)
				index = index + 1
	return encoded_data


def _hamming_decoder(data, s):
	#convert data to array of 1's and 0's that represent its bit composition
	bits = _to_bits(data)

	#create array to contain decoded bits
	no_decoded_bits = len(bits) / 2
	decoded_bits = [0] * no_decoded_bits

	#iterate through all bits
	decode_index = 0
	bit = 0
	syndrome = [0, 0, 0 ,0]
	while bit < len(bits):
		#generate syndrome:  (recv_bits * H_tranpose) % 2
		syndrome[0] = (bits[bit] + bits[bit + 5] + bits[bit + 6] + bits[bit + 7]) % 2
		syndrome[1] = (bits[bit + 1] + bits[bit + 4] + bits[bit + 6] + bits[bit + 7]) % 2
		syndrome[2] = (bits[bit + 2] + bits[bit + 4] + bits[bit + 5] + bits[bit + 7]) % 2
		syndrome[3] = (bits[bit + 3] + bits[bit + 4] + bits[bit + 5] + bits[bit + 6]) % 2

		#check to see if syndrome == [0 0 0 0], as this implies no data corruption
		error_fixed = 1
		if syndrome != [0,0,0,0]:
			error_fixed = 0
			#check for every single bit error
			for i in range(0,8):
				#if syndrome matches syndrome table
				if syndrome == s[i]:
					#flip bit
					if bits[i] == 1:
						bits[i] = 0
					else:
						bits[i] = 1
					error_fixed = 1
		
		#decode hamming data points
		decoded_bits[decode_index] = bits[bit + 4]
		decoded_bits[decode_index + 1] = bits[bit + 5]
		decoded_bits[decode_index + 2] = bits[bit + 6]
		decoded_bits[decode_index + 3] = bits[bit + 7]

		#update indexes
		bit = bit + 8
		decode_index = decode_index + 4

	#convert decoded_bits back to string
	decoded_str = _from_bits(decoded_bits)

	return decoded_str

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

def single_bit_syndrome_codes():
	s = [[0 for x in range(4)] for y in range(8)]
	e = [0,0,0,0,0,0,0,0]

	for i in range(0,8):
		e[i] = 1
		s[i][0] = (e[0] + e[5] + e[6] + e[7]) % 2
		s[i][1] = (e[1] + e[4] + e[6] + e[7]) % 2
		s[i][2] = (e[2] + e[4] + e[5] + e[7]) % 2
		s[i][3] = (e[3] + e[4] + e[5] + e[6]) % 2

		e[i] = 0  #reset error array to all zeros

	return s

if __name__ == '__main__':
	main()