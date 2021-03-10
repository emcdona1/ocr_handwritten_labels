import sys
import pandas as pd
import os
import requests
from zipfile import ZipFile
from fuzzywuzzy import fuzz

WORLD_FLORA_ONLINE_URL = 'http://104.198.143.165/files/WFO_Backbone/_WFOCompleteBackbone/WFO_Backbone.zip'


class NameMatcher:
    def __init__(self):
        classification_file_path: str = self.download_classification_file_if_needed()
        self.taxonomic_names: pd.DataFrame = self.load_classification_file(classification_file_path)
        self.top_match_results = pd.DataFrame(columns=['search_query', 'best_matches', 'best_match_ratio'])

    def download_classification_file_if_needed(self) -> str:
        """ If not downloaded, this downloads latest World Flora Online backbone and extracts the classification file
        (*.txt, but is tab-separated).  Returns relative file path of classification.tsv. """
        # todo: if a new version comes out, it wouldn't update....
        classification_path = 'file_resources' + os.path.sep + 'classification.tsv'
        if not os.path.exists(classification_path):
            wfo_backbone = requests.get(WORLD_FLORA_ONLINE_URL)
            zip_path = 'file_resources' + os.path.sep + 'WFO_Backbone.zip'
            with open(zip_path, 'wb') as f:
                f.write(wfo_backbone.content)

            with ZipFile(zip_path, 'r') as zipped_file:
                zipped_file.extract('classification.txt', path='file_resources')
            os.remove(zip_path)
            classification_path = 'file_resources' + os.path.sep + 'classification.tsv'
            os.rename('file_resources' + os.path.sep + 'classification.txt', classification_path)

        return classification_path

    def load_classification_file(self, file_path: str) -> pd.DataFrame:
        """ Given the TSV file from World Flora Online, import the file and remove all non-species.
        Returns a DataFrame with only the taxonomic name/status information."""
        classifications = pd.read_csv(file_path, sep='\t',
                                      usecols=['taxonID', 'scientificName', 'taxonRank', 'taxonomicStatus',
                                               'genus', 'specificEpithet', 'acceptedNameUsageID'],
                                      dtype={
                                          'specificEpithet': 'string'})  # unclear why I need to specify, but fixes it
        classifications = classifications[classifications.taxonRank == 'SPECIES']
        del classifications['taxonRank']
        # todo: save this filtered classifications file for quicker future reference
        return classifications

    def find_best_matches_for_query(self, search_query: str):
        fuzz_ratio = self.generate_ratios(search_query)
        fuzz_ratio = sorted(fuzz_ratio.items(), reverse=True)
        best_match = fuzz_ratio[0]

        best_ratio = best_match[0]
        best_matches_list = best_match[1]
        one_name_results = {'search_query': search_query,
                            'best_matches': best_matches_list,
                            'best_match_ratio': best_ratio}
        self.top_match_results = self.top_match_results.append(one_name_results, ignore_index=True)

    def generate_ratios(self, search_query: str) -> dict:
        fuzz_ratio = dict()
        for genus_species in self.taxonomic_names['scientificName']:
            ratio = fuzz.ratio(search_query.lower(), genus_species.lower())
            if ratio in fuzz_ratio.keys():
                fuzz_ratio[ratio].append(genus_species)
            else:
                fuzz_ratio[ratio] = [genus_species]
        return fuzz_ratio

    def save_best_match_results(self, original_filename: str):
        filename = os.path.basename(original_filename).split('.')[0] + '-name_match_results.csv'
        self.top_match_results.to_csv(filename, index=False)
        print('Name matching results saved as %s' % filename)


def main():
    matcher = NameMatcher()
    list_of_queries: list = load_query_file()
    # todo: remove this temp query
    list_of_queries = ['Adiantum pedatum', 'Isoeter engelmanni']  # [0] is exact match, [1] is fuzzy

    for one_name in list_of_queries:
        print('Finding matches for %s' % one_name)
        matcher.find_best_matches_for_query(one_name)
    matcher.save_best_match_results(query_filename)


def load_query_file() -> list:
    list_of_queries = list()
    with open(query_filename, 'r') as f:
        lines = f.readlines()
        for name in lines:
            name = name.strip()
            list_of_queries.append(name)
    return list_of_queries


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Please provide 1 argument for the file of name queries.'
    query_filename = sys.argv[1]
    main()
