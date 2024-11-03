import os


def remove_file(file_path) :
    if os.path.exists(file_path) :
        os.remove(file_path)


def create_directory_if_not_exists(directory_path) :
    if not os.path.exists(directory_path) :
        os.makedirs(directory_path)
