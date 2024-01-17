from darts.models import TFTModel
import logging


class ModelTrainer:
    def __init__(self) -> None:
        from data_controller import DataController
        from config.config import Configurations

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
        self.data_controller.save_metrics(mape, r2, self.model_name, self.extraction_date)
        model_number = self.data_controller.get_latest_model_number()
        self.data_controller.save_forecast(forecast_dataframe=self.forecast.pd_dataframe(), model_number=model_number, extraction_date = extraction_date)
        self.data_controller.save_model(file=self.model, file_name='_'.join([str(model_number), self.model_name]), target_year=self.target_year, extraction_date=self.extraction_date)

    def _get_files(self) -> None:
         (
            self.covariates_scaled, 
            self.y_scaler, 
            self.y_train_scaled, 
            self.y_val
        ) = self.data_controller.get_files_for_training(self.target_year, self.extraction_date)

    def _fit(self):
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
            epochs=10,
        )

    def _predict(self) -> None:
        self.forecast = self.model.predict(
            n=len(self.y_val),
            past_covariates=self.covariates_scaled,
            future_covariates=self.covariates_scaled,
        )

        self.forecast = self.y_scaler.inverse_transform(self.forecast)
    
    def _evaluate_forecast(self) -> tuple[float,float]:
        from darts.metrics import mape, r2_score

        return mape(self.y_val, self.forecast), r2_score(self.y_val, self.forecast)