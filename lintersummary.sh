allinfo=0
allwarning=0
chartsinfo=0
numcharts=0
alltxt=

for i in _charts/*.tgz
do
	echo -n $counter

	lintput=`helm lint $i`

	infotxt=`echo $lintput | grep INFO`
	info=`echo $lintput | grep INFO | wc -l`
	warning=`echo $lintput | grep WARNING | wc -l`

	allinfo=$(($allinfo+$info))
	allwarning=$(($allwarning+$warning))
	if [ $info -gt 0 ]
	then
		((chartsinfo++))
		infotxt="$infotxt\n"
	fi
	alltxt="$alltxt$infotxt"
	((numcharts++))
done
echo

echo "Infos: $allinfo (Charts: $chartsinfo of $numcharts)"
echo "Warnings: $allwarning"
echo "All infos:"
echo $alltxt