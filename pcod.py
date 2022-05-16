#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sodapy import Socrata

%matplotlib

# get data (Homeless Persons Who Regain Housing) from Socrata/Pierce Co API as dataframe
client = Socrata("internal.open.piercecountywa.gov", None)
pchs = client.get("qghi-2efp")
pchs_df = pd.DataFrame.from_records(pchs, index='date') #index on 'date'

# convert dtype of index from str to datetime
pchs_df.index = pd.to_datetime(pchs_df.index)

#-----Data quality checks------------------------------------

#inspect structure, dtypes, nulls
pchs_df.info()

# convert dtypes of cols: 'number_served', 'year', 'date'
pchs_df = pchs_df.astype({'number_served': 'int64', 
                          'annual_cumulative_distinct': 'int64',
                          'year_end_target': 'int64'})

pchs_df['year'] = pd.to_datetime(pchs_df['year']).dt.year

# convert strs in 'month' to ints
mo_map = {'January':1, 'February':2, 'March':3, 'April':4,
          'May': 5, 'June': 6, 'July': 7, 'August': 8,
          'September': 9, 'October': 10, 'November': 11, 'December': 12 }
pchs_df['month'] = pchs_df['month'].map(mo_map)

pchs_df.duplicated()
pchs_df.duplicated(subset=['year', 'month']) # duplicate Jan (Jan 1) entry in 2019 
pchs_df = pchs_df.drop(pd.Timestamp('2019-01-01'))

# TODO (Lee) check annual cumulative sum correctly from number_served

#-----Data transformations-------------

# add new col with month-over-month % change in # homeless persons regaining housing (# served)
pchs_df['pct_chg_no_served_mom'] = pchs_df['number_served'].pct_change()

# add new col with year-over-year % change in # homeless persons regaining housing (# served)
# pchs_yoy_df['pct_chg_no_served_yoy'] = pchs_yoy_df['number_served'].pct_change(12)

# create new df of year-level data (total persons housed, performance target) from December obs
pchs_ann_df = pchs_df[['year', 'annual_cumulative_distinct', 'year_end_target']][pchs_df['month'] == 'December']

# pct of target
pchs_ann_df = pchs_ann_df.astype({'annual_cumulative_distinct': 'int64'})
pchs_ann_df['pct_change'] = pchs_ann_df['annual_cumulative_distinct'].pct_change()

# Calculate annual means and quarterly means:
# annual mean
# monthly mean

# ----------
df_15_18 = pchs_df.iloc[0:48]
df_19 = pchs_df.iloc[48:60]
df_20_21 = pchs_df.iloc[60:84]

dfx_15_18 = df_15_18.copy()
dfx_19 = df_19.copy()
dfx_20_21 = df_20_21.copy()

fig, ax = plt.subplots(1, 3, sharex='col', sharey='row', figsize=(15,5))
ax[0].scatter(dfx_15_18.index, dfx_15_18['number_served'])
ax[1].scatter(dfx_19.index, dfx_19['number_served'])
ax[2].scatter(dfx_20_21.index, dfx_20_21['number_served'])

plt.tight_layout()

ax[0].tick_params(rotation=90)
ax[1].tick_params(rotation=90)
ax[2].tick_params(rotation=90)

x1518 = mdates.date2num(df_15_18.index)
y1518= df_15_18['number_served']
z = np.polyfit(x1518, y1518, 1)
p = np.poly1d(z)
ax[0].plot(x1518, p(x1518),"r--")

x2021 = mdates.date2num(df_20_21.index)
y2021= df_20_21['number_served']
z = np.polyfit(x2021, y2021, 1)
p = np.poly1d(z)
ax[2].plot(x2021,p(x2021),"r--")

fig.savefig('pcod.jpg')

# convert datetime idx to ordinal vals to plot a regression line
# dfx_15_18.index = dfx_15_18.index.map(pd.Timestamp.toordinal)
# dfx_19.index = dfx_19.index.map(pd.Timestamp.toordinal)
# dfx_20_21.index = dfx_20_21.index.map(pd.Timestamp.toordinal)

# fig, ax = plt.subplots(1, 3, sharex='col', sharey='row')
# ax[0].plot(dfx_15_18.index, dfx_15_18['number_served'])
# ax[1].plot(dfx_19.index, dfx_19['number_served'])
# ax[2].plot(dfx_20_21.index, dfx_20_21['number_served'])

# scratch notes
# convert the axis back to datetime
# xticks = ax1.get_xticks()
# labels = [pd.Timestamp.fromordinal(int(label)).date() for label in xticks]
# ax1.set_xticks(xticks)
# ax1.set_xticklabels(labels)

# ax[0] = sns.regplot(x=df_15_18.index, y='number_served', data=df_15_18)

# fig.tight_layout()
# ax[0].autoscale(tight=True)
# ax[1].autoscale(tight=True)
# ax[2].autoscale(tight=True)

# xlab1518 = df_15_18.index.strftime("%Y-%m")
# xlab19 = df_19.index.strftime("%Y-%m")
# xlab2021 = df_20_21.index.strftime("%Y-%m")

# xticks_15_18 = ax[0].get_xticks()
# labels_15_18 = [pd.Timestamp.fromordinal(int(label)).date() for label in xticks_15_18]
# ax[0].set_xticks(xticks_15_18)
# fig.set_size_inches([11.12, 5.5])