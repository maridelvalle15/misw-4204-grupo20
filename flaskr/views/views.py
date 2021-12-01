from functools import total_ordering
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from flask import request
from ..models import db, User, UserSchema, Task, TaskSchema, Status
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import os
from flask import flash, request, redirect, url_for, send_from_directory, Response
from werkzeug.utils import secure_filename
from sqlalchemy import desc
from celery import Celery
from ..util import util
import datetime

celery_app = Celery(
    "converter", backend="redis://172.31.28.3:6379", broker="redis://172.31.28.3:6379"
)

usuario_schema = UserSchema()
task_schema = TaskSchema()

UPLOADED_FOLDER = 'files/uploads/'
PROCESSED_FOLDER = "files/processed/"

class SignUpView(Resource):

    def post(self):
        if request.json["password1"] != request.json["password2"] :
            return {"message":"La confirmación de la contraseña es inválida"}, 400

        usuario = User.query.filter(User.username == request.json["username"]).first()
        if usuario is not None:
            return {"message":"El usuario ya existe"}, 400
        usuario = User.query.filter(User.email == request.json["email"]).first()
        if usuario is not None:
            return {"message":"El usuario ya existe"}, 400

        nuevo_usuario = User(username=request.json["username"], password=request.json["password1"], email=request.json["email"])
        db.session.add(nuevo_usuario)
        db.session.commit()
        return {"message":"usuario creado exitosamente"}, 200

class LogInView(Resource):

    def post(self):
        
        usuario = User.query.filter(User.username == request.json["username"], User.password == request.json["password"]).first()
        db.session.commit()
        if usuario is None:
            return {"message":"El usuario no existe"}, 404
        else:
            expire_date =  datetime.timedelta(days=1)
            token_de_acceso = create_access_token(identity = usuario.id,expires_delta = expire_date)
            return {"message":"Inicio de sesión exitoso", "token": token_de_acceso}

class TasksView(Resource):

    @jwt_required()
    def get(self):

        max = request.args.get('max') if request.args.get('max') is not None else 0
        order = request.args.get('order') if request.args.get('order') is not None else 0
        user_id = get_jwt_identity()
        tasks = Task.query.filter(Task.user_id == user_id)
        tasks = tasks.order_by(Task.id) if order == 0 else tasks.order_by(desc(Task.id))
        tasks = tasks.all() if max != 0 else tasks.limit(max).all()

        return [task_schema.dump(task) for task in tasks ]

    @jwt_required()
    def post(self):

        if 'fileName' not in request.files:
            return {"message":"No se encuentra el archivo para convertir en la solicitud "}, 400

        file = request.files['fileName']

        if file.filename == '':
            return {"message":"Nombre del archivo inválido (Sin un nombre). No es posible determinar el formato"}, 400

        fileName = file.filename
        original_format = os.path.splitext(fileName)[1].upper().replace('.','')
        new_format=request.form["newFormat"].upper()
        content_type = request.mimetype

        if original_format == new_format :
            return {"message":"Formato inválido. Seleccione un formato diferente de conversión"}, 400

        ALLOWED_EXTENSIONS = {'mp3', 'aac', 'ogg', 'wav', 'wma'}

        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            file_name = "files/uploads/" + filename
            print(file_name)
            util.uploadFileS3(file, file_name,content_type )
            id_user = get_jwt_identity()
            new_task = Task(
                uploaded_file=filename,
                uploaded_format=original_format,
                processed_format=new_format,
                user_id=id_user)
            db.session.add(new_task)
            try:
                db.session.commit()
                celery_app.send_task("convert", [new_task.id])
            except IntegrityError:
                db.session.rollback()
                return {"message":'Error interno en la aplicación'},500

            return {"message":"Tarea creada exitosamente"}, 200

        return {"message":"Archivo inválido"}, 400

class TaskView(Resource):

    @jwt_required()
    def get(self, id_task):
        task = Task.query.filter(Task.id == id_task).first()
        if task is None:
            return {"message":"La tarea no existe"}, 400
        return task_schema.dump(task), 200

    @jwt_required()
    def put(self, id_task):
        task = Task.query.get_or_404(id_task)

        if task.uploaded_format == request.json['newFormat'].upper():
            return {"message":"Formato inválido. Seleccione un formato diferente de conversión"}, 400
        task.processed_format = request.json['newFormat'].upper()

        if task.status == Status.PROCESSED:
            if util.checkFileExists(PROCESSED_FOLDER+task.processed_file) :
                util.deleteFile(PROCESSED_FOLDER+task.processed_file)

        task.status = 'UPLOADED'
        db.session.commit()

        celery_app.send_task("convert", [task.id])

        return task_schema.dump(task)

    @jwt_required()
    def delete(self,id_task):
        task = Task.query.get_or_404(id_task)
        if task.status == Status.PROCESSED:
            if util.checkFileExists(UPLOADED_FOLDER+task.uploaded_file) :
                util.deleteFile(UPLOADED_FOLDER+task.uploaded_file)
            if util.checkFileExists(PROCESSED_FOLDER+task.processed_file) :
                util.deleteFile(PROCESSED_FOLDER+task.processed_file)
            db.session.delete(task)
            db.session.commit()
            return ('', 204)
        return {"mensaje":"No es posible eliminar el archivo en estado UPLOADED " }, 400

class FileView(Resource):

    @jwt_required()
    def get(self, filename):

        if util.checkFileExists(UPLOADED_FOLDER+filename) :
            return Response(util.downloadFileS3(UPLOADED_FOLDER+filename), content_type='audio/mpeg')
        if util.checkFileExists(PROCESSED_FOLDER+filename) :
            return Response(util.downloadFileS3(PROCESSED_FOLDER+filename), content_type='audio/mpeg')
        return {"mensaje":"Archivo inválido. Dicho archivo no existe"}, 400
    
class HealthCheckView(Resource):
    def get(self):
        return {"mensaje":"Service UP"}, 200

