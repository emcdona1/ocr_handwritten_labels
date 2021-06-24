import os
import sys
import pandas as pd


def main(occurrence_filepath: str, corpus_name: str):
    corpus_filepath = os.path.join('corpora', corpus_name)
    if not os.path.exists(corpus_filepath):
        os.makedirs(corpus_filepath)

    occurrence = pd.read_csv(occurrence_filepath, encoding='UTF-8')
    target_columns = ['scientificName', 'scientificNameAuthorship', 'recordNumber', 'verbatimEventDate',
                      'habitat', 'stateProvince', 'county', 'locality', 'verbatimElevation']
    for column_name in target_columns:
        target_column = occurrence[column_name]
        with open(os.path.join(corpus_filepath, column_name + '.txt'), 'w', encoding='utf8') as f:
            for row in target_column:
                if not pd.isna(row):
                    f.write(str(row) + '\n')


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Include 2 arguments: 1) pointing to an occurrence file (CSV), and ' +\
            '2) the name of the new corpus to generate.'
    occur = sys.argv[1]
    folder = sys.argv[2]
    main(occur, folder)
