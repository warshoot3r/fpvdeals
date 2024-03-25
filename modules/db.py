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
                        "Price": "INTEGER",
                        "TotalPriceReduction": "INTEGER"

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
            sql_table_col = ", ".join([f'"{key}"' for key, values in self.SCHEMA[0].items()])
            sql_string = f'''CREATE TABLE IF NOT EXISTS {self.TableName}
                            (id INTEGER PRIMARY KEY,
                            {sql_table_col}
                            )
            '''
            self.cursor.execute(sql_string)
            print("Table Initialised.",flush=True)

    def update_table(self):
        
            
                # Fetch current table column names
        self.cursor.execute(f"PRAGMA table_info({self.TableName});")
        current_columns_info = self.cursor.fetchall()
        current_columns = {info[1] for info in current_columns_info}  # Extract column names
        # Check for missing columns and add them
        print("Updating the Table. `n",self.SCHEMA)
        for data in self.SCHEMA:
            for column_name, column_type in data.items():
                    if column_name not in current_columns:
                        print(f"Missing column '{column_name}'. Adding to the database.", flush=True)
                        alter_table_sql = f"ALTER TABLE {self.TableName} ADD COLUMN \"{column_name}\" {column_type};"
                        self.cursor.execute(alter_table_sql)
                        print(f"Column '{column_name}' added.", flush=True)
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
            print(existing_data_dict)
            for key, new_value in data_dict.items():
                old_value = existing_data_dict.get(key)
                if key != "lastupdated" and key != "totalpricereduction" and old_value != new_value:
                    changed_keys.append(key)
                    if key == "price":
                        price_change_detected = True
                        # Calculate the difference if the old value is not None; otherwise, treat as no reduction
                        price_difference = old_value - new_value if old_value is not None else 0
           
            
            if changed_keys:
                # Update 'totalpricereduction' if price has changed
                if price_change_detected:
                    totalpricereduction = existing_data_dict.get("totalpricereduction", 0) or 0
                    new_totalpricereduction = totalpricereduction + price_difference
                    data_dict["totalpricereduction"] = new_totalpricereduction  # Update data_dict to include this change
                    if "totalpricereduction" not in changed_keys:
                        changed_keys.append("totalpricereduction")  # Ensure this field is updated
                
                # Prepare update query with changed fields
                update_parts = ", ".join([f"{k} = ?" for k in changed_keys])
                update_values = [data_dict[k] for k in changed_keys] + [data_dict[unique_key]]
                update_query = f"UPDATE {self.TableName} SET {update_parts} WHERE {unique_key} = ?"
                self.cursor.execute(update_query, update_values)
                
                print("Updating current listing due to changes", flush=True)
            else:
                print("No changes detected; not updating listing", flush=True)
        else:
            # No existing record, prepare to insert
            columns = ", ".join(data_dict.keys())
            placeholders = ", ".join(["?" for _ in data_dict])
            insert_values = list(data_dict.values())
            insert_query = f"INSERT INTO {self.TableName} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(insert_query, insert_values)
            
            print("Inserting new listing", flush=True)
            
        self.conn.commit()