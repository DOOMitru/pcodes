import re
import csv
import json
import sys
import time
import urllib2

GEOCODER_URL = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=true&address='

RAW_FILE = 'raw.txt'
VALID_FILE = 'valid.txt'
OUTPUT_FILE = 'output.js'

invalid_codes_counter = 0
zero_results_counter = 0
unique_codes_counter = 0
valid_codes_counter = 0

most_popular_code = ''
highest_code_count = 0
line_number = 0

def StripLine(pcode):
	return pcode.replace(' ', '').strip(' \t\n\r').upper()

def IsValidPostalCode(pcode):
	if re.match(r'[A-Z][0-9][A-Z][0-9][A-Z][0-9]', pcode):
		return True
	return False

def GetCodeDict(codes):
	global invalid_codes_counter
	global valid_codes_counter
	global unique_codes_counter
	global highest_code_count
	global most_popular_code

	print 'Building dictionary of postal codes...'
	code_dict = {}

	for pcode in codes:
		if not IsValidPostalCode(pcode):
			invalid_codes_counter += 1
			print 'Invalid code: ' + pcode
		else:
			valid_codes_counter += 1

			if code_dict.has_key(pcode):
				if(code_dict[pcode] > highest_code_count):
					most_popular_code = pcode
					highest_code_count = code_dict[pcode]
				code_dict[pcode] += 1
			else:
				code_dict[pcode] = 1
				unique_codes_counter += 1

	return code_dict

def BuildValidFile(codes):

	global VALID_FILE

	print 'Building file of properly formatted codes...'

	valid_file = open(VALID_FILE, 'w')

	for pcode, count in codes.iteritems():
		valid_file.write(pcode + ',' + str(count) + '\n')

	valid_file.close()

def GetLatLng(code):
	global line_number
	global zero_results_counter

	line_number += 1

	try:
		response = urllib2.urlopen(GEOCODER_URL + code)
		json_response = json.load(response)

		status = json_response['status']
		results = json_response['results']

		if status == 'OK':
			lat = results[0]['geometry']['location']['lat']
			lng = results[0]['geometry']['location']['lng']
			return (lat, lng)

		if status == 'ZERO_RESULTS':
			zero_results_counter += 1

		print 'STATUS: ' + status + ', ' + str(line_number) + ', ' + code
		return (0, 0)

	except urllib2.HTTPError, e:
		print 'HTTP error:', e.code
		return (0, 0)
	except urllib2.URLError, e:
		print 'Server Failure:', e.reason
		return (0, 0)

def BuildOutputFile(lines, print_output = True):

	print 'Building output file...'
	output_file = open(OUTPUT_FILE, 'w')

	output_file.write('var postal_codes = [\n');	

	for line in lines:
		postal_code,count = line.split(',')
		lat,lng = GetLatLng(postal_code)
		
		if print_output:
			print 'line: ' + str(line_number) + ', code: ' + postal_code + ', count = ' + count

		if lat != 0 and lng != 0:
			output = '\t{ postal_code: \'' + postal_code + '\', count: ' + str(count) + ', '
			output += 'lat: ' + str(lat) + ', lng: ' + str(lng) + ' },\n';

			output_file.write(output)

		time.sleep(0.15)

	output_file.write('];\n')
	output_file.close()

if __name__ == '__main__':
	
	raw_codes = [StripLine(line) for line in open(RAW_FILE, 'r')]
	code_dict = GetCodeDict(raw_codes)
	print str(invalid_codes_counter) + ' invalid codes found...'

	BuildValidFile(code_dict)

	lines = [line.strip(' \n') for line in open(VALID_FILE, 'r')]

	#BuildOutputFile(lines)

	print ''

	print str(zero_results_counter) + ' ZERO_RESULTS generated...'
	print str(valid_codes_counter) + ' valid postal codes found...'
	print str(invalid_codes_counter) + ' invalid postal codes found...'
	print str(unique_codes_counter) + ' unique postal codes found...'
	print 'The most popular zip code is ' + most_popular_code + ' (' + str(highest_code_count) + ')'

	print '\nAll Done!'