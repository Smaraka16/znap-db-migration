import json
import os
import time
import logging
from logging.handlers import RotatingFileHandler


class customError(Exception):
    def __init__(self, message="[+] An Error Occurred"):
        self.message = message
        super().__init__(self.message)


def loggingHandler(logFile='app.log', logLevel=logging.DEBUG):
    '''
        setting up log config
        :param logFile: log File Name
        :param logLevel: logging Level
    '''
    # creating a loggger and level
    logger = logging.getLogger()
    logger.setLevel(logLevel)

    # formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(
        logFile, maxBytes=10*1024*1024, backupCount=5)
    
    file_handler.setFormatter(formatter)
    
    #removing existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # adding handler  to loggers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def readJsonData(file, logger):
    try:
        with open(file) as tableData:
            return json.load(tableData)

    except FileNotFoundError as file_err:
        logger.error(f"File not found: {file_err}")
        raise customError(f"Error retriving Data: File not found")

    except json.JSONDecodeError as json_err:
        logger.error(f"Error decoding JSON in {file}. {json_err}")
        raise customError("Error reading table data: JSON decoding error.")

    except Exception as err:
        raise customError(f"An Error Occured While Reading json File - {err}")


def processTableInfo(tableInfo, logger):
    from dbOperation import MigrationDataCursor
    from fileOperaion import FileReaderContextManager
    
    try:
        modelName = tableInfo.get("model_name", None)
        file = tableInfo.get("file_path", None)
        columns = tableInfo.get("columns", None)
        fk_value = tableInfo.get("fk_val", None)
        code = tableInfo.get("code", None)
         
        try:
            fileName = os.path.basename(file)
            
            logger.info(f"[+] File Initialisation Started: {fileName}")
            
            fileReader = FileReaderContextManager(file)
            df = fileReader.readFileResource()
            
            logger.info(f"Success: Data Frame Retrived From- {fileName}")
            
        except customError as customerr:
            raise 

        try:
            logger.info(f"[+] Database Initialization Started")
            
            dbCursor = MigrationDataCursor(modelName, df, columns, fk_value, code)
            dbCursor.connect_migrate_data()
            
        except customError as err:
            raise

    except Exception as err:
        raise customError(f'{err}')


def main():
    logger = loggingHandler()
    try:
        dataPath = "E:\\Rwood-Db-Migration\\tableconfig.json"
        jsonData = readJsonData(dataPath, logger)

        if jsonData:
            for tableInfo in jsonData.get("tableModel", []):
                processTableInfo(tableInfo, logger)
                

    except customError as customErr:
        logger.error(f'{customErr}')

    except Exception as err:
        logger.error(f'{err}')


if __name__ == "__main__":
    
    try:
         
        logging.info("[+] Database Migration Started started")
        start_time = time.time()
        main()
        end_time = time.time()
        logging.info("[+] Database Migration Completed")
        logging.info(f'[+] Time Taken For Migration: {end_time - start_time / 60}')
    except Exception as err:
        logging.error(f" An Error Occured - {err}")
