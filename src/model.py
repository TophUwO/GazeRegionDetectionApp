from torch import nn


class GazeRegEyeModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.eyeModel = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        x = self.eyeModel(x)
        x = x.view(x.size(0), -1)

        return x


class GazeRegLandmarkModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.lmModel = nn.Sequential(
            nn.Linear(68, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        x = self.lmModel(x)

        return x
    

class GazeRegModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.eyeModel = GazeRegEyeModel()
        self.lmModel  = GazeRegLandmarkModel()

    def forward(self, x):
        x = self.eyeModel(x)
        # TODO: Other things.
        
        return x


