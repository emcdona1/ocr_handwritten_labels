import os
from fuzzywuzzy import fuzz
import pandas as pd
import sys


def main():
    all_binomials = load_names()
    list_of_queries = load_search_queries()
    results = pd.DataFrame(columns=['search_query', 'best_matches', 'best_match_ratio'])
    for one_name in list_of_queries:
        print('Finding matches for %s' % one_name)
        fuzz_ratio = generate_ratios(one_name, all_binomials)
        best_ratio, best_matches = find_top_matches(fuzz_ratio)
        one_name_results = {'search_query': one_name,
                            'best_matches': best_matches,
                            'best_match_ratio': best_ratio}
        results = results.append(one_name_results, ignore_index=True)

    results.to_csv('best_binomial_matches.csv', index=False)


def load_names() -> list:
    names = list()
    with open(file_of_all_binomial_names, 'r') as f:
        lines = f.readlines()
        for a_line in lines:
            a_line = a_line.strip().lower()
            names.append(a_line)
    return names


def load_search_queries() -> list:
    list_of_queries = list()
    with open(file_of_names_to_match, 'r') as f:
        lines = f.readlines()
        for name in lines:
            name = name.strip()
            list_of_queries.append(name)
    return list_of_queries


def generate_ratios(search_query: str, names: list) -> dict:
    search_query_lower = search_query.lower()
    fuzz_ratio = dict()
    for genus_species in names:
        ratio = fuzz.ratio(search_query_lower, genus_species)
        add_ratio_to_list(fuzz_ratio, genus_species, ratio)
    return fuzz_ratio


def add_ratio_to_list(fuzz_ratio: dict, genus_species: str, ratio: int) -> None:
    if ratio in fuzz_ratio.keys():
        fuzz_ratio[ratio].append(genus_species)
    else:
        fuzz_ratio[ratio] = [genus_species]


def find_top_matches(fuzz_ratio: dict) -> (float, list):
    ordered_ratios = sorted(fuzz_ratio.items(), reverse=True)
    best_match = ordered_ratios[0]
    best_ratio_achieved = best_match[0]
    list_of_best_matches = best_match[1]
    return best_ratio_achieved, list_of_best_matches


if __name__ == '__main__':
    # Example: file_of_all_binomial_names = 'file_resources' + os.path.sep + 'list_of_scientific_names.txt'
    assert len(sys.argv) > 1, 'Provide an argument of the file (txt) to be read.'
    file_of_all_binomial_names = sys.argv[1]
    file_of_names_to_match = 'file_resources' + os.path.sep + 'list_of_gcv_identified_names.txt'
    main()
