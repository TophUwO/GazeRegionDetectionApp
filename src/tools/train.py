# This file is based on
#   https://docs.pytorch.org/tutorials/beginner/data_loading_tutorial.html
import numpy as np
import torch as pytorch

from os.path          import join
from json             import load
from torch            import tensor, float32, long, device, nn, softmax
from torch.optim      import Adam
from torch.cuda       import is_available
from torch.utils.data import Dataset, DataLoader
from sys              import argv
from tqdm             import tqdm
from random           import sample

from model            import GazeRegEyeModel


class GazeRegDataset(Dataset):
    def __init__(self, cfg, dir, split=(1, 0)):
        # (1) Load dataset listing file.
        try:
            with open(cfg, 'r') as file:
                self._config = load(file)
        except:
            print(f'Could not read dataset listing file "{cfg}". Aborting.')

            return
        self._nSessions = self._config['nsess']
        self._dir       = dir

        # (2) Get training set.
        sessions  = list(self._config['sessions'].keys())
        trainSess = sessions[0:int(split[0]*self._nSessions)]
        self._trainData = []
        for s in trainSess:
            v = self._config['sessions'][s]

            self._trainData.extend(v)

        # self._trainData = sample(self._trainData, 1000)

        print(f'Training set: {trainSess}/{self._nSessions}, {len(self._trainData)} items.')


    def __len__(self):
        return len(self._trainData)


    def __getitem__(self, idx):
        ln, rn, lbl = self._trainData[idx]

        l = tensor(np.load(join(self._dir, ln)), dtype=float32).unsqueeze(0) / 255
        r = tensor(np.load(join(self._dir, rn)), dtype=float32).unsqueeze(0) / 255
        y = tensor(lbl, dtype=long)
        # print(l.min(), l.max(), l.mean(), y)

        # print(f'{ln}, {rn}, {lbl}')
        return l, r, y
    

if __name__ == '__main__':
    cfg  = argv[1]
    dir  = argv[2]
    save = '-s' in argv or '--save' in argv

    epochs = 10
    batch  = 32
    crit   = nn.CrossEntropyLoss()

    ds  = GazeRegDataset(cfg, dir)
    ld  = DataLoader(ds, batch_size=batch, shuffle=True, num_workers=0)
    dev = device('cuda' if is_available() else 'cpu')
    mdl = GazeRegEyeModel().to(dev)
    opt = Adam(mdl.parameters(), lr=1e-3)

    for e in range(epochs):
        mdl.train()
        loss = 0.0

        t = tqdm(ld, desc=f"Epoch {e+1}/{epochs}")
        for l, r, y in t:
            l = l.to(dev)
            r = r.to(dev)
            y = y.to(dev)

            opt.zero_grad()

            res = mdl(l, r)
            # print(softmax(res, dim=1)[:5])
            # print("logits mean/std:", res.mean().item(), res.std().item())
            currLoss = crit(res, y)
            # print("batch loss example:", currLoss.item())

            currLoss.backward()
            opt.step()
            loss += currLoss.item()
            t.set_postfix(loss=currLoss.item())

        avgLoss = loss / len(ld)
        print(f"Epoch {e+1}: avg loss = {avgLoss:.4f}")

    print("FINAL avg loss:", avgLoss)
    print("RAW accumulated loss:", loss)

    print('Finished training.')
    if save:
        pytorch.save(mdl.state_dict(), 'model1.pth')

        print('Saved model under "model1.pth".')

    exit(0)


