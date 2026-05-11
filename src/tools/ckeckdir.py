from sys import argv
from os  import listdir, path


if __name__ == '__main__':
    dir = argv[1]

    for file in listdir(dir):
        if file.endswith('.jpg') and not path.exists(file.replace('img', 'lbl'.replace('.jpg', '.json'))):
            print(f'error: Image ""{file} has no corresponding label.')


