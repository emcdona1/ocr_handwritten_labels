import ImageProcessor.ImageProcessorDriver as ipd
import pandas as pd
global transcription_results
from ClassificationApp_GUI.ClassificationApp_root import ClassificationApp

def main():
    image_list_filename = 'image_list.txt'
    one_image = 'https://pteridoportal.org/imglib/fern/F/C0611/C0611253F_1591198805_web.jpg'
    # i don't understand what root is beyond the GUI, but he has it tied in so I have to use it for now
    c = ClassificationApp()
    global transcription_results
    transcription_results = pd.DataFrame([], columns=['filename', 'gcv_results', 'correction_results'])

    # args below:
    ## suggestEngine
    ## txt file name
    ## "minimum confidence" -- using his value of 1
    ## and False=don't search for the label)
    ipd.ProcessImagesFromTheUrlsInTheTextFile(c.suggest_engine, image_list_filename, 1, False)

    save_to_CSV()


def save_to_CSV():
    global transcription_results
    print(transcription_results.head(2))
    # todo: save the results to a file
    pass


if __name__ == '__main__':
    main()
