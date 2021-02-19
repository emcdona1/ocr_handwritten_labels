import os
from fuzzywuzzy import fuzz


def main():
    names = load_names()
    list_of_queries = load_search_queries()
    for search_query in list_of_queries:
        print('Finding matches for %s' % search_query)
        search_query_lower = search_query.lower()
        fuzz_ratio = generate_ratios(search_query_lower, names)
        present_results(fuzz_ratio)


def load_search_queries() -> list:
    list_of_queries = list()
    with open('list_of_gcv_names.txt', 'r') as f:
        lines = f.readlines()
        for name in lines:
            name = name.strip()
            list_of_queries.append(name)
    # list_of_queries = ['Cystopteria byulbutere']
    return list_of_queries


def generate_ratios(search_query_lower: str, names: list) -> dict:
    fuzz_ratio = dict()
    for genus_species in names:
        ratio = fuzz.ratio(search_query_lower, genus_species)
        add_ratio_to_list(fuzz_ratio, genus_species, ratio)
    return fuzz_ratio


def load_names() -> list:
    names = list()
    with open('InputResources' + os.path.sep + 'genusspecies_data.txt', 'r') as f:
        lines = f.readlines()
        for a_line in lines:
            a_line = a_line.strip().lower()
            names.append(a_line)
    return names


def add_ratio_to_list(fuzz_ratio: dict, genus_species: str, ratio: int) -> None:
    if ratio in fuzz_ratio.keys():
        fuzz_ratio[ratio].append(genus_species)
    else:
        fuzz_ratio[ratio] = [genus_species]


def present_results(fuzz_ratio: dict) -> None:
    ordered_ratios = sorted(fuzz_ratio.items(), reverse=True)
    best_match = ordered_ratios[0]
    best_ratio = best_match[0]
    best_matches_list = ''
    for each in best_match[1]:
        best_matches_list += each + ', '
    print('Best matches with a ratio of %i: [%s]' % (best_ratio, best_matches_list))


if __name__ == '__main__':
    main()