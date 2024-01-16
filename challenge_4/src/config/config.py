class Configurations:
    def __init__(self) -> None:
        self.db_path = '../mock_database/zap_inc.db'
        self.logger_name = "ZapIncLogger"
        self.log_file_name = "zap_inc.log"
        self.storage_path = '../mock_storage/'
        self.storage_raw_data_folder = 'raw_data'
        self.storage_models_folder = 'models'
        self.models_path = '../models/'

    def get_db_path(self) -> str:
        return self.db_path
    
    def get_logger_name(self) -> str:
        return self.logger_name

    def get_log_file_name(self) -> str:
        return self.log_file_name
    
    def get_storage_path(self) -> str:
        return self.storage_path
    
    def get_storage_raw_data_path(self) -> str:
        from os.path import join
        return join(self.storage_path,self.storage_raw_data_folder)
    
    def get_storage_models_path(self) -> str:
        from os.path import join
        return join(self.storage_path,self.storage_models_folder)