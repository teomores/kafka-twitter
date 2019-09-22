import pandas as pd
import os

data_folder = 'data/'
path, dirs, files = next(os.walk(data_folder))
file_count = len(files)
print(file_count)
files = pd.read_csv('data/twitter_dataset_1.csv', lineterminator='\n')


for j in range(file_count):
    df=pd.read_csv(data_folder+'twitter_dataset_{}.csv'.format(j+1), lineterminator='\n')
    files = files.append(df)
files.drop_duplicates(inplace=True)
files.drop_duplicates(subset = 'text',inplace=True)
print(files.shape)
files.to_csv('twitter_dataset.csv', encoding='utf-8', index=False)
