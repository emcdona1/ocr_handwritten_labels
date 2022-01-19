import os
import sys
import ast
import pandas as pd
from typing import Union, List
from statistics import multimode
import string
from utilities import data_loader
from imageprocessor import GCVProcessor
import math
from pathlib import Path

WORKFLOW_NAME = 'Transcribe Words'  # from Zooniverse or the classifications CSV file - case-sensitive!
MINIMUM_WORKFLOW_VERSION = '21.31'  # from Zooniverse or the classifications CSV file -
                                    # all classifications this version and higher will be included
RETIREMENT_COUNT = 5  # from Zooniverse within the workflow


def main(zooniverse_classifications_file: Path, folders_of_source_images: List[Path], image_save_folder=None):
    print('Load & clean classification file.')
    zooniverse_classifications = pd.read_csv(zooniverse_classifications_file)
    zooniverse_classifications = clean_raw_zooniverse_file(zooniverse_classifications)
    print('Consolidate file.')
    zooniverse_classifications = consolidate_classification_rows(zooniverse_classifications)
    print('Update file paths.')
    update_full_image_paths(folders_of_source_images, zooniverse_classifications)
    print('Save files.')
    csv_save_location = data_loader.save_dataframe_as_csv('file_resources', 'zooniverse_parsed',
                                                          zooniverse_classifications)
    print('Saved parsed results file to %s.' % csv_save_location)
    if image_save_folder:
        print(f'Saving word images to {image_save_folder}')
        save_images_to_folders(zooniverse_classifications, image_save_folder)


def _parse_zooniverse_subject_text(subject_text):
    image_name = subject_text['Filename']
    id = image_name.replace('wordbox-', '').replace('.jpg', '').replace('label-', '')
    barcode = id.split('-')[0]  # in case the file name includes "-label"
    block = int(id.split('b')[1].split('p')[0])
    paragraph = int(id.split('p')[1].split('w')[0])
    word = int(id.split('w')[1])
    try:
        gcv_identification = subject_text['#GCV_identification']
    except KeyError:
        gcv_identification = None
    result = pd.Series([id, barcode, block, paragraph, word, gcv_identification, image_name],
                       index=['id', 'barcode', 'block', 'paragraph', 'word', 'gcv_identification', 'image_location'])
    return result


