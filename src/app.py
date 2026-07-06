import os
from flask import Flask, render_template
from dotenv import load_dotenv
from config.mongodb import mongo
from routes.usuario import usuario
from routes.calificar import calificar
from routes.mascota import mascota

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/huellitas')
mongo.init_app(app)

@app.route('/')
def hello():
    return render_template('index.html')

app.register_blueprint(usuario, url_prefix='/usuario')
app.register_blueprint(calificar, url_prefix='/calificar')
app.register_blueprint(mascota, url_prefix='/mascota')

if __name__ == '__main__':
    app.run(debug=True)