#!/usr/bin/env python3

from collections import defaultdict
import statistics
import fileinput
import scipy.stats as st

def main():
    d = defaultdict(list)
    for inp in fileinput.input():
        approach, real = inp.split()
        d[approach].append(float(real))

    for k in d.keys():
        vals = d[k][:12]
        sample_mean = sum(vals)/len(vals)
        sample_stdev = statistics.stdev(vals, xbar=sample_mean)
        interval = st.t.interval(0.95, len(vals)-1, loc=sample_mean, scale=st.sem(vals))
        print(k)
        print(f"Sample mean: {sample_mean}")
        print(f"Sample standard deviation: {sample_stdev}")
        print(f"Interval: {interval}")

if __name__ == "__main__":
    main()
