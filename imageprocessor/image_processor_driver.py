import pandas as pd


def process_images_from_text_file_with_urls(file_path: str, min_confidence: float, extract_tag: bool,
                                            image_processor) -> pd.DataFrame:
    """ Process a list of images from a text file and return OCR and spellcheck top_match_results for all images.
    Returns a pd.DataFrame with values for the processed images.

    Parameters
    ----------
    file_path : str
        File path location for a txt file, which contains one image URL per line (no other data).
    min_confidence : float
        Value [0,1] which would be used for setting a confidence threshold.
    extract_tag : bool
        True if you would like to use the program that extracts the tag from the image, or just
        process the whole image.
    google_vision_client
        Already initialized Google Cloud Vision ia_client with proper token."""
    list_of_urls = []
    with open(file_path) as f:
        lines = f.readlines()
    for line in lines:
        list_of_urls.append(line.strip())
    print('%i images in list.' % len(list_of_urls))
    return process_list_of_image_paths(list_of_urls, min_confidence, extract_tag, image_processor)


def process_one_image(image_path: str, min_confidence: float, extract_tag: bool, image_processor) -> pd.DataFrame:
    """ Wrapper function to process a single image (instead of a batch)."""
    return process_list_of_image_paths([image_path], min_confidence, extract_tag, image_processor)


def process_list_of_image_paths(file_paths, min_confidence, extract_tag, image_processor) -> pd.DataFrame:
    df = pd.DataFrame([], columns=['filename', 'gcv_results', 'correction_results'])
    for one_path in file_paths:
        gcv_response_object, gcv_text, corrected_text = image_processor.process_image(one_path)
        new_row = pd.DataFrame([[one_path, gcv_text, corrected_text]], columns=df.columns)
        df = df.append(new_row)
    return df
