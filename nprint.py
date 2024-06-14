import pandas as pd


filepath = input('News filepath: ')
df = pd.read_csv(filepath)

for _, row in df.iterrows():
    print(f'\n\n===== {row.ticker} - {row.title} =====\n[{row.published}] {row.description}\n==================================================================')
    input('>>> Press Enter to print the next one')