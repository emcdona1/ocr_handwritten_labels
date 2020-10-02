import os, io
import pandas as pd

from AlgorithmicMethods import getPolygonAreaByTouples

def getWordProperties(index, text, full_text_annotation,minimumConfidence):
    found = False
    tupleVertices=centroid=area=conf=y_list =None,
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
        centroid= (sum(x_list)/len(x_list), sum(y_list)/len(y_list ))
        area = getPolygonAreaByTouples(tupleVertices)
    return tupleVertices,y_list,centroid,area, conf, charsAboveMinimumConfidence

def InitializeDataFromImage(root,vision):
    with io.open(root.imagePath, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    # response = client.text_detection(image=image)
    response = root.client.document_text_detection(image=image)
    df = pd.DataFrame(columns=['index',
                               'description',
                               'suggestedDescription',
                               'replacement',
                               'isIncorrectWord',
                               'color',
                               'centroid',
                               'tupleVertices',
                               'y_list',
                               'confidence',
                               'charsAboveMinimumConfidence',
                               'area',
                               'polygon',
                               'canvas'])
    index=0
    texts = response.text_annotations
    for text in texts:
        tupleVertices,y_list,centroid,area, conf, charsAboveMinimumConfidence = getWordProperties(index, text, response.full_text_annotation,root.minimumConfidence)
        df = df.append(
            dict(
                index=index,#can be used to ignore the word, if set to -1 in future
                description=text.description,#ocr detected word
                suggestedDescription=[],#later to be corrected if needed
                replacement="",#replacement by bert or manual
                isIncorrectWord = False,#ocr is not matching with bert or manual
                color="green",#red: ocr<>bert, yellow: manual entry, green replacement=OCR
                centroid = centroid,#we would need this to serialize alogrithm
                tupleVertices = tupleVertices,#for gui
                confidence=conf,#confidence
                charsAboveMinimumConfidence=charsAboveMinimumConfidence,
                area=area,#area covered by the word, needed to sort
                polygon=None,#for the gui placeholder
                canvas=None,#for the gui placeholder
                y_list=y_list
            ),
            ignore_index=True
        )
        index=index+1

    root.df=df
