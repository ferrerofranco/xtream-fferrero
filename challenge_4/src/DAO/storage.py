from darts import TimeSeries
from typing import Any
import pandas as pd
import logging


class StorageDAO:
    def __init__(self) -> None:
        from config.config import Configurations
        self.configs = Configurations()

        self.logger = logging.getLogger(self.configs.get_logger_name())
        self.train_data_path = self.configs.get_storage_train_data_path()
    
    def get_all_filenames(self, folder_path:str)  -> list[str]:
        from os import listdir
        from os.path import isfile, join

        only_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

        return only_files

    def read_parquet(self, file_name:str, folder:str, sub_folder:str) -> pd.DataFrame:
        from os.path import join

        if sub_folder is None:
            full_path = folder
        else:
            full_path = join(folder,sub_folder)

        try:
            file_df = pd.read_parquet(join(full_path,file_name))
            return file_df
        except:
            self.logger.error(
                f"[{self.__class__.__name__}] Could not read file {file_name} from {self.raw_data_path}"
            )
            raise

    def save_parquet(self, dataframe:pd.DataFrame, sub_folder:str, file_name:str) -> None:
        from os.path import join
        complete_filename = join(self.train_data_path, sub_folder, file_name + '.parquet.gzip')
        dataframe.to_parquet(complete_filename,compression='gzip')

    def save_timeseries(self, timeseries: TimeSeries, full_file_name:str)->None:
        timeseries.to_pickle(full_file_name + '.pkl')

    def pickle_file(self, file:Any, full_file_name:str) -> None:
        from pickle import dump
        dump(file, open(full_file_name + '.pkl', 'wb'))

    def load_pickle(self, full_file_name:str) -> Any:
        from pickle import load
        return load(open(full_file_name,'rb'))