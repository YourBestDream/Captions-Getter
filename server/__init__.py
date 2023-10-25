import os 
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     f'postgresql://{os.environ.get("POSTGRES_USER").strip()}:'  # username
#     f'{os.environ.get("POSTGRES_PASSWORD").strip()}@'  # password
#     f'{os.environ.get("POSTGRES_URL").strip()}/'  # host:port
#     f'{os.environ.get("POSTGRES_DATABASE").strip()}'  # database_name
# )
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://postgres:'  # username
    f'{"postgres"}@'  # password
    f'{"localhost:5432"}/'  # host:port
    f'{"wise_back"}'  # database_name
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



CORS(app)
db = SQLAlchemy(app)
# CORS(app, resources={r"/results/stats": {"origins": "*"}})

from server import views