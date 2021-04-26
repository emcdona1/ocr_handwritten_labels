import sys
import os
import numpy as np
import prep_comparison_data
import calculate_changes
from imageprocessor.image_processor import ImageProcessor, GCVProcessor, AWSProcessor
from typing import List, Tuple
from matplotlib import pyplot
from sklearn.cluster import Birch, AgglomerativeClustering
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture


def main(occurrence_filepath: str, ocr_text_filepath: str, image_folder: str, analysis):
    # analysis = prep_comparison_data.main(occurrence_filepath, ocr_text_filepath)
    # calculate_changes.main(analysis, 150)
    processors: List[ImageProcessor] = [GCVProcessor(), AWSProcessor()]
    for idx, row in analysis.iterrows():
        barcode = row.at['ground_truth', 'barcode']
        image_location = image_folder + os.path.sep + barcode + '.jpg'

        pyplot.clf()
        fig_count = 1
        pyplot.clf()
        for i, processor in enumerate(processors):
            processor.load_processed_ocr_response(image_location)
            list_of_word_points = processor.get_found_word_locations()
            image_height = processor.current_image_height
            image_width = processor.current_image_width

def plot_words_and_label(fig_num: int, processor, image_height: int, image_width: int, np_of_points: np.ndarray,
                         label_points: tuple, label_image_save_location: str):
    fig = pyplot.figure(fig_num)
    pyplot.clf()
    pyplot.title('%s using %s' % (processor.current_image_barcode, processor.name.upper()))
    pyplot.xlim([0, image_width])
    pyplot.ylim([0, image_height])
    if image_width > 2000:
        fig.set_size_inches(image_width / 980, image_height / 980)  # high resolution images
    else:
        fig.set_size_inches(image_width / 300, image_height / 300)  # web resolution images

    pyplot.scatter(np_of_points[:, 0], image_height - np_of_points[:, 1], s=4)

    for p in range(0, 3):
        pyplot.plot([label_points[p][0], label_points[p + 1][0]],
                    [image_height - label_points[p][1], image_height - label_points[p + 1][1]],
                    color='black')
    pyplot.plot([label_points[3][0], label_points[0][0]],
                [image_height - label_points[3][1], image_height - label_points[0][1]],
                color='black')
    pyplot.savefig(label_image_save_location + os.path.sep + processor.current_image_barcode + '-' + processor.name + '.png')


def find_most_concentrated_label(np_of_points: np.ndarray, image_width: int, image_height: int,
                                 label_width: int, label_height: int) -> \
        Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """ Searches bottom quadrant of image for highest concentration of word bounding boxes
    and returns a set of 4 tuples (top-left, top-right, bottom-right, bottom-left). """
    max_count = 0
    max_loc = (0, 0)
    for y in range(int(image_height / 2), image_height - label_height + 1):
        for x in range(int(image_width / 2), image_width - label_width + 1):
            x_values = np_of_points[:, 0]
            idx_of_valid_x = np.intersect1d(np.where(x_values >= x), np.where(x_values < x + label_width))
            y_possible = np_of_points[idx_of_valid_x, 1]
            valid_y = np.intersect1d(np.where(y_possible >= y), np.where(y_possible < y + label_height))
            count = valid_y.shape[0]
            if count >= max_count:
                max_count = count
                max_loc = (x, y)
    print('Label found at point %s with %.0f words.' % (str(max_loc), max_count/4))
    upper_left = max_loc
    upper_right = (max_loc[0] + label_width, max_loc[1])
    lower_right = (max_loc[0] + label_width, max_loc[1] + label_height)
    lower_left = (max_loc[0], max_loc[1] + label_height)
    return upper_left, upper_right, lower_right, lower_left


def slower_find_most_concentrated_label(list_of_word_points: list, image_width: int, image_height: int,
                                        label_width: int, label_height: int) -> \
        Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    """ Due to runtime length, this only searches the bottom quadrant of an image. """
    density = np.zeros((image_height, image_width))
    for vertex in list_of_word_points:
        density[vertex[1], vertex[0]] = 1 + density[vertex[1], vertex[0]]
    max_count = 0
    max_loc = (0, 0)
    for y in range(int(image_height / 2), image_height - label_height + 1):
        for x in range(int(image_width / 2), image_width - label_width + 1):
            count = np.sum(density[y:y + label_height, x:x + label_width])
            if count >= max_count:
                max_count = count
                max_loc = (x, y)
        print(y)
    upper_left = max_loc
    upper_right = (max_loc[0] + label_width, max_loc[1])
    lower_right = (max_loc[0] + label_width, max_loc[1] + label_height)
    lower_left = (max_loc[0], max_loc[1] + label_height)
    return upper_left, upper_right, lower_right, lower_left


def word_clustering(fig_count: int, image_height: int, image_width: int, np_of_points: np.ndarray,
                    processor: ImageProcessor) -> None:
    # n_clusters = range(2, 5)
    # for N in n_clusters:
    model = Birch(threshold=5)  # this one clustered an isolated pt by itself, that's good
    # model = AgglomerativeClustering(n_clusters=N)  # this seems very similar to Birch so far
    # model = GaussianMixture(n_components=N)  # this one doesn't seem like what we want - it clustered an isolated pt with a far away group
    # model = BayesianGaussianMixture(n_components=N)  # best guess: this is GaussianMixture but # of clusters can be <= N
    # model = AffinityPropagation(damping=0.9)  # Seems like it always makes too many.
    model.fit(np_of_points)
    y_hat = model.fit_predict(np_of_points)
    clusters = np.unique(y_hat)
    pyplot.figure(fig_count)
    pyplot.title(processor.name.upper())  # + ' - %i clusters' % N)
    pyplot.xlim([0, image_width])
    pyplot.ylim([0, image_height])
    for cluster in clusters:
        row_idx = np.where(y_hat == cluster)
        pyplot.scatter(np_of_points[row_idx, 0], image_height - np_of_points[row_idx, 1])


def distance(pt1, pt2) -> float:
    dist = (pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2
    dist = dist ** 0.5
    return dist
