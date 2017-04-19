import pandas as pd
url = './fac.html'

for i, df in enumerate(pd.read_html(url)):
    df.to_csv('myfile_%s.csv' % i)
