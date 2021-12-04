from celery import Celery
from celery.utils.log import get_task_logger
import os
import ffmpeg
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..app import create_app
from ..models import db, Task, Status, User
from ..util import util
import time

celery_app = Celery(
    "converter", backend=os.environ.get('REDIS_TLS_URL'), broker=os.environ.get('REDIS_TLS_URL')
)

flask_app = create_app('default')
app_context = flask_app.app_context()
app_context.push()

db.init_app(flask_app)
logger = get_task_logger(__name__)

@celery_app.task(name="convert")
def convert_audio(id: int):
    time.sleep(5)
    # get task
    task = Task.query.get_or_404(id)

    # convert audio file
    if task.status == Status.UPLOADED:
        TEMP_UPLOAD_FOLDER = os.path.abspath(os.getcwd()) + "/files/uploads/"
        TEMP_PROCESSED_FOLDER = os.path.abspath(os.getcwd()) + "/files/processed/"
        S3_UPLOAD_FOLDER =  "files/uploads/"
        S3_PROCESSED_FOLDER =  "files/processed/"
        logger.info("Archivo a procesar")
        try:
            localSourceFile = os.path.join(TEMP_UPLOAD_FOLDER, task.uploaded_file)
            s3SourceFile = S3_UPLOAD_FOLDER + task.uploaded_file
            
            logger.info("Descargar Archivo")
            logger.info("localSourceFile: " + localSourceFile)
            logger.info("s3SourceFile: " + s3SourceFile)
            
            s3file=util.downloadFileS3(s3SourceFile)
            logger.info("Tipo Archivo" + str(type(s3file)))
            logger.info("Archivo descargado: " + s3SourceFile)
            localProcessedFile = os.path.join(TEMP_PROCESSED_FOLDER, task.uploaded_file + "." + task.processed_format.name.lower())
            logger.info("Nuevo archivo local: " + localProcessedFile)
            s3TargetFile=S3_PROCESSED_FOLDER+task.uploaded_file + "." + task.processed_format.name.lower()
            logger.info("Nuevo archivo en S3: " + s3TargetFile)
            ffmpeg.input(localSourceFile).output(localProcessedFile).overwrite_output().run()
            logger.info("Archivo procesado")
            util.uploadFile(localProcessedFile,s3TargetFile)
            logger.info("Archivo subido a S3")
            os.remove(localProcessedFile)
            os.remove(localSourceFile)
            logger.info("Remover archivos locales")

        except BaseException as e:
            e = f" error {e=}, {type(e)=}"
            logger.info(e)

        # change status
        task.status = Status.PROCESSED
        logger.info("Cambiar estado de la tarea")
        task.processed_file = task.uploaded_file + "." + task.processed_format.name.lower()
        db.session.commit()
        logger.info("Actualizar tarea")

        # notify user
        notify_user(task)

        return True
    else:
        return False


def notify_user(task: Task):
    user = User.query.get_or_404(task.user_id)

    msg_body: str = f"""
    ¡Hola, {user.username}!

    Tu tarea de convertir el archivo {task.uploaded_file} a formato {task.processed_format.name}, ha terminado."""

    receiver_email = user.email
    sender_email = "pruebame.de.una@gmail.com"
    sender_pw = "probameya"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Tu archivo ha sido convertido"
    message.attach(MIMEText(msg_body, "plain"))

    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender_email, sender_pw)
    text = message.as_string()
    session.sendmail(sender_email, receiver_email, text)
    session.quit()
