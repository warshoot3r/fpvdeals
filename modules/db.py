import sqlite3
import pandas as pd
from datetime import datetime
import re


class productobject:
    def __init__(self, **objectpairs):
        if objectpairs:
            for key, value in objectpairs.items():
                setattr(self, key, value) 
        
        current_datetime = datetime.now()
        datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        setattr(self, "LastUpdated",datetime_str)
        
    def add_data(self, **objectpairs):
        for key,value in objectpairs.items():
            setattr(self, key, value)
            
            
    def get_data(self, key):
        return getattr(self,key ,None)
    
    def __repr__(self) -> str:
        attributes= ', '.join([f"{key}={value}" for key, value in self.__dict__.items()])
        return attributes
    
class umtbargainsproductobject(productobject):
    def __init__(self, **objectpairs):
        super().__init__(**objectpairs),
        title = self.get_data("title")
        price = self.get_data("price")
        
        #regex to split
        pattern = re.compile(r'^(.*?)\s*\[(.*)\]$')
        match  = pattern.match(title)
        if match:
            name, condition = match.groups()
            print(f"Title-> {name}. Condition -> {condition}")
            setattr(self, "title", name)
            setattr(self, "condition", condition)
        else:
            print(f"No match {title}")
        # Regex to extract the numeric value from a string like "£5.00"
        pattern = re.compile(r'£(\d+\.\d+)')
        match = pattern.search(price)
        
        if match:
            # Extracting the monetary value and converting it to an integer representation
            monetary_value = match.group(1)  # This will be something like '5.00' or '89.95'
            # Removing the decimal point and converting to integer
            monetary_value_as_int = int(monetary_value.replace('.', ''))
            
           # print(f"Monetary Value: {monetary_value}. Integer Representation: {monetary_value_as_int}")
            
            # Setting attributes for later use
            setattr(self, "price", monetary_value)

        else:
            print(f"No monetary value found in title: {price}")
        
