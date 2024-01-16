import pandas as pd
import logging


class DataController:
    def __init__(self) -> None:
        from config.config import Configurations
        from DAO.database import DatabaseDAO
        from DAO.storage import StorageDAO

        self.configs = Configurations()

        self.logger = logging.getLogger(self.configs.get_logger_name())
        self.storage_dao = StorageDAO()
        self.database_dao = DatabaseDAO()

    def get_all_filenames(self, folder_path:str) -> list[str]:
        return self.storage_dao.get_all_filenames(folder_path)
    
    def read_parquet(self, file_name:str) -> pd.DataFrame:
        return self.storage_dao.read_parquet(file_name)
    
    def get_latest_model(self) -> tuple:
        return  self.storage_dao.get_latest_model()[0]
    
    def save_parquet(self, dataframe: pd.DataFrame, folder: str, file_name:str, extraction_date:str) -> None:
        file_name = extraction_date + '_' + file_name
        self.storage_dao.save_parquet(dataframe,folder,file_name)