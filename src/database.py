from peewee import *
from config import config

db = SqliteDatabase(config.db_path)

class BaseModel(Model):
    id = AutoField(primary_key=True)
    class Meta:
        database = db

class ForwardRule(BaseModel):
    from_qube = CharField()
    from_port = IntegerField()
    to_qube = CharField()
    to_port = IntegerField()
    pid = IntegerField(null=True)
    
    def __str__(self):
        return f"{self.from_qube}:{self.from_port}@{self.to_qube}:{self.to_port}"

db.create_tables([ForwardRule])