allinfo=0
allwarning=0
allerror=0
chartsinfo=0
numcharts=0
alltxt=

predirs=`find -name Chart.yaml`
dirs=
for predir in $predirs; do x=`dirname $predir`; dirs="$dirs $x"; done

#dirs=_charts/*.tgz

for i in $dirs
do
	echo -n .
	lintput=`helm lint $i 2>&1`

	infotxt=`echo $lintput | grep INFO`
	info=`echo $lintput | grep INFO | wc -l`
	warning=`echo $lintput | grep WARNING | wc -l`
	error=`echo $lintput | grep Error | wc -l`

	allinfo=$(($allinfo+$info))
	allwarning=$(($allwarning+$warning))
	allerror=$(($allerror+$error))
	if [ $info -gt 0 ]
	then
		chartsinfo=$(($chartsinfo+1))
		infotxt="$infotxt\n"
	fi
	alltxt="$alltxt$infotxt"
	numcharts=$(($numcharts+1))
done
echo

echo "Infos: $allinfo (Charts: $chartsinfo of $numcharts)"
echo "Warnings: $allwarning"
echo "Errors: $allerror"
echo "All infos:"
echo $alltxt
