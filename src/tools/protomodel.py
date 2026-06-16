from torch import nn, cat, abs

class GazeRegEyeModel1(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=64, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.reg = nn.Sequential(
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 4)
        )
            
    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)
        
        l = l.flatten(1)
        r = r.flatten(1)
        
        x = cat([l, r], dim=1)
        x = self.reg(x) 
        return x


class GazeRegEyeModel2(nn.Module):
    def __init__(self):
        super().__init__()

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
            nn.AdaptiveAvgPool2d((4, 4)) 
        )
        
        self.reg = nn.Sequential(
            nn.Linear(4096, 256),
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Linear(256, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel3(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # nn.Dropout2d(0.1),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((2, 2))
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(1024, 4),
            # nn.BatchNorm1d(256),
            # nn.ReLU(inplace=True),
            # nn.Dropout(p=0.5),
            # nn.Linear(256, 4)
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel4(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            # nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            #nn.BatchNorm2d(128),
            #nn.ReLU(inplace=True),
            # nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((4, 4)) 
        )
        
        self.reg = nn.Sequential(
            nn.Linear(2048, 4),
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel5(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            # nn.Dropout2d(0.1),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            # nn.Dropout2d(0.2),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((6, 6))
        )

        self.reg = nn.Sequential(
            #nn.Linear(4608 + 2304, 512),
            # nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(4608 + 2304, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r, abs(l - r)], dim=1)
        return self.reg(x)


class GazeRegEyeModel6(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.1),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.2),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((2, 2)), 
            nn.Dropout2d(p=0.3)
        )
        
        self.reg = nn.Sequential(
            nn.Linear(1024, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(256, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        return self.reg(x)
    

class GazeRegEyeModel7(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            # Input: 120 x 72
            nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.15),

            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.2),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.25),
            
            nn.AdaptiveAvgPool2d((5, 3))
        )
        
        self.reg = nn.Sequential(
            nn.Linear(3840, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            
            nn.Linear(512, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            
            nn.Linear(128, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        return self.reg(x)
    

class GazeRegEyeModel8(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.15),

            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.2),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(p=0.25),
            
            nn.AdaptiveAvgPool2d((5, 3))
        )
        
        self.reg = nn.Sequential(
            nn.Linear(3840, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.5),
            
            nn.Linear(512, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            
            nn.Linear(128, 4)
        )

class GazeRegEyeModel10(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=8, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(8),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=8, out_channels=16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout2d(0.1), # Next

            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((6, 6)) # 2, 2 => 59.38, 7, 4 => 63.17, 11,7 -> 48%
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(6 * 6 * 2 * 32, 4),
            # nn.BatchNorm1d(256),
            # nn.ReLU(inplace=True),
            # nn.Dropout(p=0.5),
            # nn.Linear(256, 4)
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 4)
        )

    def forward(self, left, right):
        l = self.cnn(left)
        r = self.cnn(right)

        l = l.flatten(1)
        r = r.flatten(1)

        x = cat([l, r], dim=1)
        x = self.reg(x)

        return x









class GazeRegEyeModel100(nn.Module):
    def __init__(self):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(256 + 64, 4),
            # nn.BatchNorm1d(256),
            # nn.ReLU(inplace=True),
            # nn.Dropout(p=0.5),
            # nn.Linear(256, 4)
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

# 62.7151%
class GazeRegEyeModel101(nn.Module):
    def __init__(self):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 16),
            nn.BatchNorm1d(16),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(256 + 16, 4),
            # nn.BatchNorm1d(256),
            # nn.ReLU(inplace=True),
            # nn.Dropout(p=0.5),
            # nn.Linear(256, 4)
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x

# 65.2887% no-A
# 59.667%     A
class GazeRegEyeModel102(nn.Module):
    def __init__(self):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(256 + 128, 4),
            # nn.BatchNorm1d(256),
            # nn.ReLU(inplace=True),
            # nn.Dropout(p=0.5),
            # nn.Linear(256, 4)
            # nn.BatchNorm1d(256),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 64),
            # nn.BatchNorm1d(64),
            #nn.ReLU(inplace=True),
            #nn.Linear(256, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

# Epoch 20:
#  Training:   L=0.9050, A=66.9512%
#  Evaluation: L=0.9967, A=67.4924%
#
# Cracked 75% with 30 epochs.
class GazeRegEyeModel103(nn.Module):
    def __init__(self):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.4), # was 0.4
            nn.Linear(128 + 128 + 128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4), # was 0.4
            nn.Linear(64, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel104(nn.Module):
    def __init__(self):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.3), # was 0.4
            nn.Linear(128 + 128 + 128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3), # was 0.4
            nn.Linear(64, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel105_Shit(nn.Module):
    def __init__(self):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.4), # was 0.4
            nn.Linear(128 + 128 + 256, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4), # was 0.4
            nn.Linear(64, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel106(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=2),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Dropout(p=0.4), # was 0.4
            nn.Linear(128 * 2 + 128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4), # was 0.4
            nn.Linear(64, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    

class GazeRegEyeModel107(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
        self.reg = nn.Sequential(
            nn.Linear(128 * 2 + 128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(64, 4)
        )

    def forward(self, left, right, lm, pose):
        l  = self.cnn(left).flatten(1)
        r  = self.cnn(right).flatten(1)
        lp = self.lmp(cat([lm, pose], dim=1))
        
        x = cat([l, r, lp], dim=1)
        x = self.reg(x)

        return x
    








class GazeRegEyeModel200(nn.Module):
    def __init__(self, merged):
        super().__init__()

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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
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
    

class GazeRegEyeModel201(nn.Module):
    def __init__(self, merged):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=11, stride=1, padding=5),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=7, stride=1, padding=3),
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

        self.lmp = nn.Sequential(
            nn.Linear(68 * 2 + 3, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True)
        )
        
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