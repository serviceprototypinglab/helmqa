import tarfile
import os
import subprocess


def rewritechart(chartfile, dupeslist):
    try:
        subprocess.call(["rm", "-rf", "_rewriter"])
        subprocess.call(["mkdir", "-p", "_rewriter/orig"])
        subprocess.call(["mkdir", "-p", "_rewriter/deduped"])
        subprocess.call(["mkdir", "-p", "_diffs"])
    except OSError as os_err:
        print(os_err)
        exit(1)

    tar = tarfile.open(chartfile)
    tar.extractall("_rewriter/orig")
    tar.extractall("_rewriter/deduped")

    for varcounter, (v, count) in enumerate(dupeslist):
        v = v.replace("\\", "\\\\")
        v = v.replace("/", "\\/").replace("'", "'\\''").replace("[", "\\[")
        v = v.replace("TEMPLATE", "")

        cmd = "for i in `find _rewriter/deduped/*/templates/ -name *.yaml`;" \
              f" do sed -i -e 's/: \(.*\){v}$/: \\1{{{{ .suggestions.var{varcounter} }}}}/' $i; done"

        os.system(cmd)

    p = subprocess.run("diff -Nur _rewriter/orig/ _rewriter/deduped/", shell=True, stdout=subprocess.PIPE)
    diff = p.stdout

    difffile = os.path.join("_diffs", os.path.basename(chartfile).replace(".tgz", "-deduplicated.diff"))

    with open(difffile, "wb") as f:
        f.write(diff)

    p = subprocess.run(f"diffstat {difffile} | tail -1 | sed 's/insertions.*//'", shell=True,
                       stdout=subprocess.PIPE)

    lines = p.stdout.decode("utf-8").strip().split(" ")[-1]

    if lines == "changed":
        lines = 0
        extraeffect = 0
    else:
        lines = int(lines)
        extraeffect = lines - sum([x[1] for x in dupeslist])

    print("effect", lines, "= +", extraeffect)

    dirname = os.listdir("_rewriter/deduped")[0]

    with open(f"_rewriter/deduped/{dirname}/values.yaml", "a") as f:
        print("", file=f)
        print("suggestions:", file=f)

        for varcounter, (v, count) in enumerate(dupeslist):
            print(f"  var{varcounter}: {v}", file=f)

    p = subprocess.run("diff -Nur _rewriter/orig/ _rewriter/deduped/", shell=True, stdout=subprocess.PIPE)
    diff = p.stdout

    with open(difffile, "wb") as f:
        f.write(diff)
