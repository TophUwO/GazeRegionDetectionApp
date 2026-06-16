# Generate plots and graphs from evaluation file.
from json            import load
from sys             import argv
from os              import listdir, makedirs
from os.path         import exists, join
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report

import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def int_GenerateLossGraph(trLossX, trLossY, evLossX, evLossY, dir, lim) -> None:
    lim = min(int(lim), len(trLossX))

    plt.figure()
    plt.plot(trLossX[0:lim], trLossY[0:lim], label='train loss', marker='o')
    plt.plot(evLossX[0:lim], evLossY[0:lim], label='eval loss', marker='o')
    plt.legend()
    plt.xlabel('Epoch [n]')
    plt.ylabel('Loss')
    plt.xlim(0, min(len(trLossY), lim) + 1)
    plt.ylim(0, max(max(trLossY), max(evLossY)) * 1.2)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.savefig(join(dir, f'LossPlot_Total.pdf'), dpi=300)
    plt.close()

    print(f'Saved loss plot under "{join(dir, "LossPlot_Total.pdf")}".')


def int_GenerateAccGraph(trAccX, trAccY, evAccX, evAccY, dir, lim) -> None:
    lim    = min(int(lim), len(trAccX))
    trAccY = [x * 100.0 for x in trAccY]
    evAccY = [x * 100.0 for x in evAccY]

    plt.figure()
    plt.plot(trAccX[0:lim], trAccY[0:lim], label='train accuracy', marker='o')
    plt.plot(evAccX[0:lim], evAccY[0:lim], label='eval accuracy', marker='o')
    plt.legend()
    plt.xlabel('Epoch [n]')
    plt.ylabel('Accuracy [%]')
    plt.xlim(0, min(len(trAccY), lim) + 1)
    plt.ylim(0, max(max(trAccY), max(evAccY)) * 1.2)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.savefig(join(dir, f'AccPlot_Total.pdf'), dpi=300)
    plt.close()

    print(f'Saved accuracy plot under "{join(dir, "AccPlot_Total.pdf")}".')


