from flaskr import create_app
from flask_restful import Api
from .models import db
from .views import SignUpView, LogInView, TasksView, TaskView, FileView, HealthCheckView
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
cors = CORS(app)

api = Api(app)

api.add_resource(SignUpView, '/api/auth/signup')
api.add_resource(LogInView, '/api/auth/login')
api.add_resource(TasksView, '/api/tasks')
api.add_resource(TaskView, '/api/tasks/<int:id_task>')
api.add_resource(FileView, '/api/files/<filename>')
api.add_resource(HealthCheckView, '/healthcheck')

jwt = JWTManager(app)

if __name__ == "__main__":
    app.run(debug=True)
