from darts.models import TFTModel
import logging


class ModelTrainer:
    def __init__(self) -> None:
        from src.data_controller import DataController
        from src.config.config import Configurations

        self.configs = Configurations()
        self.logger = logging.getLogger(self.configs.get_logger_name())

        self.data_controller = DataController()

    def train(self,target_year:int, extraction_date:str, model_name:str)->None:
        
        self.target_year = target_year
        self.extraction_date = extraction_date
        self.model_name = model_name
        
        self._get_files()
        self._fit()
        self._predict()
        
        mape, r2 = self._evaluate_forecast()
        model_number = self.data_controller.get_latest_model_number()
        alarms = self._generate_alarms(model_number)

        self.logger.info(
            f"[{self.__class__.__name__}] Saving model outputs"
        )
        self.data_controller.save_metrics(mape, r2, self.model_name, self.extraction_date)
        self.data_controller.save_forecast(forecast_dataframe=self.forecast.pd_dataframe(), model_number=model_number, extraction_date = extraction_date)
        self.data_controller.save_alarms(alarms)
        self.data_controller.save_model(model=self.model, file_name='_'.join([str(model_number), self.model_name]), target_year=self.target_year, extraction_date=self.extraction_date)

    def _get_files(self) -> None:
         (
            self.covariates_scaled, 
            self.y_scaler, 
            self.y_train_scaled, 
            self.y_val
        ) = self.data_controller.get_files_for_training(self.target_year, self.extraction_date)

    def _fit(self):
        self.logger.info(
            f"[{self.__class__.__name__}] Fitting model"
        )
        self.model = TFTModel(
            hidden_size=12,
            lstm_layers=3,
            num_attention_heads=4,
            full_attention=False,
            # feed_forward=GatedResidualNetwork,
            dropout=0.1,
            hidden_continuous_size=8,
            categorical_embedding_sizes=None,
            add_relative_index=False,
            likelihood=None,
            # norm_type=LayerNorm,
            use_static_covariates=True,
            input_chunk_length=365,
            output_chunk_length=365,
            random_state=7,
        )

        self.model.fit(
            self.y_train_scaled,
            past_covariates=self.covariates_scaled,
            future_covariates=self.covariates_scaled,
            epochs=self.configs.get_train_epochs(),
        )

    def _predict(self) -> None:
        self.logger.info(
            f"[{self.__class__.__name__}] Forecasting with model"
        )
        self.forecast = self.model.predict(
            n=len(self.y_val),
            past_covariates=self.covariates_scaled,
            future_covariates=self.covariates_scaled,
        )

        self.forecast = self.y_scaler.inverse_transform(self.forecast)
    
    def _evaluate_forecast(self) -> tuple[float,float]:
        from darts.metrics import mape, r2_score

        self.logger.info(
            f"[{self.__class__.__name__}] Evaluating forecast"
        )
        return mape(self.y_val, self.forecast), r2_score(self.y_val, self.forecast)
    
    def _generate_alarms(self, model_number):
        import pandas as pd

        forecast_df = self.forecast.pd_dataframe()
        alarm_names = []
        alarm_contents = []

        high_value_limit = 1_000_000
        high_values = forecast_df.query("Load > @high_value_limit").shape[0]
        if high_values>0:
            alarm_names.append('high_values')
            alarm_contents.append(f'There are {high_values} values over {high_value_limit}')

        negatives = forecast_df.query("Load < 0").shape[0]
        if negatives>0:
            alarm_names.append('negatives')
            alarm_contents.append(f'There are {negatives} negative values')

        low_value_limit = 700_000
        low_values = forecast_df.query("Load < 700_000").shape[0]
        if low_values >0 :
            alarm_names.append('low_values')
            alarm_contents.append(f'There are {low_values} values under {low_value_limit}')

        alarms = pd.DataFrame(
            {
                'model_number' : model_number,
                'alarm_date' : self.extraction_date,
                'alarm_name' : alarm_names,
                'alarm_content' : alarm_contents,
            }
        )

        return alarms