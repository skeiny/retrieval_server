import logging


class MyLogger:
    def __init__(self, log_file="my_log.log", log_level=logging.INFO):
        self.log_file = log_file
        self.log_level = log_level

        # 创建一个日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.log_level)

        # 创建一个日志格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # 创建一个文件处理器，用于将日志写入文件
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)

        # 创建一个控制台处理器，用于将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)

        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, message, level=logging.INFO):
        if level == logging.DEBUG:
            self.logger.debug(message)
        elif level == logging.INFO:
            self.logger.info(message)
        elif level == logging.WARNING:
            self.logger.warning(message)
        elif level == logging.ERROR:
            self.logger.error(message)
        elif level == logging.CRITICAL:
            self.logger.critical(message)

    def debug(self, message):
        self.log(message, level=logging.DEBUG)

    def info(self, message):
        self.log(message, level=logging.INFO)

    def warning(self, message):
        self.log(message, level=logging.WARNING)

    def error(self, message):
        self.log(message, level=logging.ERROR)

    def critical(self, message):
        self.log(message, level=logging.CRITICAL)


if __name__ == "__main__":
    input_file_name = "../logs/run.log"
    output_file_name = "../logs/error.log"
    with open(input_file_name, "r") as input_file, open(output_file_name, "w") as output_file:
        for line in input_file:
            if "ERROR" in line:
                output_file.write(line)

