import yaml

with open("chartsubs.yaml") as f:
    chartsubs = yaml.load(f)

counter = {}

for chartbase in chartsubs:
    num = len(chartsubs[chartbase])
    if num not in counter:
        counter[num] = 0
    counter[num] += 1

print(counter)
