
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid", context="notebook") # Sets the style and context 
# Style: https://seaborn.pydata.org/tutorial/aesthetics.html
# Context: https://seaborn.pydata.org/generated/seaborn.set_context.html

# Read the data / validate
df = pd.read_csv('~/Desktop/storm_cleaned.csv')
print('Shape: ', df.shape)
print(df.head())
print(df.info())

# Cast datetime columns as datetime data type
df[['cre_dttm', 'restore_dttm']] = df[['cre_dttm', 'restore_dttm']].apply(pd.to_datetime)

# Create a date range to use as the index (to ensure evenly spaced intervals in the series)
dt_range = pd.DataFrame({'date': pd.date_range(start='2017-09-10', end='2018-04-23')}) # range of dates in this dataset

# Summing the affected customers by day (outcome: one row per day)
# And joining with date range created above
affected = df[['cre_dttm', 'affected_cust']].groupby(df['cre_dttm'].dt.date).sum() # sum affected cust by date
affected.index = pd.to_datetime(affected.index) # index to datetimeindex
affected = pd.merge(dt_range, affected, how='left', left_on='date', right_index=True).fillna(0).astype({'affected_cust':int}).set_index('date')

# Summing the restored customers by day (outcome: one row per day)
# And joining with date range created above
restored = df[['restore_dttm', 'affected_cust']].groupby(df['restore_dttm'].dt.date).sum() # sum restored cust by date
restored.rename(columns={'affected_cust':'restored_cust'}, inplace=True) # rename in prep for join
restored.index = pd.to_datetime(restored.index) # index to datetimeindex
restored = pd.merge(dt_range, restored, how='left', left_on='date', right_index=True).fillna(0).astype({'restored_cust':int}).set_index('date')

# join affected and restored
df = pd.merge(affected, restored, how='outer', left_index=True, right_index=True).fillna(0).astype({'affected_cust':int, 'restored_cust':int}) 

# Calculate the cumulative sums for affected and restored customers
df['affected_cumulative'] = df['affected_cust'].cumsum() # get the cumulative sum of affected customers by date
df['restored_cumulative'] = df['restored_cust'].cumsum() # get the cumulative sum of affected customers by date

# Calculated the unrestored customers by day
df['affected_current'] = df['affected_cumulative'] - df['restored_cumulative']

# Plot the affected customers
# g = sns.barplot(data=df, x=df.index.date, y='affected_current', color='steelblue')
g = sns.lineplot(data=df, x=df.index.date, y='affected_current', color='steelblue', linewidth=3)
g.set(title='Affected Customers During Storm', xlabel='', ylabel='Affected customers (thousands)')
plt.grid(axis='x')
ticks = ['2017-09-10', '2017-11-06', '2018-01-02', '2018-02-28', '2018-04-23']
plt.xticks(ticks, rotation=45)
ylabels = [int(x / 1000) for x in g.get_yticks()]
g.set_yticklabels(ylabels)
plt.tight_layout()
plt.show()