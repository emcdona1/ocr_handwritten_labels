import string
from Levenshtein import editops
import pandas as pd
from copy import deepcopy
from typing import Dict, Tuple, List
import regex


def main(comparisons: pd.DataFrame, min_threshold=2, diff_tolerance=6):
    aws_errors: Dict[Tuple[str, str], int] = dict()
    gcv_errors: Dict[Tuple[str, str], int] = dict()
    for idx, row in comparisons.iterrows():
        ground_truth_tokens = row['ground_truth']['filtered_tokens']
        aws_best_matches = row['aws']['fuzzy_match_list']
        gcv_best_matches = row['gcv']['fuzzy_match_list']
        for i in range(0, len(ground_truth_tokens)):
            process_changes(ground_truth_tokens[i], aws_best_matches[i][0][0], aws_errors)
            process_changes(ground_truth_tokens[i], gcv_best_matches[i][0][0], gcv_errors)
    print('==================AWS==================')
    output(aws_errors, min_threshold)
    print('\n\n==================GCV==================')
    output(gcv_errors, min_threshold)
    combined = combine(aws_errors, gcv_errors, min_threshold)
    print(combined)


def parse_fuzzy_string_to_list(aws_best_matches: str) -> List[Tuple[List[str], int]]:
    """ Parse the string from CSV file into a list of tuples. """
    items = aws_best_matches[2:-1] + ', '
    items = items.split('), (')
    items[-1] = items[-1][:-3]
    items = [(regex.split(r'\],[ ]{0,1}', item)[0], int(regex.split(r'\],[ ]{0,1}', item)[1])) for item in items]
    results = []
    for item in items:
        list_of_results = item[0].replace("['", '')[:-1]
        list_of_results = regex.split("',[ ]{0,1}'", list_of_results)
        results.append((list_of_results, item[1]))
    return results


def process_changes(start: str, end: str, errors: dict) -> None:
    changes = editops(start, end)
    for change in changes:
        orig = ''
        update = ''
        if change[0] == 'replace':
            orig = start[change[1]]
            update = end[change[2]]
        elif change[0] == 'insert':
            orig = '*'
            update = end[change[2]]
        elif change[0] == 'delete':
            orig = start[change[1]]
            update = '*'
        else:
            print('Error: change value is ' + str(change[0]))
        k = (orig, update)
        if k in errors.keys():
            errors[k] += 1
        else:
            errors[k] = 1


def output(results: dict, tolerance=4) -> None:
    sorted_keys = sorted(results, key=results.get, reverse=True)
    for k in sorted_keys:
        if k[0] not in (string.digits + string.punctuation + ' ') and \
                k[1] not in (string.digits + string.punctuation + ' ') and \
                results[k] > tolerance:
            print('Swap %s for %s - %i times' % (k[0], k[1], results[k]))


def combine(aws_errors: dict, gcv_errors: dict, min_threshold: int) -> pd.DataFrame:
    combined = pd.DataFrame(columns=['wrong', 'correct', 'aws_count', 'gcv_count'])
    gcv_errors_copy = deepcopy(gcv_errors)
    for k in aws_errors.keys():
        new_row = {'wrong': k[0], 'correct': k[1], 'aws_count': aws_errors[k], 'gcv_count': 0}
        if k in gcv_errors_copy:
            new_row['gcv_count'] = gcv_errors_copy.pop(k)
        new_row['difference'] = int(abs(new_row['gcv_count'] - new_row['aws_count']))
        excluded_characters = string.digits + string.punctuation + ' '
        if new_row['wrong'] not in string.digits + excluded_characters or new_row['correct'] not in excluded_characters:
            combined = combined.append(new_row, ignore_index=True)
    for k in gcv_errors_copy.keys():
        new_row = {'wrong': k[0], 'correct': k[1], 'aws_count': 0, 'gcv_count': gcv_errors[k]}
        new_row['difference'] = int(abs(new_row['aws_count'] - new_row['gcv_count']))
        combined = combined.append(new_row, ignore_index=True)

    combined = combined.query('(aws_count > %i or gcv_count > %i)' % (min_threshold, min_threshold))
    return combined
