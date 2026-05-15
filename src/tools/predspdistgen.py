from sys               import argv
from json              import load, dumps
from os                import listdir, makedirs
from os.path           import join, exists
from matplotlib.pyplot import hist2d, savefig, figure, close, colorbar, close, subplots
from matplotlib.colors import LogNorm

import datetime as dt


def int_FixToGlobalCoordinateSystem_Identity(r, x, y) -> tuple[float, float]:
    return x, y

def int_FixToGlobalCoordinateSystem_Global(r, x, y) -> tuple[float, float]:
    # TODO: implement
    return x, y


if __name__ == '__main__':
    datadir = argv[1]
    resdir  = argv[2]
    cfgfile = argv[3]
    dbg     = '-d' in argv or '--debug'    in argv
    sep     = '-s' in argv or '--separate' in argv

    # (1) Merge all data into one object per region.
    fps = 60.0
    regions = {} if sep else {'x': [], 'y': []}
    for f in listdir(datadir):
        if not f.endswith('.json'):
            continue

        with open(join(datadir, f), 'r') as fp:
            parsed = load(fp)

            _, rr = f.split('_')
            r, _  = rr.split('.')

            if sep and not int(r) in regions.keys():
                regions[int(r)] = {
                    'x': [],
                    'y': []
                }
            for v in parsed.values():
                if sep:
                    x, y = int_FixToGlobalCoordinateSystem_Identity(int(r), *list(v.values()))

                    regions[int(r)]['x'].append(x)
                    regions[int(r)]['y'].append(y)
                else:
                    x, y = int_FixToGlobalCoordinateSystem_Global(int(r), *list(v.values()))

                    regions['x'].append(x)
                    regions['y'].append(y)

    # (INTERM) If we are debugging, write the preprocessed region data to an
    # extra file for inspection.
    if dbg:
        with open('prep_pos.json', 'w') as o:
            o.write(dumps(regions, indent=4))

            print('Saved preprocessed position data under "prep_pos.json".')

    # (2.1) Get aspect ratios for regions from session config.
    ar = {}
    with open(cfgfile) as fp:
        sesscfg = load(fp)

        for v in sesscfg['stages']:
            if 'region' not in v.keys():
                continue

            l, t, r, b = [v for k, v in v['region'].items() if k in ['left', 'top', 'right', 'bottom']]
            ar[int(v['id'])] = (r - l) / (b - t) * 1.9737

    # (2.2) Create the histograms.
    if not exists(resdir):
        makedirs(resdir)
    for h in ar.keys():
        x, y = regions[h]['x'], regions[h]['y']
        a    = ar[h]

        fig, ax = subplots()
        bins    = (round(30 * a), 30) if h != 1 else (round(13 * a), 13)
        hh      = ax.hist2d(x, y, bins, range=[[0.0, 1.0], [0.0, 1.0]], cmap='viridis')

        fig.colorbar(hh[3], label='Count', orientation='horizontal')
        ax.set_aspect(1 / a)
        savefig(
            join(resdir, f'PredspaceDist_Reg{h}_{dt.datetime.now().strftime("%Y-%m-%d")}.png'),
            dpi=300,
            bbox_inches='tight'
        )
        close(fig)

    exit(0)


