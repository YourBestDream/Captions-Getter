import os 
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sqla
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Loading the environment variables from file using dotenv
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{os.environ.get("POSTGRES_USER").strip()}:'  # username
    f'{os.environ.get("POSTGRES_PASSWORD").strip()}@'  # password
    f'{os.environ.get("POSTGRES_URL").strip()}/'  # host:port
    f'{os.environ.get("POSTGRES_DATABASE").strip()}'  # database_name
)

# # Hardcoding the database URI for now
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     f'postgresql://postgres:'  # username
#     f'{"postgres"}@'  # password
#     f'{"localhost:5432"}/'  # host:port
#     f'{"postgres"}'  # database_name
# )
# print(app.config['SQLALCHEMY_DATABASE_URI'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)
# CORS(app, resources={r"/results/stats": {"origins": "*"}})

from server import views