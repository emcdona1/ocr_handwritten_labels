import os
import sys
from pathlib import Path
import pandas as pd
from typing import List


def main(metadata_path: Path, image_folders: List[Path], folder_labels: List[str]):
    metadata = pd.read_csv(metadata_path)
    images = list()
    for folder in image_folders:
        new_l = os.listdir(folder)
        new_l = [a for a in new_l if Path(a).suffix == '.jpg']
        images.append(new_l)
    image_words = [''] * len(images)
    for idx, folder in enumerate(images):
        for image in folder:
            id = image.replace('-word.jpg', '')
            row = metadata[metadata['id'] == id]
            transcription = row['human_transcription'].values[0]
            image_words[idx] += str(transcription)
    results = pd.DataFrame({'collector': folder_labels})
    results_case_insensitive = pd.DataFrame({'collector': folder_labels})
    dict_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\' !"#&()*+,-./0123456789:;?[]'
    for c in dict_chars:
        results[c] = 0
        results_case_insensitive[c.lower()] = 0
    for idx, cs in enumerate(image_words):
        for c in cs:
            results.loc[idx, c] += 1
            results_case_insensitive.loc[idx, c.lower()] += 1
    results.to_csv(Path('C:\\Users\\betht\\Downloads\\nn_images_10k\\letter_analysis2.csv'))
    results_case_insensitive.to_csv(Path('C:\\Users\\betht\\Downloads\\nn_images_10k\\letter_analysis_lowercase.csv'))


if __name__ == '__main__':
    assert len(sys.argv) >= 3, '2+ arguments are required: (1) CSV file location for a Zooniverse metadata file, ' + \
        '(2+) One or more image folders.'
    m_path = Path(sys.argv[1])
    assert os.path.exists(m_path), f'Metadata file {m_path} not found.'
    assert m_path.suffix == '.csv', f'Metadata file {m_path} must be in CSV format.'
    # m_path = Path('C:\\Users\\betht\\Downloads\\nn_images_10k\\words_metadata.csv')
    image_fs = [Path(f) for f in sys.argv[2:]]
    for folder in image_fs:
        assert os.path.isdir(folder), f'Image folder {folder} not found.'
    # image_fs = [
    #     Path('C:\\Users\\betht\\Downloads\\nn_images_10k\\Steyermark'),
    #     Path('C:\\Users\\betht\\Downloads\\nn_images_10k\\Standley')
    # ]
    labels = [i.name for i in image_fs]
    main(m_path, image_fs, labels)
