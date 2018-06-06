import yaml

f = open("chartsubs.yaml")
chartsubs = yaml.load(f)
f.close()

counter = {}
for chartbase in chartsubs:
	num = len(chartsubs[chartbase])
	if not num in counter:
		counter[num] = 0
	counter[num] += 1

print(counter)
