# Eval as normal.
from sys              import argv
from tqdm             import tqdm
from torch.utils.data import DataLoader
from torch            import device, argmax, no_grad, load
from torch.cuda       import is_available
from json             import dumps
from datetime         import datetime

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from tools.train     import GazeRegDataset
from model           import *


if __name__ == '__main__':
    # (1) Prepare evaluation.
    mdlfile = argv[1]
    cfg     = argv[2]
    data    = argv[3]
    id      = argv[4]
    istr    = '-t' in argv or '--trainds'   in argv
    confmtx = '-c' in argv or '--confusion' in argv
    jsres   = '-j' in argv or '--jsonres'   in argv

    __i, __t = 100, GazeRegModel
    new = __i >= 100

    ds  = GazeRegDataset(cfg, data, True, (0.8, 0.2), eval=True)
    dl  = DataLoader(ds, batch_size=32)
    dev = device('cuda' if is_available() else 'cpu')
    mdl = __t(merged=False).to(dev)
    mdl.load_state_dict(load(mdlfile, map_location=dev))
    mdl.eval()

    # (2) Evaluate.
    print(f'Evaluating on {"training" if istr else "evaluation"} dataset.')
    correct, total = 0, 0
    if jsres:
        res = { 'results': [] }
    if confmtx:
        y_real = []
        y_pred = []
    with no_grad():
        pbar = tqdm(dl, desc="Evaluating")

        for i in pbar:
            if new:
                l, r, lmn, pn, y = i

                lmn, pn = lmn.to(dev), pn.to(dev)
            else:
                l, r, y = i
            l, r, y = l.to(dev), r.to(dev), y.to(dev)

            if new:
                yPred = mdl(l, r, lmn, pn)
            else:
                yPred = mdl(l, r)
            yPred = argmax(yPred, dim=1)

            correct += (yPred == y).sum().item()
            total += y.size(0)

            acc = correct / total
            for yr, yp in zip(y, yPred):
                if jsres:
                    res['results'].append({'correct': (yp == yr).item(), 'y': yr.item(), 'y_pred': yp.item() })
                if confmtx:
                    y_real.append(yr.item())
                    y_pred.append(yp.item())
            pbar.set_postfix(acc=f'{acc:.4f}', correct=correct, total=total)

    # (3) If desired, print results as JSON.
    dt = datetime.now().strftime("%Y-%m-%d")
    if jsres:
        fname = f'Eval_JsRes_{"Tr" if istr else "Ev"}_{"N" if new else ""}{__i}_{dt}.json'
        with open(fname, 'w') as f:
            f.write(dumps(res, indent=4))

            print(f'Evaluation results have been saved to "{fname}".')

    # (4) If desired, generate confusion matrix.
    if confmtx:
        fname = f'Eval_ConfMtx_{"Tr" if istr else "Ev"}_{"N" if new else ""}{__i}_{dt}.png'
        mtx   = confusion_matrix(y_real, y_pred, labels=[0, 1, 2, 3], normalize='true')

        disp = ConfusionMatrixDisplay(confusion_matrix=mtx)
        disp.plot().figure_.savefig(fname, dpi=300)

        print(f'Confusion matrix has been saved under "{fname}".')

    exit(0)


        