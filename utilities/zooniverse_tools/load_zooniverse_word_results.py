import os
import sys
import shutil
import ast
import pandas as pd
from typing import Union
from statistics import mode, StatisticsError, multimode
sys.path.append('')  # to run __main__
from utilities import data_loader


def main(zooniverse_classifications_path: str, source_image_folder_path: str,
         image_save_folder=os.path.join('file_resources', 'zooniverse_word_images'), create_image_folders=False):
    raw_zooniverse_classifications = pd.read_csv(zooniverse_classifications_path)
    zooniverse_classifications = parse_raw_zooniverse_file(raw_zooniverse_classifications)
    zooniverse_classifications = consolidate_classifications(zooniverse_classifications)
    load_letter_images(source_image_folder_path, zooniverse_classifications)  # todo
    expert_manual_review(zooniverse_classifications)  # todo
    save_location = data_loader.save_dataframe_as_csv('file_resources', 'zooniverse_parsed', zooniverse_classifications)
    print('Saved to %s' % save_location)
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
        image_name = s['image_of_boxed_letter'].replace('box', '')
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
        new_row = subset.head(1).copy()
        idx = new_row.index[0]
        new_row.loc[idx, 'human_transcription'], count, total = vote(subset, 'human_transcription')
        new_row.loc[idx, 'confidence'] = count / total
        new_row.loc[idx, 'status'] = 'Expert Required' if new_row.loc[idx, 'confidence'] < 0.6 else 'Complete'
        new_row.loc[idx, 'unclear'], _, _ = vote(subset, 'unclear')
        new_row.loc[idx, 'handwritten'], _, _ = vote(subset, 'handwritten')
        # discard any results where the majority voted for unclear & blank
        if new_row.loc[idx, 'status'] == 'Complete' and new_row.loc[idx, 'unclear']:  # if majority says unclear
            new_row.loc[idx, 'status'] = 'Discard'
        if len(new_row.loc[idx, 'human_transcription']) > 1:  # if there's a tie
            new_row.loc[idx, 'status'] = 'Expert Required'
        zooniverse_classifications = zooniverse_classifications.drop(subset.index)
        zooniverse_classifications = zooniverse_classifications.append(new_row)
        # print('Group %s vote is %s with a confidence of %.0f' %
        #       (id_name, new_row['human_transcription'].values[0], (new_row['confidence'].values[0])*100) + '%' +
        #       ' (%i/%i).' % (count, total))
    return zooniverse_classifications.sort_values(by=['block', 'paragraph', 'word'], ascending=True)


def vote(df: pd.DataFrame, col_name: str) -> (Union[list, str], int, int):
    total = df.shape[0]

    voted = multimode(list(df.loc[:, col_name]))
    most_voted = voted[0]

    voted_count = df[df[col_name] == most_voted].shape[0]

    return voted, voted_count, total


def load_letter_images(image_folder_path: str, zooniverse_classifications: pd.DataFrame) -> None:
    for idx, row in zooniverse_classifications.iterrows():
        image_name = row['image_location']
        if not os.path.isfile(os.path.join(image_folder_path, image_name)):
            print("Warning: %s doesn't exist in this location." % image_name)
        zooniverse_classifications.at[idx, 'image_location'] = os.path.join(image_folder_path, image_name)


