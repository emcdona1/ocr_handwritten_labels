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

sys.path.append('')  # to run __main__
WORKFLOW_NAME = 'Transcribe Words'  # from Zooniverse / the classifications CSV file - case-sensitive!
MINIMUM_WORKFLOW_VERSION = '21.31'  # from Zooniverse - all classifications from versions >= are included
RETIREMENT_COUNT = 5  # from Zooniverse within the workflow


def main(zooniverse_classifications_file: Path, folders_of_source_images: List[Path],
         image_save_folder=None):
    print('Load raw file.')
    zooniverse_classifications = pd.read_csv(zooniverse_classifications_file)
    print('Clean file.')
    zooniverse_classifications = clean_raw_zooniverse_file(zooniverse_classifications)
    print('Consolidate file.')
    zooniverse_classifications = consolidate_classification_rows(zooniverse_classifications)
    print('Update file paths.')
    update_full_image_paths(folders_of_source_images, zooniverse_classifications)
    print('Manual edits.')
    expert_manual_review_steyermark(zooniverse_classifications)
    expert_manual_review_standley(zooniverse_classifications)
    csv_save_location = data_loader.save_dataframe_as_csv('C:\\Users\\betht\\Documents\\Field Museum\\' + \
                                                          'ocr_handwritten_labels\\file_resources', 'zooniverse_parsed',
                                                          zooniverse_classifications)
    print('Saved to %s.' % csv_save_location)
    # compare_gcv_to_human(zooniverse_classifications)

    # if image_save_folder:
    #     print('Saving images.')
    #     destination_folder: Path = image_save_folder
    #     save_images_to_folders(zooniverse_classifications, destination_folder)


def _parse_zooniverse_subject_text(subject_text):
    try:
        image_name = subject_text['Filename']
    except KeyError:
        image_name = subject_text['image_of_boxed_letter']
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


