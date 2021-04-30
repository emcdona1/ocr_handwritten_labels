"""Compare OCR results to ground truth text, and provide a list of best-match-words (using NLTK fuzzy match ratio) and
a rough baseline comparison score [0, 100] for each OCR platform on each image."""
import string
import sys
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from fuzzywuzzy import fuzz
from utilities.dataloader import save_dataframe_as_csv


def main(occurrence_filepath: str) -> pd.DataFrame:
    """ Load, populate, and return a pd.DataFrame with OCR text and quality analysis. """
    occurrences = pd.read_csv(occurrence_filepath, encoding='ISO-8859-1')
    add_ground_truth_text(occurrences)
    separate_word_analysis = pd.DataFrame(columns=['barcode', 'word_number', 'ground_truth_token',
                                                   'aws_best_match_tokens', 'aws_best_match_score',
                                                   'gcv_best_match_tokens', 'gcv_best_match_score'])

    for idx, occur_row in occurrences.iterrows():
        if pd.isna(occur_row['awsOcrText']):
            aws_tokens = ['']  # this means that AWS didn't find anything...
        else:
            aws_tokens = word_tokenize(occur_row['awsOcrText'])
        if pd.isna(occur_row['gcvOcrText']):
            gcv_tokens = ['']  # this means that GCV didn't find anything...
        else:
            gcv_tokens = word_tokenize(occur_row['gcvOcrText'])
        aws_match_results = list()
        gcv_match_results = list()

        ground_truth_filtered_words: list = preprocess_text(occur_row['labelText'])
        for i, search_word in enumerate(ground_truth_filtered_words):
            aws_best_matches_list, aws_best_ratio = fuzzy_match_with_token_list(search_word, aws_tokens)
            gcv_best_matches_list, gcv_best_ratio = fuzzy_match_with_token_list(search_word, gcv_tokens)
            aws_match_results.append((aws_best_matches_list, aws_best_ratio))
            gcv_match_results.append((gcv_best_matches_list, gcv_best_ratio))
            swa_row = {'barcode': occur_row['catalogNumber'], 'word_number': i, 'ground_truth_token': search_word,
                       'aws_best_match_tokens': aws_best_matches_list, 'aws_best_match_score': aws_best_ratio,
                       'gcv_best_match_tokens': gcv_best_matches_list, 'gcv_best_match_score': gcv_best_ratio}
            separate_word_analysis = separate_word_analysis.append(swa_row, ignore_index=True)

        occurrences.at[idx, 'awsMatchingScore'] = generate_score(occurrences.at[idx, 'catalogNumber'],
                                                                 'aws', aws_match_results)
        occurrences.at[idx, 'gcvMatchingScore'] = generate_score(occurrences.at[idx, 'catalogNumber'],
                                                                 'gcv', gcv_match_results)
        print()

    filename = save_dataframe_as_csv('test_results', 'occurrence_with_ocr_scores', occurrences)
    print('%i row(s) processed, added, and saved to %s' % (occurrences.shape[0], filename))
    filename = save_dataframe_as_csv('test_results', 'compare_word_by_word', separate_word_analysis)
    print('Word-by-word analysis saved to %s' % filename)
    return occurrences


def add_ground_truth_text(occur_data: pd.DataFrame) -> None:
    # Ground truth from the following extracted fields, \n separated:
    # scientificName + scientificNameAuthorship, recordNumber **ADDED "No." **, verbatimEventDate, habitat,
    # stateProvince, county **ADDED "Co."**, locality, verbatimElevation
    for idx, one_line in occur_data.iterrows():
        ground_truth_string = ''
        data_to_add = [one_line['scientificName'], one_line['scientificNameAuthorship'], one_line['recordNumber'],
                       one_line['verbatimEventDate'], one_line['habitat'],
                       one_line['stateProvince'], one_line['county'], one_line['locality'],
                       one_line['verbatimElevation']
                       ]
        for data in data_to_add:
            if not pd.isna(data):
                ground_truth_string += data + '\n'
        occur_data.at[idx, 'labelText'] = ground_truth_string.strip()


def preprocess_text(text: str) -> list:
    word_tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    stopped_words = []
    filtered_words = []
    for w in word_tokens:
        if w.lower() in stop_words:
            stopped_words.append(w)
        else:
            filtered_words.append(w)
    filtered_words = [word for word in filtered_words if word not in string.punctuation]
    filtered_words = [word for word in filtered_words if len(word) >= 2]
    return filtered_words


def fuzzy_match_with_token_list(search_word: str, token_list: list) -> (list, int):
    if token_list == '':
        return [], 0

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


def generate_score(barcode: str, service_name: str, match_results: list) -> float:
    perfect_matches = [word[0][0] for word in match_results if word[1] == 100]
    near_matches = [word[0][0] for word in match_results if 60 < word[1] < 100]
    num_of_words = len(match_results)

    accuracy_score = (len(perfect_matches) + len(near_matches) / 2) / num_of_words

    print('Score for %s on service %s: perfect = %i, near match = %i, score = %.2f%%' %
          (barcode, service_name, len(perfect_matches), len(near_matches), accuracy_score * 100))
    return accuracy_score


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Provide 1 argument: filepath for the occurrence_with_ocr file.'

    occur = sys.argv[1]
    main(occur)
