"""Provide a baseline comparison score [0, 100] between OCR systems, using NLTK."""
import sys
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from fuzzywuzzy import fuzz
from utilities.dataloader import save_dataframe_as_csv


def main(occurrence_filepath, ocr_filepath):
    """ Load, populate, and return a pd.DataFrame with OCR text and quality analysis. """
    mi = pd.MultiIndex.from_arrays(
        [['ground_truth', 'ground_truth', 'ground_truth', 'aws', 'aws', 'aws', 'gcv', 'gcv', 'gcv'],
         ['barcode', 'text', 'filtered_tokens'] + ['text', 'fuzzy_match_list', 'score']*2],
        names=('dataset', 'item'))
    analysis = pd.DataFrame(columns=mi)
    analysis = load_ocr_from_file(analysis, ocr_filepath)
    analysis = add_ground_truth_text(analysis, occurrence_filepath)

    for idx, ocr_row in analysis.iterrows():
        aws_tokens = word_tokenize(ocr_row['aws']['text'])
        gcv_tokens = word_tokenize(ocr_row['gcv']['text'])
        aws_match_results = list()
        gcv_match_results = list()
        ground_truth_filtered_words = preprocess_text(word_tokenize(ocr_row['ground_truth']['text']))
        analysis.at[[idx], ('ground_truth', 'filtered_tokens')] = pd.Series([ground_truth_filtered_words], index=[idx])
        for search_word in analysis.at[idx, ('ground_truth', 'filtered_tokens')]:
            aws_best_matches_list, aws_best_ratio = fuzzy_match_with_token_list(search_word, aws_tokens)
            gcv_best_matches_list, gcv_best_ratio = fuzzy_match_with_token_list(search_word, gcv_tokens)
            aws_match_results.append((aws_best_matches_list, aws_best_ratio))
            gcv_match_results.append((gcv_best_matches_list, gcv_best_ratio))

        analysis.at[idx, ('aws', 'score')] = generate_score('aws', aws_match_results)
        analysis.at[idx, ('gcv', 'score')] = generate_score('gcv', gcv_match_results)
        analysis.at[[idx], ('aws', 'fuzzy_match_list')] = pd.Series([aws_match_results], index=[idx])
        analysis.at[[idx], ('gcv', 'fuzzy_match_list')] = pd.Series([gcv_match_results], index=[idx])
    filename = save_dataframe_as_csv('test_results', 'compare_ocr', analysis)
    print('%i row(s) processed and saved to %s' % (analysis.shape[0], filename))


def load_ocr_from_file(analysis: pd.DataFrame, filepath: str) -> pd.DataFrame:
    """ Loads in OCR transcriptions and ground truth text from a file as a pd.DataFrame."""
    ocr_data: pd.DataFrame = pd.read_csv(filepath)
    for idx, ocr_row in ocr_data.iterrows():
        barcode = ocr_row['barcode']
        aws = ocr_row['aws']
        # aws = 'FLORA OF MISSOURI\nasplenium pinnatifidum nutt\non north exposure in crevices\n' + \
        #       'of granite, mear summit of\nstughes mt., 4 miles S.rt. Co. of\nGrandale Kashington\nNo. 1867\n' + \
        #       'Oct. 26 1930\nJULIAN A. STEYERMARK, COLLECTOR'
        gcv = ocr_row['gcv']
        # gcv = 'FLORA OF MISSOURI\nAsplenium pinnatifidum\nOn north exposure, in crevices\n' + \
        #       'Hughes int., 4 miles 8.tt. of\nFrondale, Hashington Co.\nNo. 1867\nOct. 26 1930\n' + \
        #       'JULIAN A. STEYERMARK, COLLECTOR'

        new_row_for_analysis = {('ground_truth', 'barcode'): barcode, ('aws', 'text'): aws, ('gcv', 'text'): gcv}
        analysis = analysis.append(new_row_for_analysis, ignore_index=True)
    return analysis


