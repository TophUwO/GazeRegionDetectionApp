import matplotlib.pyplot as plt

from sys                import argv
from estimator          import EstimatePitchYaw
from os                 import walk
from concurrent.futures import ThreadPoolExecutor, wait



data = []

def ProcessImage(img) -> None:
    pitch, yaw = EstimatePitchYaw(img)

    data.append((pitch, yaw))
    print(f'   Processed image: {img}; p={pitch}. y={yaw}')


if __name__ == '__main__':
    pool = ThreadPoolExecutor(1)

    i = 1
    img2Proc = []
    try:
        for r, d, files in walk(argv[1]):
            for f in files:
                if f.endswith('.jpg'):
                    #if i == 9000:
                    #    raise
                
                    img2Proc.append(r + '/' + f)
                    i += 1
    except:
        pass

    print(f'Collected {len(img2Proc)} files. Processing ...')

    x = []
    y = []
    for j, f in zip([j for j in range(i)], img2Proc):
        pitch, yaw = EstimatePitchYaw(f)

        x.append(yaw)
        y.append(pitch)
        print(f'  [{j + 1}/{i}] Processed {f}. p={pitch}, y={yaw}')

    # Generate 2D histogram.
    print('Generating histogram.')
    plt.hist2d(x, y, bins=50, cmap='viridis')

    plt.xlabel("Yaw [deg]")
    plt.ylabel("Pitch [deg]")
    plt.colorbar(label="Count")
    plt.savefig("output.png", dpi=300, bbox_inches="tight")


    