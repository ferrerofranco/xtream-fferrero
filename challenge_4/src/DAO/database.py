import pandas as pd
import logging


class DatabaseDAO:
    def __init__(self) -> None:
        from src.config.config import Configurations
        self.configs = Configurations()

        self.logger = logging.getLogger(self.configs.get_logger_name())
        self.db_path = self.configs.get_db_path()
        self._initialize_mock_db()

    def _initialize_mock_db(self) -> None:
        self.logger.info(
            f"[{self.__class__.__name__}] Initializing database"
        )

        self._create_models_table()
        self._create_forecast_table()
        self._create_alarms_table()

        self._insert_mock_data()

    def _create_models_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS models
                    (model_number INTEGER PRIMARY KEY AUTOINCREMENT, model_name TEXT, mape REAL, r2 REAL, train_date TEXT, production BOOL)'''
        
        self._execute_statement(query)

    def _create_forecast_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS forecasts
                    (model_number INTEGER, forecast_execution_date TEXT, forecast_date TEXT, forecast_value REAL)'''
        self._execute_statement(query)

    def _create_alarms_table(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS alarms
                    (model_number INTEGER, alarm_date TEXT, alarm_name TEXT, alarm_content TEXT)'''
        self._execute_statement(query)

    def _insert_mock_data(self) -> None:
        query = '''INSERT OR IGNORE INTO models(model_number, model_name, mape, r2, train_date) VALUES
                        ('1', 'mock_bad_model','28.32','0.1','2022-01-01')'''
        self._execute_statement(query)

    def get_latest_model_number(self) -> list[tuple]:
        query = '''SELECT max(model_number) max_model_number FROM models'''
        return self._execute_statement(query)
    
    def save_dataset(self, dataset:pd.DataFrame, table_name:str) -> None:
        import sqlite3
        db_connection = sqlite3.connect(self.db_path)
        try:
            self.logger.info(
                f"[{self.__class__.__name__}] Saving dataset to {table_name}"
            )
            dataset.to_sql(
                if_exists="append",
                method="multi",
                # schema=schema_name,
                name=table_name,
                con=db_connection,
                index=False,
            )
        except:
            self.logger.error(
                f"[{self.__class__.__name__}] failed to save dataset on {table_name}"
            )
            raise

    def _execute_statement(self, statement:str) -> list:
        from contextlib import closing
        import sqlite3

        try:
            with closing(sqlite3.connect(self.db_path)) as con, con,  \
                    closing(con.cursor()) as cur:
                cur.execute(statement)
                return cur.fetchall()
        except:
            self.logger.error(
                f"[{self.__class__.__name__}] Failed to execute statement on DB"
            )
            self.logger.info(
                f"[{self.__class__.__name__}] {statement}"
            )
            raise

    def save_metrics(self, mape:float, r2:float, model_name:str, extraction_date:str) -> None:
        self.logger.info(
                f"[{self.__class__.__name__}] Saving metrics to DB"
            )
        query = f'''INSERT INTO models(model_name, mape, r2, train_date) VALUES
                        ('{model_name}','{mape}','{r2}','{extraction_date}')'''
        self._execute_statement(query)
