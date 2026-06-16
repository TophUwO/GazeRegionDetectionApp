# Make head pose distribution plot.
import matplotlib.pyplot as plt
import datetime          as dt

from sys                import argv
from estimator          import EstimatePitchYawRoll
from os                 import walk
from numpy              import load
from re                 import match


if __name__ == '__main__':
    reg = -1 if len(argv) < 2 else argv[1]

    # Collect all files that we have to parse.
    i = 1
    img2Proc = []
    for r, d, files in walk(argv[1]):
        for f in files:
            if reg == -1:
                if f.endswith('.jpg'):
                    img2Proc.append(r + '/' + f)

                    i += 1
            #else:
                #if match



    print(f'Collected {len(img2Proc)} files. Processing ...')

    # Get camera calibration results.
    cmtx  = load('ccres/cam.npy')
    ncmtx = load('ccres/ncam.npy')
    dist  = load('ccres/dist.npy')
    roi   = load('ccres/roi.npy')

    # Estimate yaw and pitch for all collected images.
    x = []
    y = []
    for j, f in zip([j for j in range(i)], img2Proc):
        pitch, yaw, _ = EstimatePitchYawRoll(f, cmtx, ncmtx, dist, roi)

        x.append(yaw)
        y.append(pitch)
        print(f'  [{j + 1}/{i}] Processed {f}. p={pitch}, y={yaw}')

    # Generate 2D histogram.
    print('Generating histogram.')
    plt.hist2d(x, y, bins=50, cmap='viridis')
    plt.grid(True, color='white', linestyle='--', linewidth=0.5, alpha=0.5)

    plt.xlabel('Yaw [deg]')
    plt.ylabel('Pitch [deg]')
    plt.colorbar(label='Count')
    plt.savefig(f'GazeReg_HeadPoseDist_{dt.datetime.now().strftime("%Y-%m-%d")}.pdf', dpi=300, bbox_inches='tight')


    