def _filter_workflow_versions(raw_zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    filtered_raw_zooniverse = raw_zooniverse_classifications.query(
        f'workflow_name == "{WORKFLOW_NAME}" and workflow_version >= {MINIMUM_WORKFLOW_VERSION}').copy()
    return filtered_raw_zooniverse


def _clean_csv_strings(raw_zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    def clean_zooniverse_csv_strings(txt: str):
        txt = txt.replace('null', 'None')
        txt = ast.literal_eval(txt)
        if type(txt) is dict:  # for subject_data
            txt = [*txt.values()]
            txt = txt[0]
        return txt

    raw_zooniverse_classifications.loc[:, 'annotations'] = \
        raw_zooniverse_classifications['annotations'].apply(clean_zooniverse_csv_strings)
    raw_zooniverse_classifications.loc[:, 'subject_data'] = \
        raw_zooniverse_classifications['subject_data'].apply(lambda s:
                                                             s.replace('image_of_boxed_letter', 'Filename')
                                                             .replace('image_of_boxed_word', 'Filename'))
    raw_zooniverse_classifications.loc[:, 'subject_data'] = \
        raw_zooniverse_classifications['subject_data'].apply(clean_zooniverse_csv_strings)
    return raw_zooniverse_classifications


def _process_annotations_into_columns(filtered_raw_zooniverse, parsed_zooniverse_classifications) -> None:
    """ This method needs to be tailored to your project's workflow(s), which will
    impact the annotations column in your classifications file! """
    parsed_zooniverse_classifications['handwritten'] = filtered_raw_zooniverse['annotations'].apply(
        lambda a: a[0]['value'] == 'handwritten')
    parsed_zooniverse_classifications['human_transcription'] = filtered_raw_zooniverse['annotations'].apply(
        lambda a: '' if len(a) == 1 else a[1]['value'])
    parsed_zooniverse_classifications['unclear'] = parsed_zooniverse_classifications['human_transcription'].apply(
        lambda transcription: '[unclear]' in transcription and '[/unclear]' in transcription)
    parsed_zooniverse_classifications['human_transcription'] = \
        parsed_zooniverse_classifications['human_transcription'].apply(
            lambda transcription: transcription.replace('[unclear]', '').replace('[/unclear]', ''))
    parsed_zooniverse_classifications['seen_count'] = parsed_zooniverse_classifications.groupby('id')[
        'block'].transform(len)
    parsed_zooniverse_classifications['confidence'] = 1.0
    parsed_zooniverse_classifications['status'] = 'In Progress'


def clean_raw_zooniverse_file(raw_zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    raw_zooniverse_classifications = _filter_workflow_versions(raw_zooniverse_classifications)
    filtered_raw_zooniverse = _clean_csv_strings(raw_zooniverse_classifications)

    parsed_zooniverse_classifications = filtered_raw_zooniverse['subject_data'].apply(_parse_zooniverse_subject_text)
    _process_annotations_into_columns(filtered_raw_zooniverse, parsed_zooniverse_classifications)

    bad_data_to_drop = parsed_zooniverse_classifications.query('handwritten == True and ' +
                                                               'unclear == False and ' +
                                                               'human_transcription == ""')
    parsed_zooniverse_classifications = parsed_zooniverse_classifications.drop(index=bad_data_to_drop.index)

    return parsed_zooniverse_classifications


def vote(df: pd.DataFrame, col_name: str) -> (list, int, int):
    """ Returns:
    (1) A list (len >= 1) of the most voted item (can be multiple in the case of a tie).
    (2) The number (int) of votes the previous item received.
    (3) The number (int) of total votes for this word (i.e. the number of volunteers who classified it)."""
    total = df.shape[0]
    voted = multimode(list(df.loc[:, col_name]))
    if type(voted) is not list:
        voted = [voted]
    voted_count = df[df[col_name] == voted[0]].shape[0]
    return voted, voted_count, total


def _vote_on_handwriting(subset, consolidated_row):
    type_vote, _, _ = vote(subset, 'handwritten')
    if len(type_vote) > 1:  # if vote is evenly split, mark it as handwritten
        type_vote = [True]
    consolidated_row.at['handwritten'] = type_vote[0]


def _vote_on_transcription_text(subset, consolidated_row):
    voted, count, total = vote(subset, 'human_transcription')
    consolidated_row.at['confidence'] = count / total
    # These steps remove empty spaces
    voted = [e.strip() for e in voted]
    try:
        voted.remove('')
    except ValueError:
        pass
    voted = list(set(voted))  # todo: this isn't logically consistent -- if there are duplicates now, they should be the
                              # todo: voted text now! Either [dup] or [dup1, dup2, ...]
    if len(voted) == 1:
        voted = voted[0]
    consolidated_row.at['human_transcription'] = voted


def _vote_on_unclear_status(subset, consolidated_row):
    unclear_vote, _, _ = vote(subset, 'unclear')
    if len(unclear_vote) > 1:  # if it's evenly split, mark as NOT unclear
        unclear_vote = [False]
    consolidated_row.at['unclear'] = unclear_vote[0]


def _status_vote(row) -> str:
    status = 'Complete'
    if row.at['confidence'] <= 0.5:
        if row.at['unclear']:
            status = 'Discard - Unclear & Low Confidence'
        else:
            status = 'Expert Required'
    elif type(row.at['human_transcription']) is list:  # Tie for transcription
        status = 'Expert Required'
    elif len(row.at['human_transcription']) == 1 and row.at['human_transcription'] in string.punctuation:
        status = 'Discard - Short & Only Punctuation'
    elif row.at['unclear']:
        status = 'Discard - Unclear'
    elif row.at['status'] == 'Discard - Typewritten':
        status = row.at['status']
    return status


def _drop_subjects_without_enough_views(zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    too_few = zooniverse_classifications[zooniverse_classifications['seen_count'] < math.ceil(RETIREMENT_COUNT / 2)]
    return zooniverse_classifications.drop(index=too_few.index)


def consolidate_classification_rows(zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    zooniverse_classifications = _drop_subjects_without_enough_views(zooniverse_classifications)

    all_unique_ids = set(zooniverse_classifications[zooniverse_classifications['seen_count'] > 1]['id'])
    for image_id in all_unique_ids:
        subset = zooniverse_classifications[zooniverse_classifications['id'] == image_id]
        consolidated_row = subset.loc[subset.index[0], :]
        consolidated_row.at['gcv_identification'] = max([item for item in subset.loc[:, 'gcv_identification'] if item],
                                                        key=len)

        _vote_on_handwriting(subset, consolidated_row)
        if consolidated_row.at['handwritten']:
            _vote_on_transcription_text(subset, consolidated_row)
            _vote_on_unclear_status(subset, consolidated_row)
        else:
            consolidated_row.at['status'] = 'Discard - Typewritten'

        zooniverse_classifications = zooniverse_classifications.drop(index=subset.index)
        zooniverse_classifications = zooniverse_classifications.append(consolidated_row)
    print(f'Consolidated: {zooniverse_classifications.shape}\n')
    print('Adding manual reviews.')
    expert_manual_reviews(zooniverse_classifications)
    zooniverse_classifications['status'] = zooniverse_classifications.apply(_status_vote,axis=1)
    typed = zooniverse_classifications.query('handwritten == False')
    zooniverse_classifications = zooniverse_classifications.drop(index=typed.index)
    return zooniverse_classifications.sort_values(by=['block', 'paragraph', 'word'], ascending=True)


def update_full_image_paths(folders: List[Path], zooniverse_classifications: pd.DataFrame) -> None:
    collector_name = data_loader.load_pickle(Path('file_resources\\collectors_by_barcode.pickle'))
    for idx, row in zooniverse_classifications.iterrows():
        barcode = row['barcode']
        zooniverse_classifications.at[idx, 'collector'] = collector_name[barcode]
        image_path = Path(row['image_location'])
        if not os.path.exists(image_path):  # search in image folders for this one, and update path IF found
            image_filename = image_path.name
            found_image_path = None
            for folder in folders:
                if os.path.exists(Path(folder, image_filename)):
                    found_image_path = Path(folder, image_filename)
            if found_image_path:
                zooniverse_classifications.at[idx, 'image_location'] = found_image_path
            else:
                print(f"Warning: {image_path} doesn't exist in these folders.")


def expert_manual_reviews(df: pd.DataFrame) -> None:
    edits = pd.read_csv(Path('file_resources\\standley_steyermark_manual_review.csv'))
    for idx, row in edits.iterrows():
        id = row['id']
        if id in df['id'].values:
            df.loc[df['id'] == id, row['edit 1']] = row['edit 1 value']
            if pd.notna(row['edit 2']):
                df.loc[df['id'] == id, row['edit 2']] = row['edit 2 value']
                if pd.notna(row['edit 3']):
                    df.loc[df['id'] == id, row['edit 3']] = row['edit 3 value']
    # df.loc[df['id'] == 'C0604088F-b14p1w1', ('human_transcription', 'status')] = (
    #     'T53N', 'Expert Reviewed')  # cut off on end
    # df.loc[df['id'] == 'C0604948F-b15p2w0', ('human_transcription', 'status')] = (
    #     'Fork', 'Expert Reviewed')  # cut off on both sides
    # df.loc[df['id'] == 'C0605417F-b12p0w2', ('human_transcription', 'status')] = (
    #     'var. spec', 'Expert Reviewed')  # cut off on end
    # df.loc[df['id'] == 'C0606902F-b12p1w14', ('human_transcription', 'status')] = (
    #     'Tom', 'Expert Reviewed')  # cut off both sides
    # df.loc[df['id'] == 'C0606902F-b12p1w15', ('human_transcription', 'status')] = (
    #     'Sauk', 'Expert Reviewed')  # cut off both sides
    # df.loc[df['id'] == 'C0607530F-b12p1w1', ('human_transcription', 'status')] = (
    #     'Fork', 'Expert Reviewed')  # cut off on both sides


def save_images_to_folders(zooniverse_classifications: pd.DataFrame, word_image_folder: Path) -> None:
    collectors = (zooniverse_classifications['collector'])
    for collector in collectors:
        collector_image_path = Path(word_image_folder, collector)
        if not os.path.exists(collector_image_path):
            os.makedirs(collector_image_path)
    filtered_zooniverse: pd.DataFrame = zooniverse_classifications \
        .query("handwritten == True and (status == 'Complete' or status == 'Expert Reviewed')")
    word_image_metadata = filtered_zooniverse.copy()
    word_image_metadata = word_image_metadata.rename(columns={'image_location': 'zooniverse_image_location'})
    image_processor = GCVProcessor()
    for idx, row in filtered_zooniverse.iterrows():
        word_filename = f"{row['id']}-word"
        image_processor.load_image_by_barcode(row['barcode'])
        full_size_image_location = image_processor.current_image_location
        word_image = crop_word_image(image_processor, row)

        save_location = data_loader.save_cv2_image(Path(word_image_folder, row['collector']),
                                                   word_filename, word_image, timestamp=False)
        word_image_metadata.at[idx, 'full_size_image_location'] = full_size_image_location
        word_image_metadata.at[idx, 'word_image_location'] = save_location
        zooniverse_classifications.at[idx, 'word_image_location'] = save_location

    data_loader.save_dataframe_as_csv(word_image_folder, 'words_metadata', word_image_metadata, timestamp=False)


def crop_word_image(image_processor, row):
    word_info = [w for w in image_processor.get_list_of_words()
                 if w['b_idx'] == row['block'] and w['p_idx'] == row['paragraph'] and w['w_idx'] == row['word']][0]
    x_min, y_min = list(map(min, *word_info['bounding_box']))
    x_max, y_max = list(map(max, *word_info['bounding_box']))
    x_min = max(0, x_min - 20)
    x_max = min(x_max + 10, image_processor.current_image_width)
    word_image = image_processor.annotator.cropped_copy_of_image(x_min, x_max, y_min, y_max)
    return word_image


if __name__ == '__main__':
    assert len(sys.argv) >= 3, 'Include 3+ arguments: (1) the location of the Zooniverse CSV classifications, ' + \
                               '(2) the folder in which to save images for the neural network, or "None" if' + \
                               'not generating the images, and' + \
                               '(3+) the folder(s) of label images which were used in Zooniverse. '

    zooniverse_results = Path(sys.argv[1])
    assert os.path.isfile(zooniverse_results), f'Invalid 1st argument: {zooniverse_results} is not a file.'

    if sys.argv[2] == 'None':
        words_save_folder = None
    else:
        words_save_folder = Path(sys.argv[2])
        if not os.path.exists(words_save_folder):
            os.makedirs(words_save_folder)

    image_folders = [Path(f) for f in sys.argv[3:]]
    for image_folder in image_folders:
        assert os.path.exists(image_folder), f'Invalid image folder: {image_folder} does not exist.'

    main(zooniverse_results, image_folders, words_save_folder)
