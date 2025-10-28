import pandas as pd
import util

path = "C:/Users/Susanto/Documents/Personal/HSILab/lib/pupilLabs-main/export/2025-05-07-10-36-27_1/csv/fixations.csv"


df = pd.read_csv(path)



print("Loaded file:", df)
print("Columns:", df.columns.tolist())



index_df=util.find_timestamp_candidates(df)
column_name=index_df['columns']

for column_name in column_name:
    df[column_name] = util.unix_to_readable(df[column_name], unit='ns')

df[column_name].dtype
print(df[column_name].dtype)


