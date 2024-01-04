import pandas as pd
import logging
import os
from main import customError, loggingHandler

class FileReaderContextManager:

    '''
        Description:
        ------------
            [+] Handles File Operation For Reading DataFrame From Excel File or CSV.
        Arguments:
        ----------
            [+] File Path
        Attributes:
        -----------
            [+] fileExists(filePath): Check if file is available.
            [+] readFileResource(): Read files using pandas and return dataframe
                
    '''
    
    def __init__(self, File):
        self.file = File
        self.df = None
        self.logger = loggingHandler()
       
    def fileExists(self,filePath):
        return os.path.exists(filePath)
    
    def readFileResource(self):
        try:
            if self.fileExists(self.file):
                
                file_extension = self.file.split(".")

                if file_extension[1] == "csv":
                    self.df = pd.read_csv(self.file, encoding="latin1")
                    
                elif file_extension[1] in ("xls", "xlsx"):
                    self.df = pd.read_excel(self.file,engine='openpyxl')
                    
                else:
                    raise ValueError(f'[-] Unsupported File Format - {file_extension}')
                return self.df
            else:
                raise FileNotFoundError(f"[-] {self.file}: File Not Found")
        
        except FileNotFoundError as fileErr:
            self.logger.error(f'{fileErr}')
            raise customError('[-] Error Retreiving Data: File Not Found')
        
        except ValueError as valErr:
            self.logger.error(f'{valErr}')
            raise customError(f'[-] File Format {file_extension[1]}: Unsupported')
        
        except Exception as err:
            self.logger.error(f'[-] {err}')
            raise customError(f'[-] {err}')