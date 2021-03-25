import os
import pickle


def load_list_from_txt(file_path: str) -> list:
    results = list()
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for item in lines:
            item = item.strip()
            results.append(item)
    return results


def load_file_list_from_filesystem(directory_or_file: str) -> list:
    results = list()
    if os.path.isdir(directory_or_file):
        results = os.listdir(directory_or_file)
        results = [directory_or_file + os.path.sep + filename for filename in results]
        results = [item for item in results if not os.path.isdir(item)]  # remove subdirectories
    elif os.path.isfile(directory_or_file):
        results = [directory_or_file]
    else:
        raise FileNotFoundError('Not a valid directory or file: %s' % directory_or_file)

    return results


def load_pickle(pickle_file_path: str):
    with open(pickle_file_path, 'rb') as file:
        de_pickled = pickle.load(file)
    return de_pickled


def pickle_an_object(save_directory: str, object_id: str, obj_to_pickle) -> None:
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    filename = object_id + '.pickle'
    with open(os.path.join(save_directory, filename), 'wb') as file:
        pickle.dump(obj_to_pickle, file)
