from abc import ABC, abstractmethod
 
class RwoodModels(ABC):
    
    '''
        Description
        -----------
            [+] Model Contract: Abstract Class
            [+] populateDb: Abstract Method     
    '''
    
    @abstractmethod
    def populate_db(self):
        pass
    
    @abstractmethod
    def insert_data(self):
        pass
    
     
    
    @abstractmethod
    def map_columns(row, column_mapping):
        pass
    
    @abstractmethod
    def fetch_foreign_key_value(self):
        pass    
    
    
    

 

                  
                
 
                 
             
