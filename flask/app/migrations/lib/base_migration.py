from app import db, create_app


class BaseMigration:
    def __init__(self):
        self.connection = None
        self.app = create_app()
        with self.app.app_context():
            self.connection = db.connect

    def add_column(self, table_name, column_name, datatype):
        query = f"""ALTER TABLE {table_name} ADD {column_name} {datatype};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def drop_column(self, table_name, column_name):
        query = f"""ALTER TABLE {table_name} DROP {column_name};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def alter_index(self, table_name, new_index_name, new_indexed_column, old_index_name):
        query = f"""ALTER TABLE {table_name} ADD INDEX {new_index_name} ({new_indexed_column}), DROP INDEX {old_index_name};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def alter_column(self, table_name, column_name, datatype):
        query = f"""ALTER TABLE {table_name} MODIFY COLUMN {column_name} {datatype};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def change_column_name(self, table_name, old_column_name, new_column_name):
        query = f"""ALTER TABLE {table_name} RENAME COLUMN {old_column_name} TO {new_column_name};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def change_table_name(self, old_table, new_table):
        query = f"""ALTER TABLE {old_table} RENAME TO {new_table};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def create_table(self, table_name, fields_with_type):
        query = f"""CREATE TABLE {table_name} ({fields_with_type});"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def drop_table(self, table_name):
        query = f"""DROP TABLE {table_name};"""
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def insert_db_version_data(self):
        query = f"INSERT INTO db_version (version) VALUES (0000000000);"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def update_version_table(self, version):
        query = f"UPDATE db_version SET version = {version};"
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def execute(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
        self.connection.commit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection.cursor:
            self.connection.cursor.close()
