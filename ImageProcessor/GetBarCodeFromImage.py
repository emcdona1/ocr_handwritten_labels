
from pyzbar.pyzbar import decode
from PIL import Image

def GetBarCodeFromImage(imagePath):
    barcode=""
    img = Image.open(imagePath)
    result = decode(img)
    if len(result)>0:
        barcode= result[0]
    return barcode





#print(GetBarCodeFromImage("/Users/Keshab/Desktop/AllImages/172.png"))
