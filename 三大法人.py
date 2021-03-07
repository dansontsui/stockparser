import requests
from io import StringIO
import pandas as pd

import requests
from io import StringIO
import pandas as pd

date = '20180102'
#r = requests.get('http://www.tse.com.tw/fund/T86?response=csv&date='+date+'&selectType=ALLBUT0999')#
#df = pd.read_csv(StringIO(r.text), header=1).dropna(how='all', axis=1).dropna(how='any')
df = pd.read_csv("r.csv",encoding='utf-8')
df.to_csv("r1.csv", header=True, index=False, encoding='utf-8')
print(df)
