from flask import Flask

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.secret_key = ' '
# app.config.from_object(__name__)
username, password, db_name = 'tej', 'tej', 'project_x'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'+username+':'+password+'@localhost/'+db_name
app.config['SECRET_KEY'] = 'c1989fb8f7b52552a80bb11fda1403080c346328'

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

import pytz
indianTime = pytz.timezone('Asia/Kolkata')
from src import models, backendRoutes, frontendRoutes, dbOps
