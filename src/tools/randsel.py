from sys     import argv
from os.path import exists, join
from os      import makedirs, walk
from random  import choices, seed
from shutil  import copyfile, rmtree
from time    import time_ns
from re      import match


if __name__ == '__main__':
    seed(time_ns())
    src = argv[1]
    dst = argv[2]
    pat = argv[3]
    n   = int(argv[4])
    cl  = '-c' in argv or '--clear' in argv

    # Get all files.
    files = []
    for r, d, f in walk(src):
        for fi in f:
            if match(pat, fi):
                files.append((join(r, fi), fi))

    # Prepare destination dir.
    if not exists(dst):
        makedirs(dst)
    elif cl:
        rmtree(dst)

        makedirs(dst)
    # Select n random ones and copy them to the destination dir.
    for s, f in choices(files, k=n):
        copyfile(s, join(dst, f))

    exit(0)
