# Evaluate bad samples.
import numpy             as np
import matplotlib.pyplot as plt

from json    import load
from sys     import argv
from os.path import dirname, join


def int_MakeBadSampleDistChart(file) -> None:
    # (1) Load results file.
    try:
        with open(file, 'r') as f:
            obj = load(f)
    except Exception as e:
        print(f'error: Could not read results file "{file}". Reason: {e}')

    # (2) Get data.
    part = [obj[x]['partial'] for x in sorted(obj.keys(), key=lambda x: int(x))]
    obs  = [obj[x]['obstructed'] for x in sorted(obj.keys(), key=lambda x: int(x))]
    X    = np.arange(4)
    L    = ['KA', 'SB', 'IB', 'U']
    W    = 0.35

    # (3) Make plot.
    _, ax = plt.subplots()
    prtBars = ax.bar(X - W/2, part, W, label='eyes only partially in frame')
    obsBars = ax.bar(X + W/2, obs, W, label='obstructed by nose ridge')
    plt.ylim(0, max(part + obs) * 1.2)
    plt.bar_label(prtBars, padding=3)
    plt.bar_label(obsBars, padding=3)
    plt.legend()
    ax.set_xlabel('Regions')
    ax.set_ylabel('Number of found items [n]')
    ax.set_xticks(X)
    ax.set_xticklabels(L)

    # (4) Save the thing.
    plt.savefig(join(dirname(file), 'BadSamplesDist.pdf'), dpi=300)


if __name__ == '__main__':
    cfg = argv[1]

    int_MakeBadSampleDistChart(cfg)
    exit(0)


    