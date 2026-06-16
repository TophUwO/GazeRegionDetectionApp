# Calculate image differences.
import cv2
import numpy as np

from sys     import argv
from os.path import join, basename
from os      import listdir

import matplotlib.pyplot as plt


def int_CalcDiff(im1, im2, col) -> any:
    im1 = cv2.imread(im1, 0)
    im2 = cv2.imread(im2, 0)

    im3 = cv2.absdiff(im1, im2)
    if col:
        im3 = cv2.applyColorMap(im3, cv2.COLORMAP_INFERNO)
    return im3


# BEGIN of ChatGPT 5.5-generated code.
# Thanks for helping me out here.
def int_MakeColorBar(path):
    fig, ax = plt.subplots()

    grad = np.linspace(0.0, 1.0, 600).reshape(600, 1)
    im   = ax.imshow(grad, cmap='inferno', aspect='auto', vmin=0, vmax=1)

    plt.colorbar(im, ax=ax)
    ax.set_axis_off()

    plt.savefig(path, bbox_inches='tight')
    plt.close(fig)
# END of ChatGPT 5.5-gemerated code.


if __name__ == '__main__':
    src = argv[1]
    ref = argv[2]
    col = '-c' in argv
    
    for f in sorted(listdir(src)):
        if f.endswith('.jpg') and f != basename(ref):
            diff = int_CalcDiff(ref, join(src, f), col)

            cv2.imwrite(join(src, f'{f}_ref_diff{"_cc" if col else ""}.png'), diff)
    int_MakeColorBar(join(src, 'ColorBar.svg'))

    exit(0)


