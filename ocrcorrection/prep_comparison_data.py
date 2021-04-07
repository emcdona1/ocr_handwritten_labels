"""Provide a baseline comparison score [0, 100] between OCR systems, using NLTK."""
import sys
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from fuzzywuzzy import fuzz


def main():
    """ Load, populate, and return a pd.DataFrame with OCR text and quality analysis. """
    mi = pd.MultiIndex.from_arrays(
        [['ground_truth', 'ground_truth', 'ground_truth', 'aws', 'aws', 'aws', 'gcv', 'gcv', 'gcv'],
         ['barcode', 'text', 'filtered_tokens'] + ['text', 'fuzzy_match_list', 'score']*2],
        names=('dataset', 'item'))
    ocr = pd.DataFrame(columns=mi)
    load_ocr_from_file(ocr)
    add_ground_truth_text(ocr)

    for idx, ocr_row in ocr.iterrows():
        aws_tokens = word_tokenize(ocr_row['aws']['text'])
        gcv_tokens = word_tokenize(ocr_row['gcv']['text'])
        aws_match_results = list()
        gcv_match_results = list()
        ground_truth_filtered_words = preprocess_text(word_tokenize(ocr_row['ground_truth']['text']))
        ocr.at[[idx], ('ground_truth', 'filtered_tokens')] = pd.Series([ground_truth_filtered_words], index=[idx])
        for search_word in ocr.at[idx, ('ground_truth', 'filtered_tokens')]:
            aws_best_matches_list, aws_best_ratio = fuzzy_match_with_token_list(search_word, aws_tokens)
            gcv_best_matches_list, gcv_best_ratio = fuzzy_match_with_token_list(search_word, gcv_tokens)
            aws_match_results.append((aws_best_matches_list, aws_best_ratio))
            gcv_match_results.append((gcv_best_matches_list, gcv_best_ratio))

        ocr.at[idx, ('aws', 'score')] = generate_score('aws', aws_match_results)
        ocr.at[idx, ('gcv', 'score')] = generate_score('gcv', gcv_match_results)
        ocr.at[[idx], ('aws', 'fuzzy_match_list')] = pd.Series([aws_match_results], index=[idx])
        ocr.at[[idx], ('gcv', 'fuzzy_match_list')] = pd.Series([gcv_match_results], index=[idx])
    return ocr


def load_ocr_from_file(ocr: pd.DataFrame, filepath=None) -> None:
    """ Loads in OCR transcriptions and ground truth text from a file as a pd.DataFrame."""
    for i in range(0, 1):  # todo: load from file
        aws = 'FLORA OF MISSOURI\nasplenium pinnatifidum nutt\non north exposure in crevices\n' + \
              'of granite, mear summit of\nstughes mt., 4 miles S.rt. Co. of\nGrandale Kashington\nNo. 1867\n' + \
              'Oct. 26 1930\nJULIAN A. STEYERMARK, COLLECTOR'

        gcv = 'FLORA OF MISSOURI\nAsplenium pinnatifidum\nOn north exposure, in crevices\n' + \
              'Hughes int., 4 miles 8.tt. of\nFrondale, Hashington Co.\nNo. 1867\nOct. 26 1930\n' + \
              'JULIAN A. STEYERMARK, COLLECTOR'

        ocr_row = {('ground_truth', 'barcode'): 'C0601155F', ('aws', 'text'): aws, ('gcv', 'text'): gcv}
        ocr = ocr.append(ocr_row, ignore_index=True)


def add_ground_truth_text(ocr: pd.DataFrame, filepath=None) -> None:
    # Ground truth from the following extracted fields, \n separated:
    # scientificName + scientificNameAuthorship, recordNumber **ADDED "No." **, verbatimEventDate, habitat,
    # stateProvince, county **ADDED "Co."**, locality, verbatimElevation
    ground_truth = 'Asplenium pinnatifidum Nutt.\nNo. 1867\nOct. 26 1930\nOn north exposure, in crevices of granite\n' + \
                   'Missouri\nWashington Co.\nNear summit of Hughes Mountain, 4 miles SW of Irondale\n\n'.strip()
    occur = pd.read_csv('1617207806-occur.csv')
    for idx, one_line in ocr.iterrows():
        row = occur[occur['catalogNumber'] == one_line['ground_truth']['barcode']]
        ground_truth_string = row['scientificName'][0] + '\n' + row['scientificNameAuthorship'][0] + '\n' + \
                              str(row['recordNumber'][0]) + '\n' + row['verbatimEventDate'][0] + '\n' + \
                              row['habitat'][0] + '\n' + row['stateProvince'][0] + '\n' + row['county'][0] + \
                              '\n' + row['locality'][0]
        if not pd.isna(row['verbatimElevation'][0]):
            ground_truth_string = ground_truth_string + '\n' + str(row['verbatimElevation'][0])
        ocr.at[idx, ('ground_truth', 'text')] = ground_truth_string


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
    # assert len(sys.argv) > 4, 'Provide 3 arguments: one ground truth file, and 2 files of OCR data to compare.'
    # ground_truth_file = sys.argv[1]
    # ocr_1_file = sys.argv[2]
    # ocr_2_file = sys.argv[3]
    main()