def int_GenerateCombinedLossAndAccuracyGraph(stats, dir, lim) -> None:
    trLossX = stats.get('trELossesX', [])
    trLossY = stats.get('trELossesY', [])
    evLossX = stats['evLossesX']
    evLossY = stats['evLossesY']
    trAccX  = stats.get('trEAccX', [])
    trAccY  = [x * 100.0 for x in stats.get('trEAccY', [])]
    evAccX  = stats['evAccX']
    evAccY  = [x * 100.0 for x in stats['evAccY']]

    lim = min(int(lim), len(trLossX))
    fig, ax1 = plt.subplots()

    # Loss on left axis
    ax1.plot(trLossX[:lim], trLossY[:lim], label='train loss', marker='o')
    ax1.plot(evLossX[:lim], evLossY[:lim], label='eval loss', marker='o')
    ax1.set_xlabel('Epoch [n]')
    ax1.set_ylabel('Loss')
    ax1.set_xlim(0, min(len(trLossY), lim) + 1)
    ax1.set_ylim(0, max(max(trLossY), max(evLossY)) * 1.2)
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    
    # Accuracy on right axis
    ax2 = ax1.twinx()
    ax2.plot(trAccX[:lim], trAccY[:lim], label='train accuracy', marker='x', color="#2ca02c")
    ax2.plot(evAccX[:lim], evAccY[:lim], label='eval accuracy', marker='x', color="#d62728")
    ax2.set_ylabel('Accuracy [%]')
    ax2.set_ylim(0.0, 100.0)  # if accuracy is stored as fractions
    
    # Combined legend
    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(0.65, 0.43))
    
    plt.savefig(join(dir, 'LossAccPlotCombined_Total.pdf'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f'Saved loss plot under "{join(dir, "LossAccPlotCombined_Total.pdf")}".')


def int_GenerateClassDistChart(totClsDist, dir) -> None:
    c = plt.cm.viridis(np.linspace(0.2, 0.85, len(totClsDist.values())))
    y = [x for x, _ in totClsDist.values()]

    plt.figure()
    bars = plt.bar(['KA', 'SB', 'IB', 'U'], y, color=c)
    plt.ylabel("Sample Count [n]")
    plt.xlabel('Regions')
    plt.bar_label(bars, padding=3)
    plt.ylim(0, max(y) * 1.2)
    plt.savefig(join(dir, "ClassDist.pdf"), dpi=300)
    plt.close()

    print(f'Saved class distribution chart under "{join(dir, "ClassDist.pdf")}".')


def int_GenerateClassDropDistChart(totClsDist, dir) -> None:
    c = plt.cm.viridis(np.linspace(0.2, 0.85, len(totClsDist.values())))

    # Maximum samples per class.
    m = [
        11 * 120 * 10,
        (2 * 60 + 9 * 90) * 10,
        11 * 150 * 10,
        11 * 120 * 10 
    ]
    l = [m[i] - x for i, (x, _) in enumerate(totClsDist.values())]

    plt.figure()
    bars = plt.bar(['KA', 'SB', 'IB', 'U'], l, color=c)
    plt.ylabel("Dropped Sample Count [n]")
    plt.xlabel('Regions')
    plt.ylim(0, max(l) * 1.2)
    plt.bar_label(bars, padding=3)
    plt.savefig(join(dir, "ClassDropDist.pdf"), dpi=300)
    plt.close()

    print(f'Saved class drop distribution chart under "{join(dir, "ClassDropDist.pdf")}".')


def int_GenerateConfusionMatrix(yReal, yPred, mode, dir, norm, ep=None, pre='', mer=False) -> None:
    # Generate confusion matrix.
    cnf = confusion_matrix(yReal, yPred, normalize=norm)
    dsp = ConfusionMatrixDisplay(confusion_matrix=cnf, display_labels=[
        'KA',
        'SB',
        'IB', 
        'U'
    ] if not mer else [
        'FB',
        'IB', 
        'U'
    ])
    mdd = 'evaluation' if mode == 'Ev' else ('training' if mode == 'Tr' else '___')
    if ep is None:
        fname = join(dir, f'CnfMtx_{pre}{mode}_Total{"_Norm" if norm else ""}.pdf')
    else:
        fname = join(dir, f'CnfMtx_{pre}{mode}_Ep{ep}{"_Norm" if norm else ""}.pdf')
    dsp.plot().figure_.savefig(fname, dpi=300)
    if ep is not None:
        print(f'Saved{" normalized" if norm else ""} {mdd} confusion matrix for epoch {ep} under "{fname}".')
    else:
        print(f'Saved{" normalized" if norm else ""} {mdd} confusion matrix under "{fname}".')

    # Generate classification report.
    rep = classification_report(yReal, yPred)
    if dir is not None:
        repName = join(dir, f'ClsRep_{pre}{mode}_Ep{ep}.txt')
    else:
        repName = f'ClsRep_{pre}{mode}_Total.txt'
    if not exists(repName):
        with open(repName, 'w') as f:
            f.write(rep)

            if dir is not None:
                print(f'Saved classification report for epoch {ep} under "{repName}".')
            else:
                print(f'Saved classification report under "{repName}".')

    plt.close()


if __name__ == '__main__':
    dir = argv[1]
    lim = argv[2] if len(argv) > 2 else -1
    mer = '-m' in argv
    tog = '-t' in argv

    # Find training statistics file. It is the output from train.py.
    for id in listdir(dir):
        if id.startswith('Ev_Stats_'):
            file = join(dir, id)

            break
    else:
        print(f'error: Could not find a training statistics file in directory "{dir}". Aborting.')

        exit(1)
    n = 0

    # Read the file.
    with open(file, 'r') as f:
        stats = load(f)

    int_GenerateClassDistChart(stats['dataset']['clsDist']['tot'], dir)
    int_GenerateClassDropDistChart(stats['dataset']['clsDist']['tot'], dir)

    if not 'trELossesX' in stats:
        print('warning: No separate train evaluation found. To get them, run the models once on the training set and collect the results.')
    if not tog:
        # (1) Generate loss graph.
        int_GenerateLossGraph(stats.get('trELossesX', []), stats.get('trELossesY', []), stats['evLossesX'], stats['evLossesY'], dir, lim)
        n += 1

        # (2) Generate acc graph.
        int_GenerateAccGraph(stats.get('trEAccX', []), stats.get('trEAccY', []), stats['evAccX'], stats['evAccY'], dir, lim)
        n += 1
    else:
        int_GenerateCombinedLossAndAccuracyGraph(stats, dir, lim)

        n += 1

    # (3) Generate confusion matrix.
    if 'evTrEReal' in stats['cnf']:
        int_GenerateConfusionMatrix(stats['cnf']['evTrEReal'], stats['cnf']['evTrEPred'], 'Tr', dir, None, None, mer=mer)
        int_GenerateConfusionMatrix(stats['cnf']['evTrEReal'], stats['cnf']['evTrEPred'], 'Tr', dir, 'true', None, mer=mer)
    int_GenerateConfusionMatrix(stats['cnf']['evYReal'], stats['cnf']['evYPred'], 'Ev', dir, None, None, mer=mer)
    int_GenerateConfusionMatrix(stats['cnf']['evYReal'], stats['cnf']['evYPred'], 'Ev', dir, 'true', None, mer=mer)
    n += 4

    # (4...) Do (3) for every epoch.
    if not exists(join(dir, 'cnf')):
        makedirs(join(dir, 'cnf'))
    for e, eps in stats['epochs'].items():
        if 'trEYReal' in eps:
                int_GenerateConfusionMatrix(eps['trEYReal'], eps['trEYPred'], 'Tr', join(dir, 'cnf'), None, int(e), mer=mer)
                int_GenerateConfusionMatrix(eps['trEYReal'], eps['trEYPred'], 'Tr', join(dir, 'cnf'), 'true', int(e), mer=mer)
        int_GenerateConfusionMatrix(eps['eYReal'], eps['eYPred'], 'Ev', join(dir, 'cnf'), None, int(e), mer=mer)
        int_GenerateConfusionMatrix(eps['eYReal'], eps['eYPred'], 'Ev', join(dir, 'cnf'), 'true', int(e), mer=mer)

        n += 4

    print(f'Successfully generated {n} graphs. Have fun analyzing them!')
    exit(0)