def add_ground_truth_text(analysis: pd.DataFrame, filepath=None) -> pd.DataFrame:
    # Ground truth from the following extracted fields, \n separated:
    # scientificName + scientificNameAuthorship, recordNumber **ADDED "No." **, verbatimEventDate, habitat,
    # stateProvince, county **ADDED "Co."**, locality, verbatimElevation
    ground_truth = 'Asplenium pinnatifidum Nutt.\nNo. 1867\nOct. 26 1930\nOn north exposure, in crevices of granite\n' + \
                   'Missouri\nWashington Co.\nNear summit of Hughes Mountain, 4 miles SW of Irondale\n\n'.strip()
    occur_data = pd.read_csv(filepath)
    bad_query_indices = []
    for idx, one_line in analysis.iterrows():
        current_barcode = one_line['ground_truth']['barcode']
        occur_row = occur_data[occur_data['catalogNumber'] == current_barcode].reset_index()
        if occur_row.shape[0] > 1:
            occur_row = occur_row.loc[0, :] # select only the first row
        if occur_row.shape[0] == 1:
            ground_truth_string = ''
            data_to_add = [occur_row.at[0, 'scientificName'],
                           occur_row.at[0, 'scientificNameAuthorship'],
                           occur_row.at[0, 'recordNumber'],
                           occur_row.at[0,'verbatimEventDate'],
                           occur_row.at[0, 'habitat'],
                           occur_row.at[0, 'stateProvince'],
                           occur_row.at[0, 'county'],
                           occur_row.at[0, 'locality'],
                           occur_row.at[0, 'verbatimElevation']
                           ]
            for data in data_to_add:
                if not pd.isna(data):
                    ground_truth_string += data + '\n'
            analysis.at[idx, ('ground_truth', 'text')] = ground_truth_string
        else:
            print('Warning! No occurrence record found for barcode %s. Removing from query list.' % current_barcode)
            bad_query_indices.append(idx)
    if bad_query_indices:
        analysis = analysis.drop(index=bad_query_indices)
    return analysis


def preprocess_text(word_tokens: list):
    stop_words = set(stopwords.words('english'))
    removed_words = []
    filtered_words = []
    for w in word_tokens:
        if w.lower() in stop_words:
            removed_words.append(w)
        else:
            filtered_words.append(w)

    for idx, w in enumerate(filtered_words):
        if len(w) < 2:
            short = filtered_words.pop(idx)
            removed_words.append(short)
    print('Tokens excluded: %s' % str(removed_words))
    return filtered_words


def fuzzy_match_with_token_list(search_word: str, token_list: list) -> (list, int):
    fuzz_ratio = dict()
    for word in token_list:
        ratio = fuzz.ratio(search_word.lower(), word.lower())
        if ratio in fuzz_ratio.keys():
            fuzz_ratio[ratio].append(word)
        else:
            fuzz_ratio[ratio] = [word]
    fuzz_ratio = sorted(fuzz_ratio.items(), reverse=True)
    best_match = fuzz_ratio[0]
    best_ratio = best_match[0]
    best_matches_list = best_match[1]
    return best_matches_list, best_ratio


def generate_score(service_name: str, match_results: list) -> float:
    perfect_matches = [word[0][0] for word in match_results if word[1] == 100]
    near_matches = [word[0][0] for word in match_results if 60 < word[1] < 100]
    num_of_words = len(match_results)

    accuracy_score = (len(perfect_matches) + len(near_matches) / 2) / num_of_words

    print('Score for %s service: perfect = %i, near match = %i, score = %.2f%%' %
          (service_name, len(perfect_matches), len(near_matches), accuracy_score * 100))
    if len(perfect_matches) < 10:
        print('%s perfect matches: %s' % (service_name, str(perfect_matches)))
    if len(near_matches) < 10:
        print('%s near matches: %s' % (service_name, str(near_matches)))
    print()
    return accuracy_score


if __name__ == '__main__':
    assert len(sys.argv) > 3, 'Provide 2 arguments: filepath for 1 occurrence' + \
                              ' (can be occurrence_with_images file), ' + \
                              'and filepath for 1 CSV file with the headers "barcode", "aws", and "gcv" to compare.'
    occur = sys.argv[1]
    ocr = sys.argv[2]
    main(occur, ocr)
