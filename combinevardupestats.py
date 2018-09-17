import json

varstr = open("variabilitystats.log").read()
var = eval(varstr)

dupstr = open("dupestats.log").readlines()[-1]
dup = eval(dupstr)

maxnum = max(max(var), max(dup))

print(var, dup, maxnum)

f = open("variabilitydupestats.csv", "w")
print("#numberofcharts,numberofdupes,numberofvariables", file=f)
for i in range(maxnum + 1):
	print("{},{},{}".format(i, dup.get(i, 0), var.get(i, 0)), file=f)
f.close()

# variabilitydupestats.csv:
# numberofcharts,numberofdupes,numberofvariables
# 1,31,26...
