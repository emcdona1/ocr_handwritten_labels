import sys
import os
from pathlib import Path
import pandas as pd
from typing import List


def main(image_folders: List[dict]):
    input_file = list()
    for f in image_folders:
        test_train = f['test_train']
        label = f['label']
        images = [Path(i) for i in os.listdir(f['folder_path'])]
        images = [i for i in images if i.suffix in ['.jpg', '.jpeg', '.gif', '.png', '.bmp', '.ico']]
        for i in images:
            input_file.append([test_train, f'gs://{bucket}/{i}', label])
    input_file = pd.DataFrame(input_file, columns=['test_train', 'path', 'label'])
    input_file.to_csv('foo-location.csv')  # todo


if __name__ == '__main__':
    assert len(sys.argv) >= 4, 'Specify at least 3 arguments: (1) mode - "c" for categorial or "h" for handwriting,\n' + \
        '(2) Google Cloud bucket name to use,\n (3) 1 folder of image folders OR multiple (2+) image folders.'
    mode = (sys.argv[1]).lower()
    assert mode in ['c', 'h'], 'Mode most be "c" for categorial data or "h" for handwriting images.'
    bucket = sys.argv[2]  # 'demo_bucket_name'

    if mode.lower() == 'c':
        folder = sys.argv[3] if len(sys.argv) == 4 else sys.argv[3:]
        folder = Path('C:\\Users\\betht\\Documents\\Field Museum\\image_sets\\6_frullania_aug_nov_jan')  # todo: remove
        if not type(folder) is list:
            folder = [Path(folder, f) for f in os.listdir(folder)]
            folder = [f for f in folder if os.path.isdir(f)]

        folders = list()
        for f in folder:
            label = input(f'Annotation label for folder "{f.name}": ')
            test_train = input(f'Is this a "test" or "train" image set?: ')
            folders.append({'name': f.name, 'folder_path': f, 'label': label, 'test_train': test_train})
        main(folders)
    elif mode.lower() == 'h':
        print('To be implemented.')
    else:
        print('Invalid mode.')

