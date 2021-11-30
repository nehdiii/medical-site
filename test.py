import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from app.models import db,CoronaDailyUpdateds
import requests
from bs4 import BeautifulSoup
from sklearn import metrics

df = pd.read_csv('C:/Users/DELL/PycharmProjects/MedicalSite/app/static/csv/confirmed.csv')
x = np.array(df['id']).reshape(-1, 1)
y = np.array(df['total_cases']).reshape(-1, 1)
plotlyFeat = PolynomialFeatures(degree=4)
x = plotlyFeat.fit_transform(x)
model = linear_model.ElasticNet(alpha=0.1, l1_ratio=0.9, selection='random', random_state=42)
model.fit(x, y)
plt.plot(y,'--r')
y0 = model.predict(x)
plt.plot(y0,'--b')
plt.show()
print(model.score(x,y))
print(int(model.predict(plotlyFeat.fit_transform([[df.shape[0]+1]]))[0]))