import os
import re
import sys
import pandas as pd
from google.api_core.exceptions import ServiceUnavailable
from google.cloud import vision
from grpc._channel import _InactiveRpcError

client = None
barcode_regex = None


def SetGoogleCloudVisionClient(serviceAccountTokenPath):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = serviceAccountTokenPath
    global client
    client = vision.ImageAnnotatorClient()
    pass


def set_barcode_regex(regex):
    global barcode_regex
    barcode_regex = regex


def GetWordProperties(index, text, full_text_annotation):
    found = False
    t = ep = sp = confidence = ""
    if index > 0:  # skip the evaluation of first node
        for page in full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        if text.bounding_poly == word.bounding_box:
                            confidence = word.confidence
                            found = True
                            t = [(v.x, v.y) for v in word.bounding_box.vertices]
                            sp = ((t[0][0] + t[3][0]) // 2, (t[0][1] + t[3][1]) // 2)
                            ep = ((t[1][0] + t[2][0]) // 2, (t[1][1] + t[2][1]) // 2)

                            break;
                        if found:
                            break;
                    if found:
                        break;
                if found:
                    break;
            if found:
                break;
    return t, confidence, sp, ep


def GetInformationAsDataFrameFromImage(imageContent):
    global client
    image = vision.types.Image(content=imageContent)
    # response = client.text_detection(image=image)
    response = None
    try:
        response = client.document_text_detection(image=image)
    except _InactiveRpcError as err:
        print("_InactiveRpcError! {0}".format(err))
        print("retrying..!")
        client = vision.ImageAnnotatorClient()
        response = client.document_text_detection(image=image)
    except ServiceUnavailable as serr:
        print("ServiceUnavailable! {0}".format(serr))
        print("\nCheck the internet connection!")
        client = vision.ImageAnnotatorClient()
        response = client.document_text_detection(image=image)
    except Exception as error:
        print(f"{error} (Error Code:IDFI_002)")
        print("Unexpected error:", sys.exc_info()[0])
        raise

    # columns with boolean values, int values must be here
    dataFrame = pd.DataFrame(columns=['index', 'isIncorrectWord'])
    index = 0
    texts = response.text_annotations
    for text in texts:
        tupleVertices, confidence, sp, ep = GetWordProperties(index, text, response.full_text_annotation)
        dataFrame = dataFrame.append(
            dict(
                index=index,
                description=text.description,
                replacement=text.description,
                category="Unknown",
                tupleVertices=tupleVertices,
                sp=sp,
                ep=ep,
                suggestedDescription=[],
                polygon=None,
                canvas=None,
                confidence=confidence,
                isIncorrectWord=False,
                color="green"
            ),
            ignore_index=True
        )
        index = index + 1
    return dataFrame


def get_barcode_from_text(textData):
    barcode = ""
    try:
        match = re.search(barcode_regex, textData, re.MULTILINE)
        if match:
            barcode = match.group(0)

    except Exception as error:
        print(f"{error} (Error Code:IDFI_001)")
        print("Could not detect bar code using OCR Data and Regx")
        pass
    return barcode
