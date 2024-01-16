import pandas as pd
import logging


class StorageDAO:
    def __init__(self) -> None:
        from config.config import Configurations
        self.configs = Configurations()

        self.logger = logging.getLogger(self.configs.get_logger_name())
        self.raw_data_path = self.configs.get_storage_raw_data_path()
    
    def get_all_filenames(self, folder_path:str)  -> list[str]:
        from os import listdir
        from os.path import isfile, join

        only_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

        return only_files

    def read_parquet(self, file_name:str) -> pd.DataFrame:
        from os.path import join

        try:
            file_df = pd.read_parquet(join(self.raw_data_path,file_name))
            return file_df
        except:
            self.logger.error(
                f"[{self.__class__.__name__}] Could not read file {file_name} from {self.raw_data_path}"
            )
            raise

    def save_parquet(self, dataframe:pd.DataFrame, folder:str, file_name:str) -> None:
        from os.path import join
        complete_filename = join(self.raw_data_path, folder, file_name + '.parquet.gzip')
        dataframe.to_parquet(complete_filename,compression='gzip')