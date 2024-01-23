
class SizeError(Exception):
    """
    Raise Exception when the given size is not in the limit of the specified date type
    """
    pass

class Field:

    data_type: str = None
    
    def __init__(self, size: int = 0, null: bool = False, unique: bool = False):

        self.size = size
        self.null = null
        self.unique = unique

        self.max_sizes = {
            "CHAR": 255,
            "VARCHAR": 65535,
            "TEXT": 65535,
            "INT": 255,
            "FLOAT": 255,
        }
    
    def _check_size_(self,  size: int):
        if size < 0:
            raise SizeError

        if size > self.max_sizes[self.data_type]:
            raise SizeError("provided size is greater than the limit")

    def _generate_field_(self, size: int, null: bool, unique: bool):
        self._check_size_(size)
        field = f"{self.data_type}"
        if size != 0:
            field += f"({size})"

        if not null:
            field += " NOT NULL"

        if unique:
            field += " UNIQUE"

        return field

    def get_query(self):
        return self._generate_field_(self.size, self.null, self.unique)

    def process_value(self, value):
        if self.size == 0:
            self.size = self.max_sizes[self.data_type]

        if len(value) > self.size:
            SizeError("length of value is greater than the limit")

        return value
        

class CharField(Field):

    data_type = "CHAR"


class VarCharField(Field):

    data_type = "VARCHAR"


class TextField(Field):

    data_type = "TEXT"


class IntField(Field):

    data_type = "INT"

    def process_value(self, value):
        super().process_value(value)
        if type(value) is not int:
            try:
                value = int(value)
            except:
                raise TypeError(f"expected int got {type(value)}")

        return value


class FloatField(Field):

    data_type = "FLOAT"

    def process_value(self, value):
        super().process_value(value)
        if type(value) is not float:
            try:
                value = float(value)
            except:
                raise TypeError(f"expected float got {type(value)}")

        return value


class PrimaryKeyField:

    def __init__(self, engine: str, col_name: str = "id"):
        self.engine = engine
        self.name = col_name

    def get_query(self):
        if self.engine == "sqlite":
            return f"{self.name} INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL"

        if self.engine in ("psql", "postgresql", "postgres"):
            return f"{self.name} SERIAL PRIMARY KEY"


class ForeignKeyField:

    def __init__(self, col_name: str, foreign_table_name: str):
        self.name = col_name

    def get_query(self):
        return f"INTEGER NOT NULL, FOREIGN KEY ({col_name}) REFERENCES {foreign_table}(id)"
