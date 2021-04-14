import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys


def main(csv_filepath: str):
    base_url = 'https://www.pteridoportal.org'
    new_col_name = 'img_url'
    occurrences = pd.read_csv(csv_filepath, encoding='ISO-8859-1')
    occurrences[new_col_name] = ''
    for idx, row in occurrences.iterrows():
        url = row['references']
        page = requests.get(url)
        if page.status_code == 200:
            full_link = extract_image_url(base_url, page)
        else:
            full_link = 'file error html status: %i' % page.status_code
        occurrences.at[idx, new_col_name] = full_link
        print('%i/%i processed' % ((idx + 1), occurrences.shape[0]))
    return occurrences


def extract_image_url(base_url: str, page: requests.models.Response) -> str:
    soup = BeautifulSoup(page.content, 'lxml')
    try:
        image_div = soup.find('div', {'class': 'imgDiv'})
        # image_link = image_div.find('a').attrs['href']
        large_image_url_div = image_div.findAll('div')[-1]
        image_url = large_image_url_div.find('a').attrs['href']
        if 'http' not in image_url:
            image_url = base_url + image_url
    except AttributeError as e:
        image_url = 'None'
    return image_url


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Provide an argument of the file (CSV) to be read ' + \
                              '(an occurrence download from the Fern Portal, with ISO-8859-1 encoding).'
    filepath = sys.argv[1]
    occurrences_new_df = main(filepath)
    occurrences_new_df.to_csv(filepath[0:-4] + '-updated.csv', encoding='ISO-8859-1')
