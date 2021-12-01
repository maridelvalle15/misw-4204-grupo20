from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship
import enum

db = SQLAlchemy()

class Format(enum.Enum):
    MP3 = enum.auto()
    AAC = enum.auto()
    OGG = enum.auto()
    WAV = enum.auto()
    WMA = enum.auto()


class Status(enum.Enum):
    UPLOADED = enum.auto()
    PROCESSED = enum.auto()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    tasks = db.relationship('Task', cascade='all, delete, delete-orphan')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    status = db.Column(db.Enum(Status), default='UPLOADED')
    uploaded_file = db.Column(db.String(256), nullable=False)
    uploaded_format = db.Column(db.Enum(Format))
    processed_file = db.Column(db.String(256))
    processed_format = db.Column(db.Enum(Format))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"key": value.name, "value": value.value}


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
         model = User
         include_relationships = True
         load_instance = True


class TaskSchema(SQLAlchemyAutoSchema):
    status = EnumADiccionario(attribute=("status"))
    uploaded_format = EnumADiccionario(attribute=("uploaded_format"))
    processed_format = EnumADiccionario(attribute=("processed_format"))
    class Meta:
         model = Task
         include_relationships = True
         load_instance = True