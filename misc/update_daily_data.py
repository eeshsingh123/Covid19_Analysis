import os
import shutil

from config import BASE_PATH

from kaggle.api.kaggle_api_extended import KaggleApi


def download_data_from_kaggle():
    kaggle_api = KaggleApi()
    kaggle_api.authenticate()

    if os.path.isdir(f"{BASE_PATH}\\twitter_db\\kaggle_data"):
        shutil.rmtree(f"{BASE_PATH}\\twitter_db\\kaggle_data")

    kaggle_api.dataset_download_files("sudalairajkumar/novel-corona-virus-2019-dataset",
                                      path=f"{BASE_PATH}//twitter_db//kaggle_data//",
                                      force=True, unzip=True, quiet=True)

    return True


if __name__ == "__main__":
    download_data_from_kaggle()


