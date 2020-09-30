#this file is to only test the quality of the coversion between google and tesseract
#from PIL.Image import Image
import pytesseract


def printTessaractOutputForImage(imagePath):
    # Simple image to string
   # print(pytesseract.image_to_string(Image.open(imagePath)))
    print("After tesseract OCR:")
    print(pytesseract.image_to_string(imagePath))

    #print(pytesseract.image_to_boxes(Image.open('test.png')))


    #print(pytesseract.image_to_data(Image.open('test.png')))


    #print(pytesseract.image_to_osd(Image.open('test.png')))
    #print(pytesseract.image_to_string('images.txt'))


