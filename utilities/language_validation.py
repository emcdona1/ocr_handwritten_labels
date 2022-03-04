import sys
import matplotlib.pyplot as plt
from utilities.data_loader import get_timestamp_for_file_saving
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


# read in ground truth occurrence file and extract language and barcode, store in new dataframe
def get_ground_truth(ground_truth_languages: str):
    gt_lan = pd.read_csv(ground_truth_languages, encoding='UTF-8')
    gt_df = pd.DataFrame(data=None, index=None, columns=['Barcode', 'TruthLanguage'])

    print("Extracting ground truth...")
    for l in range(len(gt_lan)):
        barcode = str(gt_lan['catalogNumber'][l])
        language = str(gt_lan['language'][l])
        gt_df.loc[l] = [barcode, language]

    return gt_df


# read in predicted languages and compare to ground truth to match the labels
# then evaluate if the predicted language matches the ground truth language
def compare_ground_truth(ground_truth, predicted_languages: str):
    print("Comparing predictions to ground truth...")
    predicted = pd.read_csv(predicted_languages, encoding='UTF-8')

    correct, incorrect = 0, 0
    correct_list, incorrect_list, prediction_list, truth_list, barcode_list = [], [], [], [], []

    for v in range(len(ground_truth)):
        for p in range(len(predicted)):
            if ground_truth['Barcode'][v] == predicted['Barcode'][p]:
                if ground_truth['TruthLanguage'][v] == 'nan':
                    break
                if predicted['Document Language'][p] == 'None':
                    break
                prediction_list.append(predicted['Document Language'][p])
                truth_list.append(ground_truth['TruthLanguage'][v])
                if ground_truth['TruthLanguage'][v] == predicted['Document Language'][p]:
                    print('Match found')
                    correct_list.append(predicted['Document Language'][p])
                    barcode_list.append(predicted['Barcode'][p])
                    correct = correct + 1
                    break
                else:
                    print('Match found')
                    incorrect_list.append(predicted['Document Language'][p])
                    barcode_list.append(predicted['Barcode'][p])
                    incorrect = incorrect + 1
                    break

    # initialize compare dataframe
    compare_dataframe = pd.DataFrame(data=None, index=None, columns=['Barcode', 'Predicted Lan', 'True Lan',
                                                                     'Correct?'])

    # populate compare dataframe
    for l in range(len(prediction_list)):
        predict = prediction_list[l]
        truth = truth_list[l]
        barcode = barcode_list[l]

        if predict == truth:
            correct = 'Y'
        else:
            correct = 'N'

        compare_dataframe.loc[l] = [barcode, predict, truth, correct]

    # save compare dataframe to CSV
    time = get_timestamp_for_file_saving()
    # compare_dataframe.to_csv('compare_ground_truth_dataframe' + time + '.csv')
    print("Finished: saving to " + 'compare_ground_truth_dataframe' + time + '.csv')

    # generate confusion matrix labels
    labels = set(prediction_list) | set(truth_list)
    labels = sorted(labels)

    # generate confusion matrix
    cm = confusion_matrix(truth_list, prediction_list)
    display_matrix = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    display_matrix.plot()
    plt.show()


if __name__ == '__main__':
    assert len(sys.argv) == 3, 'Must use 2 arguments: 1) ground truth occurrence file, ' + \
                               '2) detect_language_date.csv file, '
    ground_truth_languages = sys.argv[1]
    predicted_languages = sys.argv[2]

    ground_truth = get_ground_truth(ground_truth_languages)
    compare_ground_truth(ground_truth, predicted_languages)
