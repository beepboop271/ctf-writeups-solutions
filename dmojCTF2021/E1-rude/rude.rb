# call this function!
def flag()
	## SECRET ##
end

a, b, c = IO.new(0).readline().chomp.split

Object.const_get(a).send(b, c)