import nltk
from pytesseract import pytesseract


def tagText(data):
    tagTouples = nltk.word_tokenize(data)
    output = nltk.pos_tag(tagTouples)
    print(output)


def tesseractTest(imagePath):
    print("pytesseract.image_to_string")
    print(pytesseract.image_to_string(imagePath))
    print("pytesseract.image_to_boxes")
    print(pytesseract.image_to_boxes(imagePath))
    print("pytesseract.image_to_data")
    print(pytesseract.image_to_data(imagePath))
    print("pytesseract.image_to_osd")
    print(pytesseract.image_to_osd(imagePath))

def localTestExecution():
    tagText("I love this place")
    imagePath = "/Users/Keshab/Desktop/ProjectFiles/images/old/3_handWritten.png"
    tesseractTest(imagePath)

#localTestExecution()


