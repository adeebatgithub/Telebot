from .dbman import DBMan
from .dbman import DataNotFoundError

class Manager(DBMan):

    def __init__(self, base_cls):
        self.base_cls = base_cls
        self.table_name = self.base_cls.__name__.lower()
        self.default_keys = ("__module__", "__qualname__", "__doc__", "object")
        self.attrs = self.base_cls.__dict__

        self._create_table_()

    def _create_table_(self):
        table = {k: v for k,v in self.attrs.items() if k not in self.default_keys}
        tables = self._get_table_names_()
        if self.table_name not in tables:
            self.db_create_table(table)
            print(f"Table Created: {self.table_name}")


    def _get_id_(self):
        query = f"SELECT * FROM {self.table_name} ORDER BY id DESC LIMIT 1"
        query_data = self._db_read_(query)
        clean_data = self._data_to_list_(query_data)
        if clean_data:
            return clean_data[0] + 1
        return 1

    def _db_insert_(self, data):
        self.db_insert(data)

    def _db_update_(self, data):
        self.db_update(col_data=data, id=data["id"])

    def _is_exists_(self, **where):
        try:
            self.db_fetch_row(**where)
        except DataNotFoundError:
            return False
        return True

    def all(self):
        return self.db_fetch_all()

    def get(self, **where):
        data = self.db_fetch_row(**where)
        for k,v in data[0].items():
            setattr(self.base_cls, k, v)

        return self.base_cls


class DBMeta(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        if name not in ["DBMeta", "DBMAN"]:
            cls.object = Manager(cls)
    
    def __call__(cls, *args, **kwargs):
        id = cls.object._get_id_()
        cls.id = id
        for col, value in kwargs.items():
            processed_value = dict(cls.__dict__)[col].process_value(value)
            setattr(cls, col, processed_value)
        return type.__call__(cls, cls.__name__, cls.__bases__, dict(cls.__dict__), **kwargs)

    def __setattr__(cls, name, value):

        if name in cls.__dict__ or name in ("object", "id"):
            if "object" in cls.__dict__:
                if name != "id":
                    value = cls.object.attrs[name].process_value(value)

            return type.__setattr__(cls, name, value)
        
        raise ValueError(f"{name} is not a field")

    def save(cls):
        default_keys = ["__module__", "__qualname__", "__doc__", "object"]
        data = {k: v for k,v in cls.__dict__.items() if k not in default_keys}
        if cls.object._is_exists_(id=data["id"]):
            cls.object._db_update_(data)
        else:
            cls.object._db_insert_(data)



class DBMAN(metaclass=DBMeta):
    
    def __new__(self, name, bases, attrs, **kwargs):
        return type.__new__(DBMeta, name, bases, attrs)

