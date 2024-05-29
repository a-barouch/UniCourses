import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# todo get code to create data

# read in a dataframe of sizes
df = pd.read_csv('run_results/updatesVsSize_M500_9993.csv', sep="\t",index_col=0)
corr1, p1 = scipy.stats.pearsonr(df['updatesLast5YearsMain'], df['pageSize'])
x = df['pageSize']
y = df['updatesLast5YearsMain']
sns.regplot(x, y, ci=None)
plt.xlabel("Article Size")
plt.ylabel("#edits in the last 5 years")
plt.yscale('log')
plt.xscale('log')
plt.savefig("page size edits correlation.png")
plt.show()


print("Correlation = "+str(corr1)+", p value = "+str(p1))
print()