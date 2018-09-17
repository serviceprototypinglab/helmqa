import os
import json
import time
import getpass
import itertools

username = input("Github username? ")
password = getpass.getpass("Github password? ")

allrepos = {}
totalcount = 0
for page in itertools.count(1):
	if page == 11:
		print("interrupting due to search restrictions")
		break
	penalty = 10
	while True:
		os.system("curl -su {}:{} 'https://api.github.com/search/code?q=filename:Chart.yaml&per_page=100&page={}' -o gitloader.json".format(username, password, page))
		time.sleep(4)

		results = json.load(open("gitloader.json"))

		if not "documentation_url" in results:
			break

		print("penalty: {}s...".format(penalty))
		time.sleep(penalty)
		penalty *= 2
		continue

	if not totalcount:
		totalcount = results["total_count"]
	if page * 100 > totalcount:
		break

	repos = set()
	for item in results["items"]:
		repo = item["repository"]["full_name"]
		if repo in allrepos:
			allrepos[repo] += 1
		else:
			allrepos[repo] = 1
	print("loading: {} of {}... ({} unique results)".format(page * 100, totalcount, len(allrepos)))

print("Statistics:")
print(" total Helm charts (Chart.yaml): ", results["total_count"])
print(" total repositories:", len(allrepos))

f = open("gitloader.csv", "w")
print("#repo,chartcount", file=f)
for repo in allrepos:
	print("{},{}".format(repo, allrepos[repo]), file=f)
f.close()
