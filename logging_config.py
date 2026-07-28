import logging


def configure_logging(log_file: str = "pricetracker.log") -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%d-%m-%Y:%H:%M:%S",
        level=logging.DEBUG,
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
