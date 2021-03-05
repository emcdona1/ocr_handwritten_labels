import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys


def main():
    base_url = 'https://www.pteridoportal.org'
    new_col_name = 'img_url'
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


def extract_image_url(base_url: str, page: requests.models.Response) -> str:
    soup = BeautifulSoup(page.content, 'lxml')
    try:
        image_div = soup.find('div', {'class': 'imgDiv'})
        image_link = image_div.find('a').attrs['href']
        if 'http' not in image_link:
            image_link = base_url + image_link
    except AttributeError as e:
        image_link = 'No image; specimen is likely protected.'
    return image_link


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'Provide an argument of the file (CSV) to be read.'
    csv_filename = sys.argv[1]
    occurrences = pd.read_csv(csv_filename, encoding='ISO-8859-1')
    main()
    occurrences.to_csv(csv_filename[0:-4] + 'updated.csv', encoding='ISO-8859-1')
