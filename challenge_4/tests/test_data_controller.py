class TestDataController:
    def setup_class(cls):
        import os, sys

        currentdir = os.path.abspath(os.getcwd())
        parentdir = os.path.dirname(currentdir)
        sys.path.insert(0, parentdir)

        from src.config.config import Configurations
        from src.data_controller import DataController

        cls.data_controller = DataController()
        cls.configs = Configurations()

    def test_kept_vector_list(self):
        result = self.data_controller.get_all_filenames(
            self.configs.get_storage_raw_data_path()
        )
        result.sort()

        expected_result = [
            "2006.parquet.gzip",
            "2007.parquet.gzip",
            "2008.parquet.gzip",
            "2009.parquet.gzip",
            "2010.parquet.gzip",
            "2011.parquet.gzip",
            "2012.parquet.gzip",
            "2013.parquet.gzip",
            "2014.parquet.gzip",
            "2015.parquet.gzip",
            "2016.parquet.gzip",
            "2017.parquet.gzip",
            "2018.parquet.gzip",
            "2019.parquet.gzip",
            "2020.parquet.gzip",
            "2021.parquet.gzip",
            "2022.parquet.gzip",
        ]
        assert result == expected_result
