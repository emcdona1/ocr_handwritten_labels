import os
import sys
import shutil
import ast
import pandas as pd
from typing import Union
from statistics import multimode
import string

sys.path.append('')  # to run __main__
from utilities import data_loader
from imageprocessor import GCVProcessor


def main(zooniverse_classifications_path: str, source_image_folder_path: str,
         image_save_folder=os.path.join('file_resources', 'zooniverse_word_images'), create_image_folders=False):
    raw_zooniverse_classifications = pd.read_csv(zooniverse_classifications_path)
    zooniverse_classifications = parse_raw_zooniverse_file(raw_zooniverse_classifications)
    zooniverse_classifications = consolidate_classifications(zooniverse_classifications)
    update_full_image_paths(source_image_folder_path, zooniverse_classifications)
    expert_manual_review(zooniverse_classifications)
    save_location = data_loader.save_dataframe_as_csv('file_resources', 'zooniverse_parsed', zooniverse_classifications)
    print('Saved to %s.' % save_location)
    compare_gcv_to_human(zooniverse_classifications)
    if create_image_folders:
        destination_folder = image_save_folder
        save_images_to_folders(zooniverse_classifications, destination_folder)


def parse_raw_zooniverse_file(raw_zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    filtered_raw_zooniverse = raw_zooniverse_classifications.query(
        'workflow_name == "Transcribe Words" and workflow_version == 3.7').copy()

    def clean_text_values(txt: str):
        txt = txt.replace('null', 'None')
        txt = ast.literal_eval(txt)
        if type(txt) is dict:  # for subject_data
            txt = [*txt.values()]
            txt = txt[0]
        return txt

    filtered_raw_zooniverse.loc[:, 'annotations'] = filtered_raw_zooniverse['annotations'].apply(clean_text_values)
    filtered_raw_zooniverse.loc[:, 'subject_data'] = filtered_raw_zooniverse['subject_data'].apply(clean_text_values)

    parsed_zooniverse_classifications = pd.DataFrame()
    parsed_zooniverse_classifications['id'] = filtered_raw_zooniverse['subject_data'].apply(
        lambda annotation: annotation['image_of_boxed_letter'].replace('wordbox-', '').replace('.jpg', '').replace(
            'label-', ''))

    def parse_subject(s):
        barcode = s['barcode'].split('-')[0]  # in case the file name includes "-label"
        image_name = s['image_of_boxed_letter']
        col_names = ['barcode', 'block', 'paragraph', 'word', 'gcv_identification', 'image_location']
        result = pd.Series([barcode, int(s['block_no']), int(s['paragraph_no']), int(s['word_no']),
                            s['#GCV_identification'], image_name], index=col_names)
        return result

    parsed_subjects = filtered_raw_zooniverse['subject_data'].apply(parse_subject)
    parsed_zooniverse_classifications = pd.concat([parsed_zooniverse_classifications, parsed_subjects], axis=1)
    parsed_zooniverse_classifications['handwritten'] = filtered_raw_zooniverse['annotations'].apply(
        lambda annotation: annotation[0]['value'] == 'handwritten')
    parsed_zooniverse_classifications['human_transcription'] = filtered_raw_zooniverse['annotations'].apply(
        lambda annotation: annotation[1]['value'])
    parsed_zooniverse_classifications['unclear'] = parsed_zooniverse_classifications['human_transcription'].apply(
        lambda transcription: '[unclear]' in transcription and '[/unclear]' in transcription)
    parsed_zooniverse_classifications['human_transcription'] = \
        parsed_zooniverse_classifications['human_transcription'] \
            .apply(lambda transcription: transcription.replace('[unclear][/unclear]', ''))

    parsed_zooniverse_classifications['seen_count'] = parsed_zooniverse_classifications.groupby('id')[
        'block'].transform(len)
    parsed_zooniverse_classifications['confidence'] = 1.0
    parsed_zooniverse_classifications['status'] = 'In Progress'
    return parsed_zooniverse_classifications


def consolidate_classifications(zooniverse_classifications: pd.DataFrame) -> pd.DataFrame:
    too_few = zooniverse_classifications[zooniverse_classifications['seen_count'] < 2]
    zooniverse_classifications = zooniverse_classifications.drop(too_few.index)

    duplicates = zooniverse_classifications[zooniverse_classifications['seen_count'] > 1]
    ids = set(duplicates['image_location'])
    for id_name in ids:
        subset = duplicates[duplicates['image_location'] == id_name]
        idx = subset.index[0]
        new_row = subset.loc[idx, :]
        voted, count, total = vote(subset, 'human_transcription')
        new_row.at['confidence'] = count / total
        new_row.at['human_transcription'] = voted
        new_row.at['status'] = 'Expert Required' if new_row.at['confidence'] <= 0.5 else 'Complete'

        unclear_vote, _, _ = vote(subset, 'unclear')
        if type(unclear_vote) is list and len(unclear_vote) > 1:  # if it's evenly split, mark as NOT unclear
            unclear_vote = False
        new_row.at['unclear'] = unclear_vote

        type_vote, _, _ = vote(subset, 'handwritten')
        new_row.at['handwritten'] = type_vote

        # discard any results where the majority voted for unclear & blank
        if type(new_row.at['human_transcription']) is str and len(new_row.at['human_transcription']) == 1 and \
                new_row.at['human_transcription'] in string.punctuation:
            new_row.at['status'] = 'Discard - Short'
        if new_row.at['status'] == 'Complete' and new_row.at['unclear']:  # if majority says unclear
            new_row.at['status'] = 'Discard - Unclear'
        if type(new_row.at['human_transcription']) is list:  # if there's a tie
            new_row.at['status'] = 'Expert Required'
        if new_row.at['status'] == 'Expert Required' and not new_row.at['handwritten']:
            new_row.at['status'] = 'Discard - Typewritten'
        zooniverse_classifications = zooniverse_classifications.drop(subset.index)
        zooniverse_classifications = zooniverse_classifications.append(new_row)
    return zooniverse_classifications.sort_values(by=['block', 'paragraph', 'word'], ascending=True)


def vote(df: pd.DataFrame, col_name: str) -> (Union[list, str], int, int):
    total = df.shape[0]

    voted = multimode(list(df.loc[:, col_name]))

    voted_count = df[df[col_name] == voted[0]].shape[0]

    if len(voted) == 1:  # single mode value
        voted = voted[0]

    return voted, voted_count, total


def update_full_image_paths(source_image_folder_path: str, zooniverse_classifications: pd.DataFrame) -> None:
    for idx, row in zooniverse_classifications.iterrows():
        image_name = row['image_location']
        if not os.path.isfile(os.path.join(source_image_folder_path, image_name)):
            print("Warning: %s doesn't exist in this location." % image_name)
        zooniverse_classifications.at[idx, 'image_location'] = os.path.join(source_image_folder_path, image_name)


def expert_manual_review(df: pd.DataFrame) -> None:
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
    # todo: keep this section of cut-off-first-letters ?
    df.loc[df['id'] == 'C0601389F-b11p0w9', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603620F-b11p1w5', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603621F-b10p1w14', 'status'] = 'Expert Reviewed'  # cut off on both sides
    df.loc[df['id'] == 'C0603621F-b10p3w2', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0603621F-b12p0w0', ('human_transcription', 'status')] = ('Aug', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604053F-b14p2w1', ('human_transcription', 'status')] = ('Ridge', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p0w0', ('human_transcription', 'status')] = ('Crevices', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p1w0', ('human_transcription', 'status')] = ('facing', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604088F-b14p1w1', ('human_transcription', 'status')] = ('T53N', 'Expert Reviewed')  # cut off on end
    df.loc[df['id'] == 'C0604948F-b15p1w4', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0604948F-b15p2w0', ('human_transcription', 'status')] = ('Fork', 'Expert Reviewed')  # cut off on both sides
    df.loc[df['id'] == 'C0604948F-b15p2w13', ('human_transcription', 'status')] = ('E.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605227F-b9p0w15', ('human_transcription', 'status')] = ('R9W', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b10p1w8', ('human_transcription', 'status')] = ('Fork', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b10p2w0', 'status'] = 'Expert Reviewed'
    df.loc[df['id'] == 'C0605417F-b12p0w19', ('human_transcription', 'status')] = ('of', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b12p0w2', ('human_transcription', 'status')] = ('var. spec', 'Expert Reviewed')  # cut off on end
    df.loc[df['id'] == 'C0605417F-b12p0w3', ('human_transcription', 'status')] = ('tabilis', 'Expert Reviewed')
    df.loc[df['id'] == 'C0606902F-b12p1w14', ('human_transcription', 'status')] = ('Tom', 'Expert Reviewed')  # cut off both sides
    df.loc[df['id'] == 'C0606902F-b12p1w15', ('human_transcription', 'status')] = ('Sauk', 'Expert Reviewed')  # cut off both sides
    df.loc[df['id'] == 'C0606902F-b12p2w0', ('human_transcription', 'status')] = ('S.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0607530F-b12p1w1', ('human_transcription', 'status')] = ('Fork', 'Expert Reviewed')  # cut off on both sides
    df.loc[df['id'] == 'C0607745F-b15p0w0', ('human_transcription', 'status')] = ('June', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609229F-b12p1w15', ('human_transcription', 'status')] = ('Hollow,', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609229F-b12p1w5', ('human_transcription', 'status')] = ('Along', 'Expert Reviewed')
    df.loc[df['id'] == 'C0609475F-b12p1w2', ('human_transcription', 'status')] = ('6,', 'Expert Reviewed')
    df.loc[df['id'] == 'C0611047F-b14p0w6', ('human_transcription', 'status')] = ('sect', 'Expert Reviewed')
    df.loc[df['id'] == 'C0612468F-b11p0w3', ('human_transcription', 'status')] = ('L.', 'Expert Reviewed')

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


def compare_gcv_to_human(zooniverse_classifications: pd.DataFrame) -> None:
    subset = zooniverse_classifications.query("status == 'Complete' or 'status' == 'Expert Reviewed'")
    zooniverse_classifications['matches'] = subset['gcv_identification'] == subset['human_transcription']
    summary = zooniverse_classifications['matches'].value_counts()
    ratio = summary.at[False] / (summary.at[False] + summary.at[True])
    print('Zooniverse users corrected %i values and confirmed %i values (%.2f%%)' %
          (summary.at[False], summary.at[True], ratio * 100))


def save_images_to_folders(zooniverse_classifications: pd.DataFrame, word_image_folder: str) -> None:
    # TODO: go back and get rid of single-punctuation "words," and add back removed ones w/ the first letter cut off
    if not os.path.exists(word_image_folder):
        os.makedirs(word_image_folder)

    filtered_zooniverse: pd.DataFrame = zooniverse_classifications \
        .query("handwritten == True and (status == 'Complete' or status == 'Expert Reviewed')")
    word_image_metadata = filtered_zooniverse.copy()
    word_image_metadata.rename(columns={'image_location': 'zooniverse_image_location'}, inplace=True)
    image_processor = GCVProcessor()
    for idx, row in filtered_zooniverse.iterrows():
        full_size_image_location = os.path.join('images', 'Steyermark-2021_04_30-891', row['barcode'] + '.jpg')
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
        word_image = image_processor.annotator.cropped_image(x_min, x_max, y_min, y_max)
        # 3. save image to word_image_folder
        save_location = data_loader.save_cv2_image(word_image_folder, word_filename, word_image, timestamp=False)
        # 4. add word image location to zooniverse_classifications
        zooniverse_classifications.at[idx, 'word_image_location'] = save_location
        word_image_metadata.at[idx, 'full_size_image_location'] = full_size_image_location
        word_image_metadata.at[idx, 'word_image_location'] = save_location
    data_loader.save_dataframe_as_csv(word_image_folder, 'words_metadata', word_image_metadata, timestamp=False)


if __name__ == '__main__':
    assert 3 <= len(sys.argv) <= 4, 'Include 2 or 3 arguments: (1) the location of the Zooniverse CSV results, ' + \
                                    '(2) the folder of label images used in Zooniverse, and ' + \
                                    '(3) (optional) the folder in which to save word images.'
    zooniverse_results = os.path.join('file_resources',
                                      '2021_06_14-herbarium_handwriting_transcription_classifications-words.csv')
    # zooniverse_results = sys.argv[1]
    assert os.path.isfile(zooniverse_results), 'Invalid 1st argument: `%s` must be a file on the local computer.' \
                                               % zooniverse_results

    existing_image_folder = 'processed_images_zooniverse_30_words'
    # image_folder = sys.argv[2]
    assert os.path.isdir(existing_image_folder), 'Invalid 2nd argument: `%s` must be a folder on the local computer.' \
                                                 % existing_image_folder

    if len(sys.argv) == 3:
        main(zooniverse_results, existing_image_folder)
    else:
        words_save_folder = sys.argv[3]
        main(zooniverse_results, existing_image_folder, words_save_folder)
