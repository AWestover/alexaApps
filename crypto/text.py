def shift(t, x):  # shift all characters
	o = ""
	for c in t.lower():
		v = ord(c)-ord('a')
		if 0 <= v <= 25:
			o += chr(((v+x)%26)+ord('a')) 
		else:
			o += c
	print(o)
	return o