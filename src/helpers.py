def publisherkey(dictionary):
	if 'publisher' in dictionary:
		return dictionary['publisher']
	else:
		return dictionary['copyright']