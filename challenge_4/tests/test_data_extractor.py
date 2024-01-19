import pytest


class TestDataExtractor:
    def setup_class(cls):
        import os, sys

        currentdir = os.path.abspath(os.getcwd())
        parentdir = os.path.dirname(currentdir)
        sys.path.insert(0, parentdir)

        from src.data_extractor import DataExtractor

        cls.data_extractor = DataExtractor()

    def test_data_validation_pass(self):
        import pandas as pd

        test_df = pd.DataFrame(
            {
                "Date": ["2022-01-01", "2022-01-02"],
                "Load": [12.41, 15623.123],
            }
        )
        test_df.Date = pd.to_datetime(test_df.Date)

        assert self.data_extractor._validate_data(test_df) is None

    def test_data_validation_fail(self):
        from pandera.errors import SchemaError
        import pandas as pd

        test_df = pd.DataFrame(
            {
                "Date": ["2022-01-01", "2022-01-02"],
                "Load": [12.41, 15623.123],
            }
        )

        with pytest.raises(SchemaError) as excinfo:
            self.data_extractor._validate_data(test_df)

        assert (
            str(excinfo.value)
            == "expected series 'Date' to have type datetime64[ns], got object"
        )
