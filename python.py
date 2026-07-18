from backend.extensions import db
from backend.models import User, Room
from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///triviaverse.db'
db.init_app(app)

with app.app_context():
    db.create_all()

exit()