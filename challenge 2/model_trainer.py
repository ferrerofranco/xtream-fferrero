class ModelTrainer:
    def __init__(self) -> None:
        pass

    def fit_baseline(self, train_ts):
        from darts.models import TBATS

        self.baseline_model = TBATS()
        self.baseline_model.fit(train_ts)

    def predict_baseline(self, prediction_length):
        self.baseline_forecast = self.baseline_model.predict(prediction_length)

    def evaluate_forecast(self, val_ts, model_type):
        from darts.metrics import mape, r2_score
        
        if model_type=='baseline':
            forecast = self.baseline_forecast
        elif model_type=='improved':
            forecast = self.improved_forecast
        else:
            raise ValueError("Unknown model type")
        
        return mape(val_ts, forecast), r2_score(val_ts, forecast)

    def fit_model(self, y_train_scaled, covariates_scaled):
        from darts.models import TFTModel

        self.improved_model = TFTModel(
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
            random_state=7
        )

        self.improved_model.fit(y_train_scaled,
                    past_covariates=covariates_scaled,
                    future_covariates=covariates_scaled,
                    epochs=10)
        
    def predict_model(self, prediction_length, covariates_scaled, y_scaler):
        self.improved_forecast = self.improved_model.predict(
            n=prediction_length,
            past_covariates=covariates_scaled,
            future_covariates=covariates_scaled
        )

        self.improved_forecast= y_scaler.inverse_transform(self.improved_forecast)

    def compare_month(self, month_nbr, val_ts):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        fig.set_size_inches(15,6)
        val_ts.pd_dataframe().query("Date.dt.month==@month_nbr").Load.plot.line(legend=True)
        self.baseline_forecast.pd_dataframe().query("Date.dt.month==@month_nbr").Load.plot.line(legend=True)
        self.improved_forecast.pd_dataframe().query("Date.dt.month==@month_nbr").Load.plot.line(legend=True)
        ax.legend(["actual", "baseline", "improved_model"])
