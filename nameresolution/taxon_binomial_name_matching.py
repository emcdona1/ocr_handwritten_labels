import sys
from nameresolution.fuzzy_text_matching import TaxonMatcher
from utilities.data_loader import load_list_from_txt


def main():
    taxon_matcher = TaxonMatcher()
    list_of_queries: list = load_list_from_txt(query_filename)
    # list_of_queries = ['Adiantum pedatum', 'Isoeter engelmanni']  # [0] is exact match, [1] is fuzzy
    taxon_matcher.process_query_list(list_of_queries)
    taxon_matcher.save_results(query_filename)


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Please provide 1 argument for the file of name queries.'
    query_filename = sys.argv[1]
    main()
