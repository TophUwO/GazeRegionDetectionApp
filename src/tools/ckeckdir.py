from os import listdir, path


if __name__ == '__main__':
    for file in listdir('.'):
        if file.endswith('.jpg') and not path.exists(file.replace('img', 'lbl'.replace('.jpg', '.json'))):
            print(f'error: Image ""{file} has no corresponding label.')


