""" from torch import nn, cat


class GazeRegEyeModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=128, kernel_size=7, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=5, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=256, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.reg = nn.Sequential(
            nn.Linear(128, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 4)
        )

    def forward(self, left, right):
        # (1) Get features for both eyes.
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        # Concatenate and put through FC-layers.
        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x


 """
from torch import nn, cat

class GazeRegEyeModel(nn.Module):
    def __init__(self):
        super().__init__()

        # Added BatchNorm2d and corrected padding to preserve spatial data
        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=64, kernel_size=7, stride=1, padding=3), # padding=3 for 7x7
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=5, stride=1, padding=2), # padding=2 for 5x5
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Increased final channels to 256 so pooling doesn't destroy features
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1), # padding=1 for 3x3
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((1, 1)) 
        )
        
        # 256 channels * 2 eyes = 512 input features
        self.reg = nn.Sequential(
            nn.Linear(512, 256),
            nn.BatchNorm1d(256), # Added normalization for dense layers
            nn.ReLU(inplace=True),
            nn.Linear(256, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 4) # Raw logits for CrossEntropyLoss
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x