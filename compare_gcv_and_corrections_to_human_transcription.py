import ImageProcessor.ImageProcessorDriver as ipd
import pandas as pd
# global transcription_results
from ClassificationApp_GUI.ClassificationApp_root import ClassificationApp


def main():
    image_list_filename = 'image_list.txt'
    one_image = 'https://pteridoportal.org/imglib/fern/F/C0611/C0611253F_1591198805_web.jpg'
    # i don't understand what root is beyond the GUI, but he has it tied in so I have to use it for now
    c = ClassificationApp()
    # global transcription_results
    transcription_results = pd.DataFrame([], columns=['filename', 'gcv_results', 'correction_results'])
    transcription_results = process_one_image(c, one_image, transcription_results)
    # transcription_results = process_list_of_images(c, image_list_filename, transcription_results)
    save_dataframe_to_CSV(transcription_results, 'output-test.csv')


def process_one_image(c: ClassificationApp, filename: str, transcription_results: pd.DataFrame) -> pd.DataFrame:
    gcv, corrected = ipd.ExtractAndProcessSingleImage(c.suggest_engine, filename, 1, False)
    transcription_results = transcription_results.append(pd.DataFrame([[filename, gcv, corrected]],
                                                                      columns=transcription_results.columns))
    return transcription_results


def process_list_of_images(list_filename: str, transcription_results: pd.DataFrame) -> pd.DataFrame:
    # args below:
    ## suggestEngine
    ## txt file name
    ## "minimum confidence" -- using his value of 1
    ## and False=don't search for the label, use the whole image)
    ipd.ProcessImagesFromTheUrlsInTheTextFile(c.suggest_engine, list_filename, 1, False)
    return transcription_results


def save_dataframe_to_CSV(transcription_results: pd.DataFrame, filename: str):
    print(transcription_results.head())
    transcription_results.to_csv(filename)


if __name__ == '__main__':
    main()
