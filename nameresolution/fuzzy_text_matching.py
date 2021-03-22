import pandas as pd
import os
import requests
from zipfile import ZipFile
from fuzzywuzzy import fuzz
import copy


class TextMatcherTemplate:
    """ Stores a DataFrame and the name of the column containing the desired reference material,
    which can then be compared to any desired search string(s). """
    def __init__(self):
        self.expert_file = pd.DataFrame()
        self.reference_column = ''
        self.reference_id = ''
        self.load_expert_file()
        self.top_match_results = pd.DataFrame(columns=['search_query', 'best_matches', 'best_match_ratio'])

    def load_expert_file(self) -> None:
        raise NotImplementedError()

    def process_query_list(self, list_of_strings: list) -> None:
        """ Wrapper of find_best_match_for_query, which will find best matches for a list of string queries. """
        for one_string in list_of_strings:
            print('Finding matches for %s' % one_string)
            self.find_best_matches_for_query(one_string)

    def find_best_matches_for_query(self, search_query: str):
        """ Search all strings in the reference_column of expert_file and find the best match(es) for the search_query,
        using fuzzy matching ratios. Best match(es) are stored in the top_match_result attribute."""
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
        """ For a given search_query, calculate the fuzzy match ratio for all items in the reference_column of
        expert_file, and return a dictionary of the results, where key is the ratio (0-100) and value is a list
        of strings with that match ratio."""
        fuzz_ratio = dict()
        for expert_name_entry in self.expert_file[self.reference_column]:
            ratio = fuzz.ratio(search_query.lower(), expert_name_entry.lower())
            if ratio in fuzz_ratio.keys():
                fuzz_ratio[ratio].append(expert_name_entry)
            else:
                fuzz_ratio[ratio] = [expert_name_entry]
        return fuzz_ratio

    def save_best_match_results(self, original_filename: str):
        """ Save the contents of top_match_results to a CSV file. """
        filename = os.path.basename(original_filename).split('.')[0] + '-match_results.csv'
        self.top_match_results.to_csv(os.path.join('file_resources', filename), index=False)
        print('Matching results saved as %s' % filename)


class TaxonMatcher(TextMatcherTemplate):
    def load_expert_file(self):
        """ Given the TSV file from World Flora Online, import the file and remove all non-species.
                Sets the value for expert_file and reference_column."""
        file_path = 'file_resources' + os.path.sep + 'classification.tsv'
        if not os.path.exists(file_path):
            file_path = self.download_classification_file()
        classifications = pd.read_csv(file_path, sep='\t',
                                      usecols=['taxonID', 'scientificName', 'taxonRank', 'taxonomicStatus',
                                               'genus', 'specificEpithet', 'acceptedNameUsageID'],
                                      dtype={
                                          'specificEpithet': 'string'})  # unclear why I need to specify, but fixes it
        classifications = classifications[classifications.taxonRank == 'SPECIES']
        del classifications['taxonRank']
        self.expert_file = classifications
        self.reference_column = 'scientificName'
        self.reference_id = 'taxonID'

    def download_classification_file(self) -> str:
        """ If not downloaded, this downloads latest World Flora Online backbone and extracts the classification file
        (*.txt, but is tab-separated).  Returns relative file path of classification.tsv. """
        world_flora_online_url = 'http://104.198.143.165/files/WFO_Backbone/_WFOCompleteBackbone/WFO_Backbone.zip'
        wfo_backbone = requests.get(world_flora_online_url)
        zip_path = 'file_resources' + os.path.sep + 'WFO_Backbone.zip'
        with open(zip_path, 'wb') as f:
            f.write(wfo_backbone.content)

        with ZipFile(zip_path, 'r') as zipped_file:
            zipped_file.extract('classification.txt', path='file_resources')
        os.remove(zip_path)
        classification_path = 'file_resources' + os.path.sep + 'classification.tsv'
        os.rename('file_resources' + os.path.sep + 'classification.txt', classification_path)

        return classification_path

    def resolve_synonyms(self) -> pd.Series:
        synonym_matches = pd.DataFrame()
        synonym_matches[['search_query', 'best_matches']] = \
            copy.deepcopy(self.top_match_results[['search_query', 'best_matches']])
        synonym_matches['accepted_name'] = None
        for idx, row in synonym_matches.iterrows():
            # todo : only looking at the first one for now
            name_to_match = row['best_matches'][0]
        return pd.Series()