class UMTDatabase:
    def __init__(self, db_path=None, SCHEMA=None, TableName=None):
        if db_path == None:
            self.db_path = "UMTDB.db"
        else:
            self.db_path = db_path

        if SCHEMA == None:
            self.SCHEMA =[ # change the ordering here to change the DB tables order. it changes it regardless of existing table
                {
                        "Title": "TEXT",
                        "SKU": "TEXT",
                        "Condition":"TEXT" ,
                        "StockStatus": "TEXT",
                        "Description": "TEXT",
                        "LastUpdated": "DATE",
                        "Price": "REAL",
                        "TotalPriceReduction": "INTEGER",
                        "Reason": "TEXT"
                }
            ]
        else:
            self.SCHEMA = SCHEMA
            
        self.TableName = TableName
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.init_table()
        self.update_table()
    
    
    def return_data(self):
        sql_query = f"SELECT * FROM {self.TableName}"
        data =  pd.read_sql(sql_query, self.conn)
        if data.empty:
            print("No data in table.", flush=True)
            return None
        else:
            return data
        
    def return_data_with_time(self, time_interval='1 hour'):
            """
            Fetches data updated within the specified time interval.

            Args:
            time_interval (str): The time interval within which the data should have been updated.
                                The format should be compatible with SQL, e.g., '1 hour', '30 minutes'.
            """
            # Adjust the SQL query to include the time_interval in the WHERE clause
            # Note: The SQL syntax might need adjustments based on your specific SQL dialect
            sql_query = f"""
            SELECT * 
            FROM {self.TableName} 
            WHERE lastupdated >=  datetime('now', '-{time_interval}')
            """

            data = pd.read_sql(sql_query, self.conn)
            if data.empty:
                print(f"No data updated in the last {time_interval}.", flush=True)
                return None
            else:
                return data
            
    def init_table(self):
            """
            Creates the table if it doesn't exist.
            The table has columns: id, make, model, and price.
            """
            sql_table_col = ", ".join([f'"{key}" {values}' for key, values in self.SCHEMA[0].items()])
            sql_string = f'''CREATE TABLE IF NOT EXISTS {self.TableName}
                            (id INTEGER PRIMARY KEY,
                            {sql_table_col} 
                            )
            '''
            print(f"Running SQL: {sql_string}")
            self.cursor.execute(sql_string)
            print("Table Initialised.",flush=True)

    def update_table(self):
        updates_made = False
            
                # Fetch current table column names
        self.cursor.execute(f"PRAGMA table_info({self.TableName});")
        current_columns_info = self.cursor.fetchall()
        current_columns = {info[1] for info in current_columns_info}  # Extract column names
        # Check for missing columns and add them
        for data in self.SCHEMA:
            for column_name, column_type in data.items():
                    if column_name not in current_columns:
                        print(f"Missing column '{column_name}'. Adding to the database.", flush=True)
                        alter_table_sql = f"ALTER TABLE {self.TableName} ADD COLUMN \"{column_name}\" {column_type};"
                        self.cursor.execute(alter_table_sql)
                        print(f"Column '{column_name}' added.", flush=True)
                        updates_made = True
                    else:
                        print(f"Column '{column_name}' already exists. No changes needed.", flush=True)

                # Commit changes to the database


            self.conn.commit()
            print("Database schema update completed.", flush=True)
                
    def import_data(self, data_to_import, unique_key):
        """
        Updates an existing record or inserts a new one into the specified table.
        If the 'price' has changed, it updates 'totalpricereduction' accordingly.

        :param data_to_import: An object or dictionary where keys are column names and values are the data to insert/update.
        :param unique_key: The unique identifier column name for checking existing records.
        """
        # If data_to_import is an object, convert to dictionary; otherwise, ensure it's a clean dict
        if not isinstance(data_to_import, dict):
            data_dict = {k: v for k, v in data_to_import.__dict__.items() if v is not None}
        else:
            data_dict = {k: v for k, v in data_to_import.items() if v is not None}

        # Fetch existing records to check for duplicates
        self.cursor.execute(f"SELECT * FROM {self.TableName} WHERE {unique_key} = ?", (data_dict[unique_key],))
        existing_record = self.cursor.fetchone()
        

        if existing_record:
            existing_data_dict = {desc[0].lower(): value for desc, value in zip(self.cursor.description, existing_record)}
            changed_keys = []
            price_change_detected = False
            price_difference = 0

            # Determine which keys have changed, excluding 'lastupdated', and calculate price difference if applicable
            for key, new_value in data_dict.items():
                
                old_value = existing_data_dict.get(key.lower())
                # print(key, new_value,old_value )
                if key.lower() not in ["lastupdated", "totalpricereduction"] and old_value != new_value:
                    if key == "price":
                        # Calculate the difference if the old value is not None; otherwise, treat as no reduction
                        price_difference = float(old_value) - float(new_value) if old_value is not None else 0
                        if price_difference != 0:
                            price_change_detected = True
                            
                            existing_data_dict["totalpricereduction"] = round(price_difference, 4)
                            existing_data_dict["price"] = float(new_value)
                            existing_data_dict["reason"] = "Price Changed"
                            
                            
                            
                            changed_keys.append(existing_data_dict)
                            print(f" {existing_record[1]} {key} reduced to {price_difference} from {old_value}")
                    else:
                        existing_data_dict[key] = new_value
                        existing_data_dict["reason"] = f"{key} changed"
                        print(f" {existing_record[1]} {key} changed with {old_value} -> {new_value}")
                        changed_keys.append(existing_data_dict)

               # Update 'totalpric:ereduction' if price has changed
            if changed_keys:

                # Initialize variables for constructing the parameterized query
                query_parts = []
                params = []
                unique_key_value = ""

                # Construct the query and parameters list
                for products in changed_keys:
                    for properties_key, properties_value in products.items():
                        if properties_key == "lastupdated":
                            current_datetime = datetime.now()
                            datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
                            query_parts.append(f"{properties_key} = ?")
                            params.append(datetime_str)
                        else:
                            query_parts.append(f"{properties_key} = ?")
                            params.append(properties_value)
                        if properties_key == "sku":
                            unique_key_value = properties_value
                        
                # Join the query parts and add the WHERE clause
                query = ", ".join(query_parts)
                update_query = f"UPDATE {self.TableName} SET {query} WHERE {unique_key} = ?"
                # Add the unique key value to the parameters list
                params.append(unique_key_value)

                print(f"Updating current listing due to changes. Running SQL: \n {update_query} with parameters {params}", flush=True)
                # Execute the parameterized query
                self.cursor.execute(update_query, params)
            else:
                print("No changes detected; not updating listing", flush=True)

        else:
            # No existing record, prepare to insert
            #add a reason 
            data_dict["reason"] = "New Product"
            columns = ", ".join(data_dict.keys())
            placeholders = ", ".join(["?" for _ in data_dict])
            insert_values = list(data_dict.values())
            insert_query = f"INSERT INTO {self.TableName} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(insert_query, insert_values)
            
            print(f"Inserting new listing. Running SQL: \n {insert_query} ", flush=True)
        

        self.conn.commit()