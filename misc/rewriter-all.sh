for i in _charts/*; do echo "=== $i ==="; if [ -f $i ]; then python3 rewriter.py $i; fi; done
