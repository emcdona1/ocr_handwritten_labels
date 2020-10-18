import nltk
import torch
from pytorch_pretrained_bert import BertTokenizer, BertForMaskedLM
from difflib import SequenceMatcher
import re
from transformers import AutoTokenizer, AutoModelWithLMHead, pipeline

from getWordsInformation import getDescriptionFromDataBlocks


def applyCorrection(sdb):
    return ""
    maskedTextStream = getDescriptionFromDataBlocks("MASKED", sdb)

    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

    model = AutoModelWithLMHead.from_pretrained("bert-base-uncased")

    unmasker = pipeline('fill-mask', model='bert-base-uncased')
    result=unmasker(maskedTextStream)
    print(result)


def applyCorrection2(dfs):

    maskedTextStream=getDescriptionFromDataBlocks("MASKED", dfs)
    #print (maskedTextStream)

    # Load, train and predict using pre-trained model
    #(bert-base-uncased, bert-large-uncased, bert-base-cased, bert-large-cased,
    # bert-base-multilingual-uncased, bert-base-multilingual-cased, bert-base-chinese).



    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    tokenized_text = tokenizer.tokenize(maskedTextStream)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    MASKIDS = [i for i, e in enumerate(tokenized_text) if e == '[MASK]']
    # Create the segments tensors
    segs = [i for i, e in enumerate(tokenized_text) if e == "."]
    segments_ids = []
    prev = -1
    for k, s in enumerate(segs):
        segments_ids = segments_ids + [k] * (s - prev)
        prev = s
    segments_ids = segments_ids + [len(segs)] * (len(tokenized_text) - len(segments_ids))

    segments_tensors = torch.tensor([segments_ids])

    # prepare Torch inputs
    tokens_tensor = torch.tensor([indexed_tokens])
    # Load pre-trained model
    model = BertForMaskedLM.from_pretrained('bert-large-uncased')
    # Predict all tokens
    with torch.no_grad():
        predictions = model(tokens_tensor, segments_tensors)

    predict_wordUsingBert(dfs,predictions, MASKIDS, tokenizer, maskedTextStream)

    return ""


# cleanup text
def replaceShortForm(text):
    rep = {'\n': ' ', '\\': ' ', '\"': '"', '-': ' ', '"': ' " ',
           '"': ' " ', '"': ' " ', ',': ' , ', '.': ' . ', '!': ' ! ',
           '?': ' ? ', "n't": " not", "'ll": " will", '*': ' * ',
           '(': ' ( ', ')': ' ) ', "s'": "s '"}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text


def get_personslist(text):
    personslist = []
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if isinstance(chunk, nltk.tree.Tree) and chunk.label() == 'PERSON':
                personslist.insert(0, (chunk.leaves()[0][0]))
    return list(set(personslist))



#Predict words for mask using BERT;
#refine prediction by matching with proposals from SpellChecker
def predict_wordUsingBert(dfs,predictions, MASKIDS, tokenizer, maskedTextStream):
    i=0
    for index, w in dfs.iterrows():
        if w['index']>0:
            if w['description'] not in w['suggestedDescription']:
                w['suggestedDescription'].append(w['description']) #make sure OCR is listed in drop down
            if w['isIncorrectWord']:
                preds = torch.topk(predictions[0, MASKIDS[i]], k=50)
                i+=1
                indices = preds.indices.tolist()
                list1 = tokenizer.convert_ids_to_tokens(indices)
                simmax = 0
                predicted_token = ''
                for word1 in list1:
                    for word2 in w['suggestedDescription']:
                        s = SequenceMatcher(None, word1, word2).ratio()
                        if s is not None and s > simmax:
                            simmax = s
                            predicted_token = word1
                w['replacement'] = predicted_token