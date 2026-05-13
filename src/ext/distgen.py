import matplotlib.pyplot as plt
import datetime          as dt

from sys                import argv
from estimator          import EstimatePitchYaw
from os                 import walk


if __name__ == '__main__':
    # Collect all files that we have to parse.
    i = 1
    img2Proc = []
    for r, d, files in walk(argv[1]):
        for f in files:
            if f.endswith('.jpg'):
                img2Proc.append(r + '/' + f)

                i += 1

    print(f'Collected {len(img2Proc)} files. Processing ...')

    # Estimate yaw and pitch for all collected images.
    x = []
    y = []
    for j, f in zip([j for j in range(i)], img2Proc):
        pitch, yaw = EstimatePitchYaw(f)

        x.append(yaw)
        y.append(pitch)
        print(f'  [{j + 1}/{i}] Processed {f}. p={pitch}, y={yaw}')

    # Generate 2D histogram.
    print('Generating histogram.')
    plt.hist2d(x, y, bins=70, cmap='magma')

    plt.xlabel('Yaw [deg]')
    plt.ylabel('Pitch [deg]')
    plt.colorbar(label='Count')
    plt.savefig(f'GazeReg_HeadPoseDist_{dt.datetime.now().strftime("%Y-%m-%d")}.png', dpi=300, bbox_inches='tight')


    