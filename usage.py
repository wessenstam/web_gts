import pandas as pd
import numpy as np
import json
import plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from csv import writer
import os.path

df=pd.read_csv("json/usage_vgts.csv")
df.set_index(['Cluster Name'])
print(df)




