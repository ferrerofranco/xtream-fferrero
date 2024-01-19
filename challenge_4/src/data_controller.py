from darts import TimeSeries
import pandas as pd
import logging


class DataController:
    def __init__(self) -> None:
        from src.config.config import Configurations
        from src.DAO.database import DatabaseDAO
        from src.DAO.storage import StorageDAO

        self.configs = Configurations()

        self.logger = logging.getLogger(self.configs.get_logger_name())
        self.storage_dao = StorageDAO()
        self.database_dao = DatabaseDAO()

    def get_all_filenames(self, folder_path: str) -> list[str]:
        self.logger.info(
            f"[{self.__class__.__name__}] Fetching all files in {folder_path}"
        )
        return self.storage_dao.get_all_filenames(folder_path)

    def get_raw_file(self, file_name: str) -> pd.DataFrame:
        return self.read_parquet(
            file_name=file_name, folder=self.configs.get_storage_raw_data_path()
        )

    def get_raw_training_data(
        self, target_year: int, extraction_date: str
    ) -> pd.DataFrame:
        file_name = extraction_date + "_all_up_to_" + str(target_year) + ".parquet.gzip"
        return self.read_parquet(
            file_name=file_name,
            folder=self.configs.get_storage_train_data_path(),
            sub_folder="raw",
        )

    def read_parquet(
        self, file_name: str, folder: str, sub_folder: str = None
    ) -> pd.DataFrame:
        self.logger.info(
            f"[{self.__class__.__name__}] Reading parquet {file_name} in {folder}/{sub_folder}"
        )
        return self.storage_dao.read_parquet(file_name, folder, sub_folder)

    def get_latest_model_number(self) -> int:
        return self.database_dao.get_latest_model_number()[0][0]

    def save_parquet(
        self,
        dataframe: pd.DataFrame,
        sub_folder: str,
        file_name: str,
        extraction_date: str,
    ) -> None:
        file_name = extraction_date + "_" + file_name
        self.storage_dao.save_parquet(dataframe, sub_folder, file_name)

    def save_timeseries(
        self,
        timeseries: TimeSeries,
        file_name: str,
        target_year: int,
        extraction_date: str,
    ) -> None:
        from os.path import join

        full_file_name = join(
            self.configs.get_storage_train_data_path(),
            "preprocessed",
            "_".join([extraction_date, file_name, str(target_year)]),
        )
        self.storage_dao.save_timeseries(timeseries, full_file_name)

    def save_scaler(
        self, file, file_name: str, target_year: int, extraction_date: str
    ) -> None:
        from os.path import join

        full_file_name = join(
            self.configs.get_storage_train_data_path(),
            "preprocessed",
            "_".join([extraction_date, file_name, str(target_year)]),
        )
        self.storage_dao.pickle_file(file, full_file_name)

    def get_files_for_training(self, target_year: int, extraction_date: str) -> tuple:
        from os.path import join

        self.logger.info(f"[{self.__class__.__name__}] Fetching all files for training")

        file_objects = {}

        file_names = ["covariates_scaled", "y_scaler", "y_train_scaled", "y_val"]

        for file_name in file_names:

            full_file_name = (
                "_".join(
                    [
                        extraction_date,
                        file_name,
                        str(target_year),
                    ]
                )
                + ".pkl"
            )

            full_file_name = join(
                self.configs.get_storage_train_data_path(),
                "preprocessed",
                full_file_name,
            )

            file_objects[file_name] = self.storage_dao.load_pickle(full_file_name)

        for file_name in ["covariates_scaled", "y_train_scaled", "y_val"]:
            self.logger.info(
                f"[{self.__class__.__name__}] Fetched {file_name}. Min date: {file_objects[file_name].time_index.min()} Max date: {file_objects[file_name].time_index.max()}"
            )

        return (
            file_objects[file_names[0]],
            file_objects[file_names[1]],
            file_objects[file_names[2]],
            file_objects[file_names[3]],
        )

    def save_metrics(
        self, mape: float, r2: float, model_name: str, extraction_date: str
    ) -> None:
        self.database_dao.save_metrics(mape, r2, model_name, extraction_date)

    def save_forecast(
        self, forecast_dataframe: pd.DataFrame, model_number: int, extraction_date: str
    ) -> None:
        forecast_dataframe = forecast_dataframe.reset_index().rename(
            columns={"Date": "forecast_date", "Load": "forecast_value"}
        )
        forecast_dataframe["model_number"] = model_number
        forecast_dataframe["forecast_execution_date"] = extraction_date
        self.database_dao.save_dataset(
            dataset=forecast_dataframe[
                [
                    "model_number",
                    "forecast_execution_date",
                    "forecast_date",
                    "forecast_value",
                ]
            ],
            table_name=self.configs.get_database_forecast_table(),
        )

    def save_model(
        self, model, file_name: str, target_year: int, extraction_date: str
    ) -> None:
        from os.path import join

        full_file_name = (
            join(
                self.configs.get_storage_models_path(),
                "_".join([file_name, extraction_date, str(target_year)]),
            )
            + ".pt"
        )
        self.logger.info(
            f"[{self.__class__.__name__}] Saving model to {full_file_name}"
        )

        model.save(full_file_name)

    def save_alarms(self, alarms_df):
        self.database_dao.save_dataset(
            dataset=alarms_df, table_name=self.configs.get_database_alarms_table()
        )
