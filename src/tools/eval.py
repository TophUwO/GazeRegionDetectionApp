from sys              import argv
from tqdm             import tqdm
from torch.utils.data import DataLoader
from torch            import device, argmax, no_grad, load
from torch.cuda       import is_available

from train     import GazeRegDataset
from model     import GazeRegEyeModel


if __name__ == '__main__':
    mdlfile = argv[1]
    cfg     = argv[2]
    data    = argv[3]

    ds  = GazeRegDataset(cfg, data)
    dl  = DataLoader(ds, batch_size=32)
    dev = device('cuda' if is_available() else 'cpu')
    mdl = GazeRegEyeModel().to(dev)
    mdl.load_state_dict(load(mdlfile, map_location=dev))
    mdl.eval()


    correct, total = 0, 0
    with no_grad():
        pbar = tqdm(dl, desc="Evaluating")

        for l, r, y in pbar:
            l, r, y = l.to(dev), r.to(dev), y.to(dev)

            yPred = mdl(l, r)
            yPred = argmax(yPred, dim=1)
            #print(f'Got {yPred} and is {y}')

            correct += (yPred == y).sum().item()
            total += y.size(0)

            acc = correct / total

            # live tqdm display
            pbar.set_postfix(acc=f'{acc:.4f}', correct=correct, total=total)


        