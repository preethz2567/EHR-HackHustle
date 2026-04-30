from flask import Flask
from flask_cors import CORS
from routes import patient, doctor, admin
from config import Config
from utils.logger import setup_logger

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

setup_logger()

# Register blueprints
app.register_blueprint(patient.bp, url_prefix='/api')
app.register_blueprint(doctor.bp, url_prefix='/api')
app.register_blueprint(admin.bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
