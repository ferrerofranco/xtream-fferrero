from logging.handlers import RotatingFileHandler
import argparse
import logging
import sys

def main(arguments):
    logging.info("[main] starting main process")

    try:
        if arguments.prc == 0:
            from src.data_extractor import DataExtractor
            from datetime import date

            current_date = date.today().strftime("%Y-%m-%d")
            data_extractor = DataExtractor()
            data_extractor.extract_data(int(arguments.target_year),current_date)

            logging.info("[main] finished extracting")

        elif arguments.prc == 1:
            from src.data_enricher import DataEnricher
            from datetime import date

            current_date = date.today().strftime("%Y-%m-%d")
            data_enricher = DataEnricher()
            data_enricher.enrich_dataset(int(arguments.target_year),current_date)

            logging.info("[main] finished enriching data")
            

        elif arguments.prc == 2:
            from src.model_trainer import ModelTrainer
            from datetime import date

            current_date = date.today().strftime("%Y-%m-%d")
            model_trainer = ModelTrainer()
            model_trainer.train(int(arguments.target_year),current_date,arguments.model_name)

            logging.info("[main] finished training")

        else:
            raise ValueError(
                f"There is no process assigned to process parameter {arguments.prc}"
            )

        logging.info("[main] main process finished")

    except Exception as e:
        logging.exception(
            "[main] main process finished with errors",
        )
        logging.getLogger().exception(e)
        sys.exit(1)


if __name__ == "__main__":
    from src.config.config import Configurations
    import os

    logging_level = logging.INFO

    configs = Configurations()
    logging_filename = configs.get_log_file_name()
    logging_path = os.path.join('logs/',logging_filename)

    logging_format = "%(asctime)s-%(levelname)s: %(message)s"
    logging_formatter = logging.Formatter(logging_format)

    logger = logging.getLogger(configs.get_logger_name())
    logger.setLevel(logging_level)

    logging_file_handler = RotatingFileHandler(logging_path,
                                                maxBytes=1000000,
                                                backupCount=5)
    logging_file_handler.setLevel(logging_level)
    logging_file_handler.setFormatter(logging_formatter)
    logger.addHandler(logging_file_handler)

    # logging_stream_handler = logging.StreamHandler()
    # logging_stream_handler.setLevel(logging_level)
    # logging_stream_handler.setFormatter(logging_formatter)
    # logger.addHandler(logging_stream_handler)

    parser = argparse.ArgumentParser()
    parser._action_groups.pop()

    required = parser.add_argument_group("required arguments")
    # optional = parser.add_argument_group("optional arguments")

    required.add_argument(
        "--prc",
        type=int,
        required=True,
        help="""
        Number of process to run. 
            0: Extract data
            1: Enrich data
            2: Train model""",
    )

    required.add_argument(
        "--target_year",
        type=int,
        required=True,
        help="""Indicate the target year""",
    )

    required.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="""Indicate the model name. This will be needed for the training process, it will otherwise not be used""",
    )

    args = parser.parse_args()
    main(args)