def _text_cleaning(raw_zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    filtered_raw_zooniverse = raw_zooniverse_classifications.query(
        f'workflow_name == "{WORKFLOW_NAME}" and workflow_version >= {MINIMUM_WORKFLOW_VERSION}').copy()

    def clean_zooniverse_csv_text_values(txt: str):
        txt = txt.replace('null', 'None')
        txt = ast.literal_eval(txt)
        if type(txt) is dict:  # for subject_data
            txt = [*txt.values()]
            txt = txt[0]
        return txt

    filtered_raw_zooniverse.loc[:, 'annotations'] = \
        filtered_raw_zooniverse['annotations'].apply(clean_zooniverse_csv_text_values)
    filtered_raw_zooniverse.loc[:, 'subject_data'] = \
        filtered_raw_zooniverse['subject_data'].apply(clean_zooniverse_csv_text_values)
    return filtered_raw_zooniverse


def _process_annotations_into_columns(filtered_raw_zooniverse, parsed_zooniverse_classifications) -> None:
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
    filtered_raw_zooniverse = _text_cleaning(raw_zooniverse_classifications)

    parsed_zooniverse_classifications = filtered_raw_zooniverse['subject_data'].apply(_parse_zooniverse_subject_text)
    _process_annotations_into_columns(filtered_raw_zooniverse, parsed_zooniverse_classifications)

    bad_data_to_drop = parsed_zooniverse_classifications.query('handwritten == True and ' +
                                                               'unclear == False and ' +
                                                               'human_transcription == ""')
    parsed_zooniverse_classifications = parsed_zooniverse_classifications.drop(index=bad_data_to_drop.index)

    return parsed_zooniverse_classifications


def vote(df: pd.DataFrame, col_name: str) -> (Union[list, str], int, int):
    total = df.shape[0]
    voted = multimode(list(df.loc[:, col_name]))
    voted_count = df[df[col_name] == voted[0]].shape[0]
    if len(voted) == 1:  # single mode value
        voted = voted[0]
    return voted, voted_count, total


def _handwritten_vote(new_row, subset):
    type_vote, _, _ = vote(subset, 'handwritten')
    if type(type_vote) is list and len(type_vote) > 1:  # if it's evenly split, mark as handwritten
        type_vote = 'handwritten'
    new_row.at['handwritten'] = type_vote


def _transcription_vote(new_row, subset):
    voted, count, total = vote(subset, 'human_transcription')
    new_row.at['confidence'] = count / total
    if type(voted) is list:
        voted = [e.strip() for e in voted]
        try:
            voted.remove('')
        except ValueError:
            pass
        voted = list(set(voted))  # todo: just flagging to make sure this doesn't cause any problems
    if len(voted) == 1:
        voted = voted[0]
    new_row.at['human_transcription'] = voted


def _unclear_vote(new_row, subset):
    unclear_vote, _, _ = vote(subset, 'unclear')
    if type(unclear_vote) is list and len(unclear_vote) > 1:  # if it's evenly split, mark as NOT unclear
        unclear_vote = False
    new_row.at['unclear'] = unclear_vote


def _status_vote(row) -> str:
    status = 'Complete'
    if row.at['confidence'] <= 0.5:  # todo: doesn't account for "complete" if you're downloading a incomplete dataset
        status = 'Expert Required'
    elif type(row.at['human_transcription']) is str and \
            len(row.at['human_transcription']) == 1 and \
            row.at['human_transcription'] in string.punctuation:
        status = 'Discard - Short'
    elif row.at['unclear']:
        status = 'Discard - Unclear'
    elif type(row.at['human_transcription']) is list:
        status = 'Expert Required'
    elif row.at['status'] == 'Discard - Typewritten':
        status = row.at['status']
    return status


def consolidate_classification_rows(zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    too_few = zooniverse_classifications[zooniverse_classifications['seen_count'] < math.ceil(RETIREMENT_COUNT / 2)]
    zooniverse_classifications = zooniverse_classifications.drop(index=too_few.index)

    duplicates = zooniverse_classifications[zooniverse_classifications['seen_count'] > 1]
    unique_ids = set(duplicates['image_location'])
    for id_name in unique_ids:
        subset = zooniverse_classifications[zooniverse_classifications['image_location'] == id_name]
        new_row = subset.loc[subset.index[0], :]

        _handwritten_vote(new_row, subset)
        if new_row.at['handwritten']:
            _transcription_vote(new_row, subset)
            _unclear_vote(new_row, subset)

        else:
            new_row.at['status'] = 'Discard - Typewritten'

        zooniverse_classifications = zooniverse_classifications.drop(index=subset.index)
        zooniverse_classifications = zooniverse_classifications.append(new_row)

    zooniverse_classifications['status'] = zooniverse_classifications.apply(_status_vote, axis=1)
    typed = zooniverse_classifications.query('handwritten == False')
    zooniverse_classifications = zooniverse_classifications.drop(index=typed.index)
    return zooniverse_classifications.sort_values(by=['block', 'paragraph', 'word'], ascending=True)


def update_full_image_paths(folders: List[Path], zooniverse_classifications: pd.DataFrame) -> None:
    collector_barcodes = data_loader.load_pickle(Path('C:\\Users\\betht\\Documents\\Field Museum\\' + \
                                                      'ocr_handwritten_labels\\file_resources\\barcode_dict.pickle'))
    for idx, row in zooniverse_classifications.iterrows():
        barcode = row['barcode']
        collector = collector_barcodes[barcode]
        zooniverse_classifications.at[idx, 'collector'] = collector
        image_name = row['image_location']
        found_image_path = None
        for one_folder in folders:
            if os.path.exists(Path(one_folder, image_name)):
                found_image_path = Path(one_folder, image_name)
            elif os.path.exists(Path(one_folder, barcode + '.jpg')):
                found_image_path = Path(one_folder, barcode + '.jpg')
        if not found_image_path:
            if os.path.exists(image_name):
                found_image_path = image_name
            else:
                print(f'Warning: {image_name} doesn\'t exist in these folders.')
                found_image_path = Path(f'foo/{image_name}')
        zooniverse_classifications.at[idx, 'image_location'] = found_image_path


def expert_manual_review_steyermark(df: pd.DataFrame) -> None:
    df.loc[df['id'] == 'C0601392F-b11p0w0', ('handwritten', 'human_transcription', 'status')] = \
        (True, 'No. 26403', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b12p0w0', ('handwritten', 'human_transcription', 'status')] = \
        (True, 'No. 9866', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604052F-b12p0w0', ('handwritten', 'human_transcription', 'status')] = \
        (True, 'No. 23578', 'Expert Reviewed')
    df.loc[df['id'] == 'C0606667F-b13p0w0', ('handwritten', 'status')] = \
        (True, 'Expert Reviewed')
    df.loc[df['id'] == 'C0611047F-b14p3w0', ('handwritten', 'human_transcription', 'status')] = \
        (True, 'May. 6,1939', 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b19p0w0', ('handwritten', 'status')] = \
        (True, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b14p0w4', ('handwritten', 'status')] = (False, 'Discard - Reviewed')
    df.loc[df['id'] == 'C0603614F-b9p0w0', ('handwritten', 'status')] = (False, 'Discard - Reviewed')
    df.loc[df['id'] == 'C0611047F-b11p0w1', ('handwritten', 'status')] = (False, 'Discard - Reviewed')

    df.loc[df['id'] == 'C0612468F-b12p0w16', ('human_transcription', 'status')] = ('Springs,', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b11p0w7', ('human_transcription', 'status')] = ('of', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602626F-b11p0w6', ('human_transcription', 'status')] = ('tributary', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b12p0w0', ('human_transcription', 'status')] = ('Hier', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b13p0w1', ('human_transcription', 'status')] = ('latiusculum', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b13p1w16', ('human_transcription', 'status')] = ('sect', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603614F-b10p0w0', ('human_transcription', 'status')] = ('Nieuwl.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603614F-b12p1w1', ('human_transcription', 'status')] = ('Montevallo', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b11p1w21', ('human_transcription', 'status')] = ('City', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603621F-b10p0w1', ('human_transcription', 'status')] = ('Aspidium', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b14p0w4', ('human_transcription', 'status')] = ('Wooded', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b14p1w1', ('human_transcription', 'status')] = ('Michx', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b14p2w10', ('human_transcription', 'status')] = ('mi', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b14p2w12', ('human_transcription', 'status')] = ('W.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b18p0w0', ('human_transcription', 'status')] = ('Sept.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p0w2', ('human_transcription', 'status')] = ('N', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b15p0w0', ('human_transcription', 'status')] = ('Onoclea', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b15p0w2', ('human_transcription', 'status')] = ('f. obtusilobata', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b10p1w20', ('human_transcription', 'status')] = ('Munger', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b12p0w0', ('human_transcription', 'status')] = ('Osmunda', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b12p0w1', ('human_transcription', 'status')] = ('regalis', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609475F-b12p0w10', ('human_transcription', 'status')] = ('Creek,', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609475F-b12p0w13', ('human_transcription', 'status')] = ('R19W', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609475F-b12p0w8', ('human_transcription', 'status')] = ('slopes along', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609795F-b13p0w2', ('human_transcription', 'status')] = ('R23W', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609795F-b14p0w1', ('human_transcription', 'status')] = ('fragilis', 'Expert Reviewed')
    df.loc[df['id'] == 'C0611047F-b12p0w2', ('human_transcription', 'status')] = ('Prantl', 'Expert Reviewed')

    df.loc[df['id'] == 'C0601164F - b11p0w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0602626F - b11p1w10', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604088F-b14p0w7', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604088F-b14p1w8', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604948F-b15p0w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0609475F-b12p0w15', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0609475F-b12p0w7', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0611180F-b15p0w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0612468F-b12p0w15', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0612468F-b12p1w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0625663F-b16p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0625663F-b16p0w11', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0602626F-b11p1w10', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0601389F-b11p0w9', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603620F-b11p1w5', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603621F-b10p1w14', 'status'] = 'Expert Reviewed'  # cut off on both sides
    df.loc[df['id'] == 'C0603621F-b10p3w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0601385F-b11p1w29', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0601579F-b13p0w26', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603617F-b9p0w20', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603618F-b12p2w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603619F-b8p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603622F-b10p0w10', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603758F-b15p0w7', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603758F-b15p1w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603843F-b16p1w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604051F-b12p0w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604051F-b14p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604054F-b12p0w21', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604055F-b13p0w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604055F-b13p1w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604057F-b13p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604057F-b13p1w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604087F-b14p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604683F-b10p0w11', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604683F-b10p0w14', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604903F-b14p1w19', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604904F-b10p1w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604905F-b10p0w6', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604905F-b10p0w15', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604905F-b10p1w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604906F-b13p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604907F-b8p1w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604907F-b8p2w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604909F-b11p0w8', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604909F-b11p0w25', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604909F-b11p1w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604910F-b10p2w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0605228F-b10p0w6', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0605228F-b10p0w16', 'status'] = 'Expert Reviewed'
    # df.loc[df['id'] == '', 'status'] = 'Expert Reviewed'

    df.loc[df['id'] == 'C0603621F-b12p0w0', ('human_transcription', 'status')] = ('Aug', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b14p2w1', ('human_transcription', 'status')] = ('Ridge', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p0w0', ('human_transcription', 'status')] = ('Crevices', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p1w0', ('human_transcription', 'status')] = ('facing', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p1w1', ('human_transcription', 'status')] = (
        'T53N', 'Expert Reviewed')  # cut off on end
    df.loc[df['id'] == 'C0604948F-b15p1w4', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604948F-b15p2w0', ('human_transcription', 'status')] = (
        'Fork', 'Expert Reviewed')  # cut off on both sides
    df.loc[df['id'] == 'C0604948F-b15p2w13', ('human_transcription', 'status')] = ('E.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605227F-b9p0w15', ('human_transcription', 'status')] = ('R9W', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b10p1w8', ('human_transcription', 'status')] = ('Fork', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b10p2w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0605417F-b12p0w19', ('human_transcription', 'status')] = ('of', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b12p0w2', ('human_transcription', 'status')] = (
        'var. spec', 'Expert Reviewed')  # cut off on end
    df.loc[df['id'] == 'C0605417F-b12p0w3', ('human_transcription', 'status')] = ('tabilis', 'Expert Reviewed')
    df.loc[df['id'] == 'C0606902F-b12p1w14', ('human_transcription', 'status')] = (
        'Tom', 'Expert Reviewed')  # cut off both sides
    df.loc[df['id'] == 'C0606902F-b12p1w15', ('human_transcription', 'status')] = (
        'Sauk', 'Expert Reviewed')  # cut off both sides
    df.loc[df['id'] == 'C0606902F-b12p2w0', ('human_transcription', 'status')] = ('S.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0607530F-b12p1w1', ('human_transcription', 'status')] = (
        'Fork', 'Expert Reviewed')  # cut off on both sides
    df.loc[df['id'] == 'C0603758F-b14p0w3', ('unclear', 'status')] = (False, 'Expert Reviewed')
    df.loc[df['id'] == 'C0607745F-b15p0w0', ('human_transcription', 'status')] = ('June', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609229F-b12p1w15', ('human_transcription', 'status')] = ('Hollow,', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609229F-b12p1w5', ('human_transcription', 'status')] = ('Along', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609475F-b12p1w2', ('human_transcription', 'status')] = ('6,', 'Expert Reviewed')
    df.loc[df['id'] == 'C0611047F-b14p0w6', ('human_transcription', 'status')] = ('sect', 'Expert Reviewed')
    df.loc[df['id'] == 'C0612468F-b11p0w3', ('human_transcription', 'status')] = ('L.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603617F-b9p0w35', ('human_transcription', 'status')] = ('Callaway', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603619F-b8p1w0', ('human_transcription', 'status')] = ('uarry', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604051F-b12p1w1', ('human_transcription', 'status')] = ('Co', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604057F-b13p1w0', ('human_transcription', 'status')] = ('ewis', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604683F-b10p1w5', ('human_transcription', 'status')] = ('5/1939', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604905F-b10p0w17', ('human_transcription', 'status')] = ('N.W', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605228F-b10p0w1', ('human_transcription', 'status')] = ('claytoniana', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605228F-b11p0w0', ('human_transcription', 'status')] = ('No. 257', 'Expert Reviewed')
    # df.loc[df['id'] == '', ('human_transcription', 'status')] = ('', 'Expert Reviewed')

    df.loc[df['id'] == 'C0625663F-b20p0w23', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604088F - b14p1w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603614F-b11p0w0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604052F-b11p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0606667F-b12p0w16', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0609229F-b12p1w19', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603620F-b11p1w16', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602766F-b13p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0607517F-b13p0w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0609475F-b12p0w14', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0609475F-b12p0w6', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601164F-b12p0w0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604052F-b11p1w1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604053F-b14p0w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604053F-b18p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0609229F-b12p0w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604088F-b14p1w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601164F-b11p0w1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601070F-b14p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601387F-b12p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601579F-b13p1w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601779F-b9p0w34', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603619F-b8p1w6', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603619F-b8p1w9', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603619F-b8p2w5', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603619F-b9p0w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603627F-b10p0w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603627F-b10p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603843F-b13p1w6', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604051F-b12p0w7', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604054F-b12p0w1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604087F-b16p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604683F-b10p1w4', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604905F-b10p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604906F-b12p0w6', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604907F-b8p1w10', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604907F-b8p1w11', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604909F-b11p0w5', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604909F-b11p0w16', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604909F-b12p0w0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604910F-b10p0w6', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604910F-b10p1w8', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604910F-b10p2w1', 'status'] = 'Discard - Reviewed'


def expert_manual_review_standley(df: pd.DataFrame) -> None:
    df.loc[df['id'] == 'C0361312F-b18p0w3', ('unclear', 'status')] = (False, 'Expert Reviewed')
    df.loc[df['id'] == 'C0384964F-b15p0w0', ('human_transcription', 'status')] = ('nderw.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0615106F-b16p0w0', ('human_transcription', 'status')] = ('hes', 'Expert Reviewed')
    df.loc[df['id'] == 'C0615742F-b16p1w0', ('human_transcription', 'status')] = ('um serratu', 'Expert Reviewed')
    df.loc[df['id'] == 'C0358756F-b18p0w2', ('human_transcription', 'status')] = ('maxo', 'Expert Reviewed')
    df.loc[df['id'] == 'C0361270F-b17p0w0', ('human_transcription', 'status')] = ('Phanerophlebia', 'Expert Reviewed')
    df.loc[df['id'] == 'C0361295F-b14p0w4', ('human_transcription', 'status')] = ('hapm', 'Expert Reviewed')
    df.loc[df['id'] == 'C0361295F-b14p0w7', ('human_transcription', 'status')] = ('.U.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0606741F-b11p1w1', ('human_transcription', 'status')] = ('anch', 'Expert Reviewed')
    df.loc[df['id'] == 'C0608095F-b14p0w0', ('human_transcription', 'status')] = ('n', 'Expert Reviewed')
    df.loc[df['id'] == 'C0608963F-b14p0w4', ('human_transcription', 'status')] = ('dum', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609134F-b22p0w4', ('human_transcription', 'status')] = ('Wet f', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609134F-b23p0w1', ('human_transcription', 'status')] = ('orest', 'Expert Reviewed')
    df.loc[df['id'] == 'C0610937F-b11p0w2', ('human_transcription', 'status')] = ('europaeum', 'Expert Reviewed')
    df.loc[df['id'] == 'C0610937F-b13p0w0', ('human_transcription', 'status')] = ('ug.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0611164F-b18p0w1', ('human_transcription', 'status')] = ('silotum', 'Expert Reviewed')
    df.loc[df['id'] == 'C0611168F-b14p1w0', ('human_transcription', 'status')] = ('County On', 'Expert Reviewed')
    df.loc[df['id'] == 'C0612935F-b15p0w1', ('human_transcription', 'status')] = ('ban', 'Expert Reviewed')
    df.loc[df['id'] == 'C0613085F-b9p0w0', ('human_transcription', 'status')] = ('quisetum', 'Expert Reviewed')
    df.loc[df['id'] == 'C0613136F-b12p1w0', ('human_transcription', 'status')] = ('. Br', 'Expert Reviewed')
    # df.loc[df['id'] == '', ('human_transcription', 'status')] = ('', 'Expert Reviewed')

    df.loc[df['id'] == 'C0358543F-b13p0w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0361268F-b19p0w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0361271F-b13p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0361350F-b18p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0384343F-b12p0w1', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0384343F-b12p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0384343F-b14p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0385183F-b18p0w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0385187F-b11p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0385187F-b11p0w6', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0605359F-b8p0w6', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0605614F-b14p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0606741F-b11p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0606741F-b11p1w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0606741F-b11p1w4', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0609134F-b23p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0612935F-b20p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0612993F-b13p0w3', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0613061F-b14p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0613093F-b13p0w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0613097F-b11p1w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0613144F-b12p0w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0613149F-b10p1w1', 'status'] = 'Expert Reviewed'
    # df.loc[df['id'] == '', 'status'] = 'Expert Reviewed'

    df.loc[df['id'] == 'C0384980F-b17p0w16', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0611079F-b19p0w0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0613343F-b21p0w11', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0605512F-b10p1w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0609490F-b12p0w24', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0606387F-b15p1w8', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0605770F-b16p0w0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0361270F-b17p0w2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0361270F-b17p0w3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0384344F-b18p1w1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0605614F-b17p0w1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0608095F-b13p0w4', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0612993F-b13p0w1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0613149F-b10p1w0', 'status'] = 'Discard - Reviewed'
    # df.loc[df['id'] == '', 'status'] = 'Discard - Reviewed'


def compare_gcv_to_human(zooniverse_classifications: pd.DataFrame) -> None:
    subset = zooniverse_classifications.query("status == 'Complete' or 'status' == 'Expert Reviewed'")
    zooniverse_classifications['matches'] = subset['gcv_identification'] == subset['human_transcription']
    summary = zooniverse_classifications['matches'].value_counts()
    ratio = summary.at[False] / (summary.at[False] + summary.at[True])
    print('Zooniverse users corrected %i values and confirmed %i values (%.2f%%)' %
          (summary.at[False], summary.at[True], ratio * 100))


def save_images_to_folders(zooniverse_classifications: pd.DataFrame, word_image_folder: Path) -> None:
    if not os.path.exists(word_image_folder):
        os.makedirs(word_image_folder)

    filtered_zooniverse: pd.DataFrame = zooniverse_classifications \
        .query("handwritten == True and (status == 'Complete' or status == 'Expert Reviewed')")
    word_image_metadata = filtered_zooniverse.copy()
    word_image_metadata = word_image_metadata.rename(columns={'image_location': 'zooniverse_image_location'})
    image_processor = GCVProcessor()
    for idx, row in filtered_zooniverse.iterrows():
        full_size_image_location = os.path.join('images', 'Steyermark-2021_04_30-891', row['barcode'] + '.jpg')  # todo: HUH? WHAT'S THIS ABOUT?
        word_filename = row['id'] + '-word.jpg'

        image_processor.load_image_from_file(full_size_image_location)
        # 1. find bounding box of word
        word_info = [w for w in image_processor.get_list_of_words()
                     if w['b_idx'] == row['block'] and w['p_idx'] == row['paragraph'] and w['w_idx'] == row['word']]
        word_info = word_info[0]
        # 2. crop image to bounding box
        x_min, y_min = list(map(min, *word_info['bounding_box']))
        x_max, y_max = list(map(max, *word_info['bounding_box']))
        x_min = max(0, x_min - 20)
        x_max = min(x_max + 10, image_processor.current_image_width)
        word_image = image_processor.annotator.cropped_image(x_min, x_max, y_min, y_max)
        # 3. save image to word_image_folder
        save_location = data_loader.save_cv2_image(word_image_folder, word_filename, word_image, timestamp=False)
        # 4. add word image location to zooniverse_classifications
        zooniverse_classifications.at[idx, 'word_image_location'] = save_location
        word_image_metadata.at[idx, 'full_size_image_location'] = full_size_image_location
        word_image_metadata.at[idx, 'word_image_location'] = save_location
    data_loader.save_dataframe_as_csv(word_image_folder, 'words_metadata', word_image_metadata, timestamp=False)


def maine():
    zooniverse_results = Path('C:\\Users\\betht\\Downloads\\2021_11_03-humans-versus-machines-deciphering-herbarium-handwriting-classifications.csv')
    image_folders = [Path('file_resources\\processed_images_zooniverse-Standley'),
                     Path('file_resources\\processed_images_zooniverse-Steyermark')]
    main(zooniverse_results, image_folders)

if __name__ == '__main__':
    # assert len(sys.argv) >= 3, 'Include 3+ arguments: (1) the location of the Zooniverse CSV classifications, ' + \
    #                            '(2) the folder in which to save images for the neural network, or "None" if' + \
    #                            'not generating the images, and' + \
    #                            '(3+) the folder(s) of label images which were used in Zooniverse. '
    # zooniverse_results = Path(sys.argv[1])
    zooniverse_results = Path('C:\\Users\\betht\\Downloads\\2021_11_03-humans-versus-machines-deciphering-herbarium-handwriting-classifications.csv')
    # assert os.path.isfile(zooniverse_results), 'Invalid 1st argument: `%s` must be a file on the local computer.' \
    #                                            % zooniverse_results

    # image_folders = [Path(f) for f in sys.argv[3:]]
    image_folders = [Path('file_resources\\processed_images_zooniverse-Standley'),
                     Path('file_resources\\processed_images_zooniverse-Steyermark')]
    # for folder in image_folders:
    #     if not os.path.exists(folder):
    #         os.makedirs(folder)

    main(zooniverse_results, image_folders)
    # if len(sys.argv) == 3:
    #     main(zooniverse_results, image_folder)
    # else:
    #     # words_save_folder = os.path.join('file_resources', 'word_images')
    #     words_save_folder = Path(sys.argv[2])
    #     main(zooniverse_results, image_folders, words_save_folder)
