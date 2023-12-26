###################################################
# DBMan
# Author      : Adeeb
# Version     : 1.0
# Description : sqlite database manager
###################################################

import os
import sqlite3


# ============== Exception Handling ============= #

class TableNotFound(Exception):
    """
    Raise Exception when database not found in the given path
    """
    pass


class ColNotFound(Exception):
    """
    Raise Exception when the given column name not found while accessing database through column name
    """
    pass


class SizeNotPermitted(Exception):
    """
    Raise Exception when the given size is not in the limit of the specified date type
    """
    pass


class DataNotFound(Exception):
    """
    Raise Exception when the query data is empty
    """
    pass


# =============== Field Date Types ============== #

class Fields:
    """
    Table column data types for creating table
    """

    @staticmethod
    def PrimaryKey(col_name: str = "id"):
        return f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL"

    @staticmethod
    def _check_size(data_type: str, size: int):
        if size < 0:
            raise SizeNotPermitted

        sizes = {
            "CHAR": 255,
            "VARCHAR": 65535,
            "TEXT": 65535,
            "INT": 255,
            "FLOAT": 255,
        }
        if size > sizes[data_type]:
            raise SizeNotPermitted

    @staticmethod
    def _generate_field(data_type: str, size: int, null: bool, unique: bool = False):
        Fields._check_size(data_type, size)
        field = f"{data_type}"
        if size != 0:
            field += f"({size})"

        if null:
            field += " NOT NULL"

        if unique:
            field += " UNIQUE"

        return field

    @staticmethod
    def CharField(size: int = 0, null: bool = True, unique: bool = False) -> str:
        data_type = "CHAR"
        return Fields._generate_field(data_type, size, null, unique)

    @staticmethod
    def VarCharField(size: int = 0, null: bool = True, unique: bool = False) -> str:
        data_type = "VARCHAR"
        return Fields._generate_field(data_type, size, null, unique)

    @staticmethod
    def TextField(size: int = 0, null: bool = True, unique: bool = False) -> str:
        data_type = "TEXT"
        return Fields._generate_field(data_type, size, null, unique)

    @staticmethod
    def IntField(size: int = 0, null: bool = True, unique: bool = False) -> str:
        data_type = "INT"
        return Fields._generate_field(data_type, size, null, unique)

    @staticmethod
    def FloatField(size: int = 0, null: bool = True, unique: bool = False) -> str:
        data_type = "FLOAT"
        return Fields._generate_field(data_type, size, null, unique)


# =============================================== #

class DBInit:
    """
    CLass which deal with initial processes
    Include common methods
    """
    db_path: str = None
    table_name: str = None

    def __init__(self):
        if self.db_path is not None:
            self._check_db_path_()

        if self.table_name is not None:
            self._check_table_name_(self.table_name)

    def _check_db_path_(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"DataBase not found: {self.db_path}")

    def _check_table_name_(self, table_name: str):
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        db_data = self._db_read_(query)
        if not db_data:
            return
        table_names = [x[0] for x in db_data]
        if table_name not in table_names:
            raise TableNotFound(f"Table not found: {table_name}")

    def _db_read_(self, query: str, params: tuple = ()):
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        data = cur.execute(query, params).fetchall()
        cur.close()
        return data

    def _db_write_(self, query: str, params: tuple = ()):
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        cur.execute(query, params)
        db.commit()
        cur.close()


class DBRead(DBInit):
    """
    Class which deals with reading data from the database
    """

    def _get_col_name(self):
        db = sqlite3.connect(self.db_path)
        cur = db.execute(f"SELECT * FROM {self.table_name}")
        col_names = [description[0] for description in cur.description]
        db.close()
        return col_names

    def _check_col_name_(self, col_name: str):
        col_names = self._get_col_name()
        if col_name not in col_names:
            raise ColNotFound(f"column '{col_name}' not found in '{self.table_name}' of '{self.db_path}'")

    @staticmethod
    def _data_to_list_(data: list[tuple]):
        """
        list[tuple] -> list(values)
        """
        return [x[0] for x in data]

    def _data_to_dict_(self, data: list[tuple]):
        """
        list[tuple] -> dict(column_name: value)
        """
        col_names = self._get_col_name()
        if len(data) == 1:
            return dict(zip(col_names, data[0]))
        clean_data = []
        for col in data:
            clean_data.append(dict(zip(col_names, col)))
        return clean_data

    def db_fetch_all(self):
        query = f" SELECT * FROM {self.table_name}"
        query_data = self._db_read_(query)
        return self._data_to_dict_(data=query_data)

    def db_fetch_col(self, col_name: str):
        self._check_col_name_(col_name)
        query = f"SELECT {col_name} FROM {self.table_name}"
        query_data = self._db_read_(query)
        clean_data = DBRead._data_to_list_(query_data)
        return clean_data

    def db_fetch_row(self, **where):
        col, value = where.popitem()
        self._check_col_name_(col_name=col)
        query = f"SELECT * FROM {self.table_name} WHERE {col} = ?"
        param = (value,)
        query_data = self._db_read_(query, param)
        if not query_data:
            raise DataNotFound(f"value not found: {col} = {value}")
        return self._data_to_dict_(data=query_data)


class DBWrite(DBInit):
    """
    Class which deals with writing data to the database
    """

    def create_table(self, table: dict[str, dict], pk: bool = True):
        """
        Use dbman.Fields for specifying data types
        pk column is autogenerated with name of 'id'
        :param: table = {"table_name": {"col_name": "data type (dbman.Fields)",...}}
        """
        for table_name, table_details_dict in table.items():
            table_details = ", ".join([f"{col} {data_type}" for col, data_type in table_details_dict.items()])
            if pk:
                pk_col = Fields.PrimaryKey()
                table_details = f"{pk_col}, {table_details}"
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({table_details})"
            self._db_write_(query)

    def _insert_data_(self, table_name: str, col_data: dict):
        cols = ', '.join(col_data.keys())
        values = ', '.join([f"'{value}'" for value in col_data.values()])
        query = f"INSERT INTO {table_name} ({cols}) VALUES ({values})"
        self._db_write_(query)

    def db_insert(self, col_data: dict = None, tabel_data: dict[str: dict] = None):
        if col_data is not None:
            self._insert_data_(table_name=self.table_name, col_data=col_data)

        if tabel_data is not None:
            for table_name, col_data in tabel_data.items():
                self._insert_data_(table_name=table_name, col_data=col_data)


class DBMan(DBRead, DBWrite):
    """
    Base class
    """
    pass