def expert_manual_review(df: pd.DataFrame) -> None:
    df.loc[df['id'] == 'C0603620F-b1p0w0s8', ('human_transcription', 'status')] = ('r', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b1p0w0s1', ('human_transcription', 'status')] = ('h', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601389F-b1p0w0s9', ('human_transcription', 'status')] = ('s', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w8s4', ('human_transcription', 'status')] = ('.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w12s0', ('human_transcription', 'status')] = ('B', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604052F-b1p0w15s0', ('human_transcription', 'status')] = ('s', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604908F-b1p1w18s1', ('human_transcription', 'status')] = ('i', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p0w10s1', ('human_transcription', 'status')] = ('n', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p0w11s4', ('human_transcription', 'status')] = ('k', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p1w0s1', ('human_transcription', 'status')] = ('o', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p1w4s0', ('human_transcription', 'status')] = ('2', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b1p0w0s3', ('human_transcription', 'status')] = ('l', 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w0s3', ('human_transcription', 'status')] = ('o', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604052F-b1p0w0s5', ('human_transcription', 'status')] = ('y', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602626F-b1p0w0s6', ('human_transcription', 'status')] = ('u', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w3s0', ('human_transcription', 'status')] = ('C', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w5s3', ('human_transcription', 'status')] = ('a', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w12s1', ('human_transcription', 'status')] = ('a', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w12s2', ('human_transcription', 'status')] = ('g', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p0w15s2', ('human_transcription', 'status')] = ('1', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p0w20s0', ('human_transcription', 'status')] = (',', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b1p1w0s4', ('human_transcription', 'status')] = ('w', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b1p1w3s0', ('human_transcription', 'status')] = ('A', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b1p1w5s0', ('human_transcription', 'status')] = ('s', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601389F-b1p1w7s0', ('human_transcription', 'status')] = ('P', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601389F-b1p1w14s0', ('human_transcription', 'status')] = ('1', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604908F-b1p1w24s3', ('human_transcription', 'status')] = ('t', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b1p2w0s1', ('human_transcription', 'status')] = ('o', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b1p2w8s0', ('human_transcription', 'status')] = ('s', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b1p2w15s5', ('human_transcription', 'status')] = ('l', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b1p3w1s0', ('human_transcription', 'status')] = ('3', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b1p3w5s3', ('human_transcription', 'status')] = ('.', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b2p0w0s0', ('human_transcription', 'status')] = ('S', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b2p0w2s1', ('human_transcription', 'status')] = ('8', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p3w0s1', ('human_transcription', 'status')] = ('p', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b3p0w0s1', ('human_transcription', 'status')] = ('f', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p0w9s4', ('human_transcription', 'status')] = ('l', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p0w23s1', ('human_transcription', 'status')] = ('o', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604052F-b1p0w0s1', ('human_transcription', 'status')] = ('o', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604908F-b1p0w0s4', ('human_transcription', 'status')] = ('l', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b1p0w0s6', ('human_transcription', 'status')] = ('i', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601389F-b1p0w1s2', ('human_transcription', 'status')] = ('i', 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w1s5', ('human_transcription', 'status')] = ('i', 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w1s8', ('human_transcription', 'status')] = ('e', 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w1s9', ('human_transcription', 'status')] = ('r', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604052F-b1p0w1s10', ('human_transcription', 'status')] = ('i', 'Expert Reviewed')
    df.loc[df['id'] == 'C0604052F-b1p0w2s0', ('human_transcription', 'status')] = ('M', 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p0w17s0', ('human_transcription', 'status')] = ('s', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602626F-b1p1w15s0', ('human_transcription', 'status')] = (',', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b1p3w1s0', ('human_transcription', 'status')] = ('R', 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b1p4w2s1', ('human_transcription', 'status')] = ('0', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p0w0s6', ('human_transcription', 'status')] = ('i', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p0w2s0', ('human_transcription', 'status')] = ('D', 'Expert Reviewed')
    df.loc[df['id'] == 'C0603614F-b2p0w30s1', ('human_transcription', 'status')] = ('e', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p1w4s1', ('human_transcription', 'status')] = ('o', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p1w8s3', ('human_transcription', 'status')] = ('l', 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p3w0s0', ('human_transcription', 'status')] = ('A', 'Expert Reviewed')

    df.loc[df['id'] == 'C0602626F-b1p0w0s6', ('unclear', 'status')] = (True, 'Discard')
    df.loc[df['id'] == 'C0604052F-b1p0w2s1', ('unclear', 'status')] = (True, 'Discard')

    df.loc[df['id'] == 'C0601389F-b1p0w1s8', ('human_transcription', 'confidence', 'status')] = \
        ('l', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0604908F-b1p0w1s8', ('human_transcription', 'confidence', 'status')] = \
        ('i', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b1p0w3s18', ('human_transcription', 'confidence', 'status')] = \
        ('k', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0604908F-b1p1w1s0', ('human_transcription', 'confidence', 'status')] = \
        ('f', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p1w1s1', ('human_transcription', 'confidence', 'status')] = \
        ('o', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p0w4s3', ('human_transcription', 'confidence', 'status')] = \
        ('.', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p0w22s1', ('human_transcription', 'confidence', 'status')] = \
        ('i', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0605417F-b0p0w4s2', ('human_transcription', 'confidence', 'status')] = \
        ('r', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w0s5', ('human_transcription', 'confidence', 'status')] = \
        ('t', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w1s0', ('human_transcription', 'confidence', 'status')] = \
        ('b', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b1p0w1s5', ('human_transcription', 'confidence', 'status')] = \
        ('i', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b1p0w1s9', ('human_transcription', 'confidence', 'status')] = \
        ('o', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b1p0w2s3', ('human_transcription', 'confidence', 'status')] = \
        ('l', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0604948F-b1p0w3s6', ('human_transcription', 'confidence', 'status')] = \
        ('s', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0602760F-b1p0w5s2', ('human_transcription', 'confidence', 'status')] = \
        ('l', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p0w6s5', ('human_transcription', 'confidence', 'status')] = \
        ('t', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p0w12s3', ('human_transcription', 'confidence', 'status')] = \
        ('e', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601392F-b1p1w1s1', ('human_transcription', 'confidence', 'status')] = \
        ('5', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b1p1w10s3', ('human_transcription', 'confidence', 'status')] = \
        ('t', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0603620F-b1p1w18s1', ('human_transcription', 'confidence', 'status')] = \
        ('i', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0601164F-b1p3w1s1', ('human_transcription', 'confidence', 'status')] = \
        ('1', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0604908F-b1p3w3s0', ('human_transcription', 'confidence', 'status')] = \
        (',', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0605403F-b1p3w4s0', ('human_transcription', 'confidence', 'status')] = \
        (',', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0602766F-b2p1w6s6', ('human_transcription', 'confidence', 'status')] = \
        ('t', 1, 'Expert Reviewed')
    df.loc[df['id'] == 'C0045392F-b6p0w3s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0045392F-b1p0w1s1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604052F-b1p0w2s1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604052F-b1p0w2s3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601392F-b1p0w15s4', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601392F-b1p1w0s4', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604948F-b1p2w12s3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603620F-b2p0w0s1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603620F-b2p1w3s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602766F-b2p1w5s5', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602766F-b2p1w6s5', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604948F-b6p0w1s1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0605417F-b0p1w0s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601164F-b1p0w1s2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602626F-b1p0w1s9', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604052F-b1p0w1s11', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604052F-b1p0w2s2', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602626F-b1p1w10s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604948F-b1p2w12s1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603614F-b2p0w1s4', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602766F-b2p1w1s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602766F-b2p2w0s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0045392F-b6p0w3s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0602626F-b1p0w1s3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0045392F-b1p0w1s6', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601155F-b1p0w9s1', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604908F-b1p1w0s3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0605403F-b1p1w1s3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604948F-b1p1w1s4', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604908F-b1p1w8s0', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0603620F-b1p1w22s3', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0604948F-b1p2w12s5', 'status'] = 'Discard - Reviewed'
    df.loc[df['id'] == 'C0601389F-b1p0w1s12', 'status'] = 'Discard - Reviewed'


def save_images_to_folders(zooniverse_classifications: pd.DataFrame, dest_folder: str):
    filtered_zooniverse: pd.DataFrame = zooniverse_classifications\
        .query("handwritten == True and (status == 'Complete' or status == 'Expert Reviewed')").copy()
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    image_class_mappings = {'0': '30', '1': '31', '2': '32', '3': '33', '4': '34', '5': '35', '6': '36', '7': '37',
                            '8': '38', '9': '39', 'A': '41', 'B': '42', 'C': '43_63', 'D': '44', 'E': '45', 'F': '46',
                            'G': '47', 'H': '48', 'I': '49_69', 'J': '4a_6a', 'K': '4b_6b', 'L': '4c_6c', 'M': '4d_6d',
                            'N': '4e', 'O': '4f_6f', 'P': '50_70', 'Q': '51', 'R': '52', 'S': '53_73', 'T': '54',
                            'U': '55_75', 'V': '56_76', 'W': '57_77', 'X': '58_78', 'Y': '59_79', 'Z': '5a_7a',
                            'a': '61', 'b': '62', 'c': '43_63', 'd': '64', 'e': '65', 'f': '66', 'g': '67', 'h': '68',
                            'i': '49_69', 'j': '4a_6a', 'k': '4b_6b', 'l': '4c_6c', 'm': '4d_6d', 'n': '6e',
                            'o': '4f_6f', 'p': '50_70', 'q': '71', 'r': '72', 's': '53_73', 't': '74', 'u': '55_75',
                            'v': '56_76', 'w': '57_77', 'x': '58_78', 'y': '59_79', 'z': '5a_7a'}
    for v in image_class_mappings.values():
        path = os.path.join(dest_folder, v)
        if not os.path.exists(path):
            os.makedirs(path)
    for idx, row in filtered_zooniverse.iterrows():
        image_location = row['image_location']
        if row['human_transcription'] in image_class_mappings.keys():
            image_class = image_class_mappings[row['human_transcription']]
            dest = os.path.join(dest_folder, image_class)
            shutil.copy(image_location, dest)


if __name__ == '__main__':
    # assert len(sys.argv) == 4, 'Include 2 or 3 arguments: (1) the location of the classification results ' +\
    #         'from Zooniverse, (2) the folder of herbarium sheet images, and (3) word image save folder.'
    zooniverse_results = os.path.join('file_resources',
                                      '2021_06_14-herbarium_handwriting_transcription_classifications-words.csv')
    # zooniverse_results = sys.argv[1]
    assert os.path.isfile(zooniverse_results), 'Invalid 1st argument: `%s` must be a file on the local computer.' \
                                               % zooniverse_results

    existing_image_folder = 'C:\\Users\\betht\\Documents\\Field Museum\\ocr_handwritten_labels\\images\\full_size_label_images'
    # image_folder = sys.argv[2]
    assert os.path.isdir(existing_image_folder), 'Invalid 2nd argument: `%s` must be a folder on the local computer.' \
                                        % existing_image_folder

    words_save_folder = 'labeled_word_images'
    # words_save_folder = sys.argv[3]
    assert os.path.isdir(words_save_folder), 'Invalid 3rd argument: `%s` must be a folder on the local computer.' \
                                             % words_save_folder
    main(zooniverse_results, existing_image_folder, words_save_folder)
