import string
from Levenshtein import editops
import pandas as pd
from copy import deepcopy


def main(filename: str):
    aws_errors = dict()
    gcv_errors = dict()
    # keys are tuples (start, end), values are counts
    comparisons: pd.DataFrame = pd.read_csv(filename, header=[0,1])
    for idx, row in comparisons.iterrows():
        ground_truth_tokens: list = row['ground_truth']['filtered_tokens']
        aws_best_matches: list = row['aws']['fuzzy_match_list']
        gcv_best_matches: list = row['gcv']['fuzzy_match_list']
        for idx in range(len(ground_truth_tokens)):
            process_changes(ground_truth_tokens[idx], aws_best_matches[idx][0], aws_errors)
            process_changes(ground_truth_tokens[idx], gcv_best_matches[idx][0], gcv_errors)
    print('==================AWS==================')
    output(aws_errors, 4)
    print('\n\n==================GCV==================')
    output(gcv_errors, 4)
    combined = combine(aws_errors, gcv_errors, min_threshold=2, diff_tolerance=6)
    print(combined)


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


def output(results: dict, tolerance=2) -> None:
    sorted_keys = sorted(results, key=results.get, reverse=True)
    for k in sorted_keys:
        if k[0] not in (string.digits + string.punctuation + ' ') and \
                k[1] not in (string.digits + string.punctuation + ' ') and \
                results[k] > tolerance:
            print('Swap %s for %s - %i times' % (k[0], k[1], results[k]))


def combine(aws_errors: dict, gcv_errors: dict, min_threshold=2, diff_tolerance=2) -> pd.DataFrame:
    combined = pd.DataFrame(columns=['wrong', 'correct', 'aws_count', 'gcv_count'])
    gcv_errors = deepcopy(gcv_errors)
    for k in aws_errors.keys():
        row = {'wrong': k[0], 'correct': k[1], 'aws_count': aws_errors[k], 'gcv_count': 0}
        if k in gcv_errors:
            row['gcv_count'] = gcv_errors.pop(k)
        row['difference'] = int(abs(row['gcv_count'] - row['aws_count']))
        combined = combined.append(row, ignore_index=True)
    for k in gcv_errors.keys():
        row = {'wrong': k[0], 'correct': k[1], 'aws_count': 0, 'gcv_count': gcv_errors[k]}
        row['difference'] = int(abs(row['aws_count'] - row['gcv_count']))
        combined = combined.append(row, ignore_index=True)
    combined = combined.query('(aws_count > %i or gcv_count > %i) and (difference > %i)' %
                              (min_threshold, min_threshold, diff_tolerance))
    return combined

