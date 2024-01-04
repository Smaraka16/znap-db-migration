import re, datetime, random

#sql alchemy imports
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

#module imports
from modelcontract import RwoodModels
from main import customError, loggingHandler
 


class Model(RwoodModels):

    def __init__(self, db, df, col, fk_data, code, model, table):
        self.df = df
        self.db = db
        self.col = col
        self.model = model
        self.table = table
        self.fk_data = fk_data
        self.code = code
        self.fk_value = None
         
        self.logger = loggingHandler() #logger
        
    #generate model code
    def generate_model_code(self, prefix):
        current_month = datetime.datetime.now().strftime("%m")
        random_suffix = str(random.randint(1000, 9999))
        return f"{prefix}-{current_month}-{random_suffix}"

    #map json data to db records
    def map_columns(self, row, column):
        return {attr: row[col] for (attr, col) in self.col.items()}

    #fetch additional foreign key data's
    def fetch_foreign_key_value(self, id, data, fk_data):
        try:
            for _,value in fk_data.items():
                for val in value:
                    field, conditional_field, parent_table = val.values()
                    model = self.table[parent_table]
                    fk_id = data[conditional_field]
                    rec_query = select([model]).where(model.c.id == fk_id)
                    conditional_fk_value = self.db.connection.execute(rec_query).fetchone()
                     
                    #if conditonal value
                    if conditional_fk_value:
                        filtered_vals = conditional_fk_value[field]
                        print(filtered_vals)
                        data[field] = filtered_vals
        
             
        except IntegrityError as uniqueErr:
            raise   
        
        except SQLAlchemyError as sqlErr:
            raise       
           
        except Exception as err:
            raise 
         
         
    
    def insert_data(self, Id, code, model, row, data):
        try:
            
            #check if code --> eg:"RW-ACC-00-0001"
            if code:
                prefix, field_name = code.values()
                model_code = self.generate_model_code(prefix) 
                data[field_name] = model_code
                
            if Id:
                
                rec = select([model]).where(model.c.id == Id)
                exisitng_rec = self.db.connection.execute(rec).fetchone()
                 
                # check if rec exist if exist update rec (or) insert new rec
                if exisitng_rec is not None:
                    update_values = {attr: row[col] for attr, col in self.col.items() if col in row.index}
                    self.db.connection.execute(model.update().values(**update_values).where(model.c.id == Id))
                else:
                    model_data = model.insert().values(**data)
                    self.db.connection.execute(model_data)
        
        except IntegrityError as uniqueErr:
            raise   
        
        except SQLAlchemyError as sqlErr:
            raise 
         
        except Exception as err:
            raise
     

    def populate_db(self):
        
        try:
            for _, row in self.df.iterrows():
                
                #mapped data
                data = self.map_columns(row, self.col)
                
                # accountId
                Id = data["id"]
                
                #check if fk_values
                if self.fk_data:
                    self.fk_value = self.fetch_foreign_key_value(Id, data, self.fk_data)
                
                # insert Data
                try:
                    
                    self.insert_data(Id, self.code, self.model, row, data)
                
                except IntegrityError as uniqueErr:
                    
                    self.logger.error(f"Data With Unique Field is Already Presnt {self.model} - {uniqueErr}")
                    
                    if uniqueErr:
                        continue
                    
                except DataError as dataErr:
                    
                    self.logger.error(f"Data Error Occurred {self.model} - {dataErr}")
                    
                    if dataErr:
                        continue
        
               
        except SQLAlchemyError as sqlErr:
            raise   
        
        except Exception as err:
            raise
                
