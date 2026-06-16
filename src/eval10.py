# Evaluate ten at once.
import numpy as np

from sys              import argv
from tqdm             import tqdm
from torch            import device, argmax, no_grad, load, tensor, float32, long
from torch.cuda       import is_available
from json             import dumps
from datetime         import datetime
from os.path          import join, exists
from collections      import Counter

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
from tools.train     import GazeRegDataset
from model           import GazeRegModel


def int_SegmentIntoN(evalData, n) -> list:
    """groups training samples into groups of n samples"""

    res = []

    currIdx = 0
    while currIdx < len(evalData):
        group    = []
        lastLbl  = evalData[currIdx][-1]
        lastSess = evalData[currIdx][0].split('_')[1]
        for i in range(n):
            if currIdx + i >= len(evalData):
                break
            currSample = evalData[currIdx + i]
            if (currSample[-1] != lastLbl or lastSess != currSample[0].split('_')[1]):
                break

            group.append(currSample)
        currIdx += len(group)
        res.append(group)

    return res


def int_PrepareSample(sample, dir, dev) -> tuple:
    ln, rn, lmn, pn, lbl = sample

    l  = (tensor(np.load(join(dir, ln)),  dtype=float32).unsqueeze(0).unsqueeze(0) / 255.0).to(dev)
    r  = (tensor(np.load(join(dir, rn)),  dtype=float32).unsqueeze(0).unsqueeze(0) / 255.0).to(dev)
    lm = (tensor(np.load(join(dir, lmn)), dtype=float32).unsqueeze(0)).to(dev)
    p  = (tensor(np.load(join(dir, pn)),  dtype=float32).unsqueeze(0)).to(dev)
    y  = (tensor(lbl, dtype=long)).to(dev)
    
    return l, r, lm, p, y


if __name__ == '__main__':
    # (1) Prepare evaluation.
    mdlfile = argv[1] # model file to load for evaluation
    cfg     = argv[2] # listing
    data    = argv[3] # data directory containing the preprocessed samples
    confmtx = '-c' in argv or '--confusion' in argv # whether or not to generate cnfmtx
    rep     = '-r' in argv                          # whether or not to generate classification report

    ds  = GazeRegDataset(cfg, data, True, (0.8, 0.2), True, evalSessions=['317f58', '566cb4', 'dfa842'])
    dev = device('cuda' if is_available() else 'cpu')
    mdl = GazeRegModel(False).to(dev)
    mdl.load_state_dict(load(mdlfile, map_location=dev, weights_only=True))
    mdl.eval()

    # (2) Evaluate.
    print(f'Evaluating over 10 samples.')
    correct, total = 0, 0
    if confmtx:
        y_real = []
        y_pred = []
    with no_grad():
        pbar = tqdm(int_SegmentIntoN(ds.getRawEvaluationSampleList(), 10), desc="Evaluating")

        for i in pbar:
            yPredVec = []
            yRealVec = []
            for j in i:
                left, right, lm, pose, y = int_PrepareSample(j, data, dev)

                yPredVec.append(argmax(mdl(left, right, lm, pose), dim=1).item())

            predY = Counter(yPredVec).most_common()[0][0]
            realY = y.item()
            
            correct += predY == realY
            total   += 1

            acc = correct / total
            if confmtx:
                y_real.append(predY)
                y_pred.append(realY)
            pbar.set_postfix(acc=f'{acc:.4f}', correct=correct, total=total)

    dt = datetime.now().strftime("%Y-%m-%d")
    # (3) If desired, generate confusion matrix and classification report.
    if confmtx:
        fname = f'ConfMtx_Model200_Eval10_{dt}.pdf'
        mtx   = confusion_matrix(y_real, y_pred, labels=[0, 1, 2, 3], normalize='true')

        disp = ConfusionMatrixDisplay(confusion_matrix=mtx)
        disp.plot().figure_.savefig(fname, dpi=300)

        print(f'Confusion matrix has been saved under "{fname}".')
    if rep:
        # Generate classification report.
        rep = classification_report(y_real, y_pred)
        with open(f'ClsRep_Model200_Eval10_{dt}.txt', 'w') as f:
            f.write(rep)

            print(f'Saved classification report under "{f.name}".')

    exit(0)