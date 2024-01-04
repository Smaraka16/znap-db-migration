from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from dbmigration import Model

from main import customError, loggingHandler
import urllib.parse

class DbSessionContextManager:
    hostname = 'rwood.znapay.in'
    password = "Rw00dzn@p@y"
    encoded_password = urllib.parse.quote(password, safe="")
    DbEngine = "postgresql://postgres:8065@localhost:5432/znap_rwood_30_11_2023"
    # DbEngine = f"postgresql://rwood_znapay:{encoded_password}@{hostname}:5432/rwoodapi_znapay"
    
    def __init__(self):
        self.engine = create_engine(DbSessionContextManager.DbEngine)
        self.metadata = MetaData()
        self.connection = None
        self.logger = loggingHandler()

    def __enter__(self):
        self.connection = self.engine.connect()
        self.metadata.reflect(bind=self.connection)
        return self
        
    def __exit__(self,exec_type, exec_value, traceback):
        if self.connection:
            self.connection.close()
        self.logger.info("[+] Database Connection Closed Successfully")
            
class MigrationDataCursor():
    
    def __init__(self,modelName, df, col, fk_data=None, code=None):
        self.modelName = modelName
        self.df = df
        self.col = col
        self.fk_data = fk_data
        self.code  = code
        self.logger = loggingHandler()
         
     
    def connect_migrate_data(self):
         
        try:
            with DbSessionContextManager() as db_session:
                self.logger.info("[+] Database Connected Successfully")
                
                #get raw sql tables
                tables = db_session.metadata.tables
                self.modelTable = tables[self.modelName]
                
                #migrate model
                self.logger.info(f"[+] Migration Initalized For : {self.modelName}")
                
                migrate_cursor = Model(db_session, self.df, self.col, self.fk_data, self.code, self.modelTable, tables) 
                migrate_cursor.populate_db()
                
                self.logger.info(f"[+] Migration Successfull : {self.modelName}")   
        
        except OperationalError as opErr:
            raise customError(f'[-] Error Connecting Db - {DbSessionContextManager.DbEngine}')
        
        except SQLAlchemyError as sqlErr:
            raise customError(f'[-] An unexpected Database Error Occurred: {sqlErr}')
        
        except Exception as err:
            raise customError(f'[-] An unexpecte Error Occurred: {err}')
                        