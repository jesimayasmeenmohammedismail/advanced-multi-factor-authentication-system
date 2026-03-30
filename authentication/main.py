from website import create_app, db
import time
# import pyotp
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = create_app()

migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run(debug=True)
