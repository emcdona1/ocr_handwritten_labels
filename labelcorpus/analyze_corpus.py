import os
import sys
import nltk


def main(corpus_location: str):
    docs = os.listdir(corpus_location)
    raw_text_list = []
    for file in docs:
        with open(os.path.join(corpus_location, file), 'r') as f:
            raw_text = f.read()
        raw_text_list.append(raw_text)
    tokens = [nltk.wordpunct_tokenize(text) for text in raw_text_list]
    texts = [nltk.text.Text(each) for each in tokens]
    fdists = [nltk.FreqDist(t) for t in texts]
    pass


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Include 1 parameter for the folder containing the corpus files.'
    cor = sys.argv[1]
    main(cor)
