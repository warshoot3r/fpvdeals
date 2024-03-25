import sqlite3



class UMTDatabase:
    
              
    
    def __init__(self, db_path=None, SCHEMA=None, TableName=None):
        if db_path == None:
            self.db_path = "UMTDB.db"
        else:
            self.db_path = db_path

        if SCHEMA == None:
            self.SCHEMA = [ # change the ordering here to change the DB tables order. it changes it regardless of existing table
                {
                        "Title": "TEXT",
                        "SKU": "TEXT",
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
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self.init_table()
        
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
        for column_name, column_type in self.SCHEMA.items():
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