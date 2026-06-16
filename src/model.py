# 3- and 4-KM model architecture.
from torch import nn, cat


class GazeRegModel(nn.Module):
    def __init__(self, merged):
        super().__init__()

        # CNN-based feature extractor used for both eyes.
        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.AdaptiveAvgPool2d((1, 1))
        )

        # MLP for landmarks and 3D-attitude angles.
        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
        # Final classifier.
        self.reg = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(128*2 + 128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4),
            nn.Linear(64, 4 if not merged else 3)
        )


    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

