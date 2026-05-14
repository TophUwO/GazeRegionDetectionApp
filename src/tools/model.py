from torch import nn, cat


class GazeRegEyeModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.reg = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 4)
        )

    def forward(self, left, right):
        # (1) Get features for both eyes.
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)     # (B, 256)
        r = r.flatten(1)     # (B, 256)

        # Concatenate and put through FC-layers.
        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x


