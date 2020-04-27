from json import loads
import pandas as pd

df = pd.read_csv("data.csv", sep=',').fillna('')

GAMES = {
    # 'y0': 'Yakuza 0',
    'ykw2': 'Yakuza Kiwami 2',
    'y4': 'Yakuza 4',
    'y5': 'Yakuza 5',
    'yds': 'Yakuza Dead Souls',
    'yish': 'Yakuza Ishin'
}

for game in GAMES:
    with open(f'./ids/{game}.json') as f:
        kw2 = loads(f.read())

    kw2_keys = set(kw2.keys())

    empty = df[GAMES[game]] == ''
    df.loc[empty, GAMES[game]] = df['Yakuza 0'].apply(lambda y: y if y in kw2_keys else '')

df.to_csv("out.csv", index=False)
