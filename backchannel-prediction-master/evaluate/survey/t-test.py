import sqlite3
import numpy as np
from scipy import stats
from itertools import combinations

conn = sqlite3.connect('db.sqlite')

c = conn.cursor()
meths = ["random", "nn", "truthrandom"]
methnames=dict(truthrandom="truth")
rating_types = ["timing", "naturalness"]
ratings = {}
are_samples_independent = True

for rating_type in rating_types:
    for meth in meths:
        _ratings = [rating for (rating,) in
                    c.execute('SELECT rating FROM net_rating WHERE ratingType=? AND final=1 AND segment LIKE ?',
                              (rating_type, f"/{meth}/%",)).fetchall()
                    ]
        print(f"loaded N={len(_ratings)} for {rating_type} on {meth}")
        ratings.setdefault(rating_type, {})[meth] = _ratings

sep = " & "
headers = ["Predictor 1", "Predictor 2", *[f"p-value ({type})" for type in rating_types]]

l0 = r'\begin{tabular}{' + ('c' * len(headers)) + '}'
l1 = r'\hline\noalign{\smallskip}'
l2 = r'\noalign{\smallskip}\svhline\noalign{\smallskip}'
l3=r'\noalign{\smallskip}\hline\noalign{\smallskip}' + '\n' + r'\end{tabular}'

print("% generated by backchannel-prediction/evaluate/survey/t-test.py")
print(l0)
print(l1)
print(sep.join(headers) + r" \\")
print(l2)
for meth1, meth2 in combinations(meths, 2):
    res = [methnames.get(meth, meth) for meth in [meth1, meth2]]
    for rating_type in rating_types:
        ratings2 = ratings[rating_type]
        if are_samples_independent:
            ttest = stats.ttest_ind(ratings2[meth1], ratings2[meth2], equal_var=False)
        else:
            ttest = stats.ttest_rel(ratings2[meth1], ratings2[meth2])
        res += [f"{ttest.pvalue*100:.3f}\\%"]
    print(sep.join(res) + r" \\")
print(l3)