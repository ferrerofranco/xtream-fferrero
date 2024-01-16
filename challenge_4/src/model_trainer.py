import logging


class ModelTrainer:
    def __init__(self) -> None:
        from config.config import Configurations

        self.configs = Configurations()
        self.logger = logging.getLogger(self.configs.get_logger_name())

    def evaluate_forecast(self, val_ts):
        from darts.metrics import mape, r2_score

        return mape(val_ts, self.forecast), r2_score(val_ts, self.forecast)

    def fit_model(self, y_train_scaled, covariates_scaled):
        from darts.models import TFTModel

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
            y_train_scaled,
            past_covariates=covariates_scaled,
            future_covariates=covariates_scaled,
            epochs=10,
        )

    def predict_model(self, prediction_length, covariates_scaled, y_scaler):
        self.forecast = self.model.predict(
            n=prediction_length,
            past_covariates=covariates_scaled,
            future_covariates=covariates_scaled,
        )

        self.forecast = y_scaler.inverse_transform(self.forecast)