from darts import TimeSeries


class DataEnricher:
    def __init__(self, power_load_df) -> None:
        self._set_base_dataframe(power_load_df)

    def enrich_dataset(self):
        covariates_scaled = self._get_covariates_ts()

        y_scaler, y_train_scaled, y_val = self._get_y()

        return y_scaler, y_train_scaled, y_val, covariates_scaled

    def _get_y(self):
        import pandas as pd

        y_ts = TimeSeries.from_dataframe(
            df=self.base_dataframe,
            time_col="Date",
            value_cols="Load",
            freq="D",
        )
        split_dt = pd.Timestamp("20190101")
        y_train, y_val = y_ts.split_before(split_dt)

        y_scaler, y_train_scaled = self.scale_time_series(y_train)

        return y_scaler, y_train_scaled, y_val

    def _decompose_base_dataframe(self):
        from statsmodels.tsa.seasonal import MSTL
        import pandas as pd

        mstl_res = MSTL(
            self.base_dataframe.set_index("Date")[:"2018-12-31"], periods=(7, 365)
        ).fit()

        trend_df = mstl_res.trend.reset_index()
        seasonal_df = mstl_res.seasonal.reset_index().rename(
            columns={"seasonal_7": "seasonal_week", "seasonal_365": "seasonal_year"}
        )

        last_trend_year = trend_df.query("Date.dt.year==2018").reset_index(drop=True)
        last_trend_year.Date = last_trend_year.Date + pd.offsets.DateOffset(years=1)

        last_seasonal_year = seasonal_df.query("Date.dt.year==2018").reset_index(
            drop=True
        )
        last_seasonal_year.Date = last_seasonal_year.Date + pd.offsets.DateOffset(
            years=1
        )

        self.complete_trend_df = pd.concat(
            [trend_df, last_trend_year], ignore_index=True
        )
        self.complete_seasonal_df = pd.concat(
            [seasonal_df, last_seasonal_year], ignore_index=True
        )

    def _set_base_dataframe(self, power_load_df):
        self.base_dataframe = (
            power_load_df.reset_index().query("Date<='2019-12-31'").copy()
        )

    def _get_weekend_ts(self):
        base_copy = self.base_dataframe.copy()
        base_copy["is_weekend"] = base_copy.Date.apply(
            lambda x: 1 if x.isoweekday() > 5 else 0
        )
        weekend_ts = TimeSeries.from_dataframe(
            df=base_copy,
            time_col="Date",
            value_cols=[
                "is_weekend",
            ],
            freq="D",
        )

        return weekend_ts

    def scale_time_series(self, ts, scaler=None):
        from darts.dataprocessing.transformers import Scaler

        if scaler is None:
            ts_scaler = Scaler()
            ts_scaled = ts_scaler.fit_transform(ts)
            return ts_scaler, ts_scaled
        else:
            ts_scaled = scaler.transform(ts)
            return ts_scaled

    def _get_covariates_ts(self):
        from darts.utils.timeseries_generation import (
            datetime_attribute_timeseries as dt_attr,
        )
        from darts import concatenate
        import numpy as np

        weekend_ts = self._get_weekend_ts()

        month_ts = dt_attr(weekend_ts.time_index, "month", dtype=np.float32)
        week_ts = dt_attr(weekend_ts.time_index, "week", dtype=np.float32)
        day_ts = dt_attr(weekend_ts.time_index, "day", dtype=np.float32)
        year_ts = dt_attr(weekend_ts.time_index, "year", dtype=np.float32)
        dayofyear_ts = dt_attr(weekend_ts.time_index, "dayofyear", dtype=np.float32)
        dayofweek_ts = dt_attr(weekend_ts.time_index, "dayofweek", dtype=np.float32)
        quarter_ts = dt_attr(weekend_ts.time_index, "quarter", dtype=np.float32)

        # we'll split the timeseries to remove the years we are not interested in
        holidays_df = self._get_holidays()

        general_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="holiday",
            freq="D",
        )
        capodanno_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="capodanno",
            freq="D",
        )
        epifania_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="epifania",
            freq="D",
        )
        liberazione_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="liberazione",
            freq="D",
        )
        lavoro_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="lavoro",
            freq="D",
        )
        repubblica_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="repubblica",
            freq="D",
        )
        ferragosto_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="ferragosto",
            freq="D",
        )
        santi_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="santi",
            freq="D",
        )
        concezione_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="concezione",
            freq="D",
        )
        natale_holiday_ts = TimeSeries.from_dataframe(
            df=holidays_df,
            time_col="Date",
            value_cols="natale",
            freq="D",
        )

        self._decompose_base_dataframe()

        trend_ts = TimeSeries.from_dataframe(
            df=self.complete_trend_df,
            time_col="Date",
            value_cols="trend",
            freq="D",
        )
        # seasonal_week_ts = TimeSeries.from_dataframe(df=self.complete_seasonal_df,time_col='Date',value_cols='seasonal_week', freq='D',)
        seasonal_year_ts = TimeSeries.from_dataframe(
            df=self.complete_seasonal_df,
            time_col="Date",
            value_cols="seasonal_year",
            freq="D",
        )

        ts_to_concatenate = [
            weekend_ts,
            month_ts,
            week_ts,
            day_ts,
            year_ts,
            dayofyear_ts,
            dayofweek_ts,
            quarter_ts,
            general_holiday_ts,
            capodanno_holiday_ts,
            epifania_holiday_ts,
            liberazione_holiday_ts,
            lavoro_holiday_ts,
            repubblica_holiday_ts,
            ferragosto_holiday_ts,
            santi_holiday_ts,
            concezione_holiday_ts,
            natale_holiday_ts,
        ]

        covariates_ts = concatenate(
            ts_to_concatenate + [trend_ts, seasonal_year_ts],  # seasonal_week_ts
            axis="component",
        )

        covariates_scaler, covariates_scaled = self.scale_time_series(covariates_ts)
        return covariates_scaled

    def _get_holidays(self):
        import holidays

        holiday_days = holidays.CountryHoliday("IT")

        base_df = self.base_dataframe[["Date"]].copy()
        # TODO: Refactor this code for optimization, readability and maintainability
        for i, r in base_df.iterrows():
            if r.Date in holiday_days:
                base_df.loc[i, "holiday"] = 1
            else:
                base_df.loc[i, "holiday"] = 0

            if r.Date.month == 1 and r.Date.day == 1:
                base_df.loc[i, "capodanno"] = 1
            else:
                base_df.loc[i, "capodanno"] = 0

            if r.Date.month == 1 and r.Date.day == 6:
                base_df.loc[i, "epifania"] = 1
            else:
                base_df.loc[i, "epifania"] = 0

            if r.Date.month == 4 and r.Date.day == 25:
                base_df.loc[i, "liberazione"] = 1
            else:
                base_df.loc[i, "liberazione"] = 0

            if r.Date.month == 5 and r.Date.day == 1:
                base_df.loc[i, "lavoro"] = 1
            else:
                base_df.loc[i, "lavoro"] = 0

            if r.Date.month == 6 and r.Date.day == 2:
                base_df.loc[i, "repubblica"] = 1
            else:
                base_df.loc[i, "repubblica"] = 0

            if r.Date.month == 8 and r.Date.day == 15:
                base_df.loc[i, "ferragosto"] = 1
            else:
                base_df.loc[i, "ferragosto"] = 0

            if r.Date.month == 11 and r.Date.day == 1:
                base_df.loc[i, "santi"] = 1
            else:
                base_df.loc[i, "santi"] = 0

            if r.Date.month == 12 and r.Date.day == 8:
                base_df.loc[i, "concezione"] = 1
            else:
                base_df.loc[i, "concezione"] = 0

            if r.Date.month == 12 and r.Date.day == 25:
                base_df.loc[i, "natale"] = 1
            else:
                base_df.loc[i, "natale"] = 0

        return base_df
