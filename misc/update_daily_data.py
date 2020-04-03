import os
import shutil

from config import BASE_PATH

from kaggle.api.kaggle_api_extended import KaggleApi


def call_kaggle_api():
    kaggle_api = KaggleApi()
    kaggle_api.authenticate()

    if os.path.isdir(f"{BASE_PATH}\\twitter_db\\kaggle_data"):
        shutil.rmtree(f"{BASE_PATH}\\twitter_db\\kaggle_data")

    kaggle_api.dataset_download_files("sudalairajkumar/novel-corona-virus-2019-dataset",
                                      path=f"{BASE_PATH}//twitter_db//kaggle_data//",
                                      force=True, unzip=True, quiet=False)

    return True


if __name__ == "__main__":
    call_kaggle_api()


