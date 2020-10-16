import os, io
import sys

import pandas as pd
from google.api_core.exceptions import ServiceUnavailable
from google.cloud import vision
from grpc._channel import _InactiveRpcError

from algorithmicMethods import getPolygonAreaByTouples

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'serviceAccountToken.json'
client = vision.ImageAnnotatorClient()


def getWordProperties(index, text, full_text_annotation,minimumConfidence):
    found = False
    tupleVertices=centroid=area=conf=y_list=x_list =None,
    charsAboveMinimumConfidence=""
    if index>0:#skip the evaluation of first node
        for page in full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        if text.bounding_poly==word.bounding_box:
                            fullAnnotation=word
                            found = True
                            for symbol in word.symbols:
                                if symbol.confidence>minimumConfidence:
                                    charsAboveMinimumConfidence +=symbol.text
                                else:
                                    charsAboveMinimumConfidence=charsAboveMinimumConfidence+"?"
                            break;
                        if found:
                            break;
                    if found:
                        break;
                if found:
                    break;
            if found:
                break;
        #adding more information
        #if needed pass the fullAnnotation as well.print(fullAnnotation)
        conf=fullAnnotation.confidence
        tupleVertices=[(v.x,v.y) for v in fullAnnotation.bounding_box.vertices]
        x_list = [v.x for v in fullAnnotation.bounding_box.vertices]
        y_list = [v.y for v in fullAnnotation.bounding_box.vertices]
        #x_list=x_list.sort()
        #y_list=y_list.sort()
        #centroid= (sum(x_list)/len(x_list), sum(y_list)/len(y_list ))
        centroid = ((min(x_list)+max(x_list))/ 2, (min(y_list)+max(y_list)) / 2)
        area = getPolygonAreaByTouples(tupleVertices)
    return tupleVertices,x_list,y_list,centroid,area, conf, charsAboveMinimumConfidence

def initializeDataFromImage(imagePath,minimumConfidence):
    global client
    with io.open(imagePath, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    # response = client.text_detection(image=image)
    response=None
    try:
        response = client.document_text_detection(image=image)
    except _InactiveRpcError as err:
        print ("_InactiveRpcError! {0}".format(err))
        print("retrying..!")
        client=vision.ImageAnnotatorClient()
        response = client.document_text_detection(image=image)
    except ServiceUnavailable as serr:
        print("ServiceUnavailable! {0}".format(serr))
        print("\nCheck the internet connection!")
        client = vision.ImageAnnotatorClient()
        response = client.document_text_detection(image=image)

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    df = pd.DataFrame(columns=['index',
                               'description',
                               'suggestedDescription',
                               'suggestedLatinDescription',
                               'replacement',
                               'isIncorrectWord',
                               'color',
                               'centroid',
                               'tupleVertices',
                               'x_list',
                               'y_list',
                               'confidence',
                               'charsAboveMinimumConfidence',
                               'area',
                               'polygon',
                               'canvas',
                               'category'])
    index=0
    texts = response.text_annotations
    for text in texts:
        tupleVertices,x_list,y_list,centroid,area, conf, charsAboveMinimumConfidence = getWordProperties(index, text, response.full_text_annotation,minimumConfidence)
        df = df.append(
            dict(
                index=index,#can be used to ignore the word, if set to -1 in future
                description=text.description,#ocr detected word
                suggestedDescription=[],#later to be corrected if needed
                suggestedLatinDescription=[],#later to be corrected for latin words possibility
                replacement=text.description,#replacement by bert or manual, initially it is the samedf
                isIncorrectWord = False,#ocr is not matching with bert or manual
                color="green",#red: ocr<>bert, yellow: manual entry, green replacement=OCR
                centroid = centroid,#we would need this to serialize alogrithm
                tupleVertices = tupleVertices,#for gui
                confidence=conf,#confidence
                charsAboveMinimumConfidence=charsAboveMinimumConfidence,
                area=area,#area covered by the word, needed to sort
                polygon=None,#for the gui placeholder
                canvas=None,#for the gui placeholder
                category="Unknown",#for the classification of the word
                x_list=x_list,
                y_list=y_list
            ),
            ignore_index=True
        )
        index=index+1

    return df
