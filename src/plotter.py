import matplotlib.pyplot as plt
import pandas as pd
from housing_data import ZIP, PRICE, SCORE

# cluster and plot data
def plot(df: pd.DataFrame) -> None:

    # group by zip code
    dic = {}
    for _, row in df.iterrows():
        z, p, s = row[[ZIP, PRICE, SCORE]]
        group = dic.setdefault(z, [])
        group.append([p,s])

    for k, v in dic.items():
        if len(v) < 50: continue # drop small clusters
        plt.scatter(*zip(*v), label=f'{k}')
    plt.title('price and score correlation')
    plt.xlabel('price [CHF]')
    plt.ylabel('score')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()