---
title: Python_parse2
date: 2017-05-06 14:59:19.139000000 Z
---

import pandas as pd
url = './grad.html'

for i, df in enumerate(pd.read_html(url)):
    df.to_csv('b-myfile_%s.csv' % i)
