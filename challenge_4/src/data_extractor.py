import logging


class DataExtractor:
    def __init__(self) -> None:
        from src.config.config import Configurations
        from src.data_controller import DataController

        self.configs = Configurations()
        self.logger = logging.getLogger(self.configs.get_logger_name())

        self.data_controller = DataController()

    def extract_data(self, target_year:int, extraction_date:str) -> None:
        import pandas as pd

        self.logger.info(
            f"[{self.__class__.__name__}] Fetching and unifying data"
        )

        file_list = self.data_controller.get_all_filenames(self.configs.get_storage_raw_data_path())
        filtered_file_list = [file_name for file_name in file_list if int(file_name[:4])<=target_year]

        full_df = None
        for file_name in filtered_file_list:
            temp_df = self.data_controller.get_raw_file(file_name)
            if full_df is None:
                full_df = temp_df.copy()
            else:
                full_df = pd.concat([full_df,temp_df],ignore_index=True)

        full_df = full_df.sort_values(by='Date').reset_index(drop=True)

        file_name = 'all_up_to_'+str(target_year)
        self.data_controller.save_parquet(
            dataframe=full_df,
            sub_folder='raw',
            file_name=file_name,
            extraction_date=extraction_date
        )