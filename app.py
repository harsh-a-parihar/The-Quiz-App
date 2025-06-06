from flask import Flask, render_template
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from extension import db
from routes.admin_routes import admin
from routes.user_routes import user

app = Flask(__name__)
app.secret_key = "something"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(admin, url_prefix='/admin')  # register the admin blueprint
app.register_blueprint(user, url_prefix='/user')    # register the user blueprint

db.init_app(app)    # bind the db to the app
migrate = Migrate(app, db)  # bind the migrate to the app

# initialize the db
with app.app_context():
    # importing models 
    from models.models import User, Subject, Chapter, Quiz, Question, Score

    # Create the database tables if they don't exist
    db.create_all()

    # Create the admin user if it doesn't exist
    # if not User.query.filter_by(username='admin').first():
    #     admin = User(
    #         username='admin',
    #         password='admin123',
    #         full_name='Quiz Master Admin',
    #         is_admin=True
    #     )
    #     db.session.add(admin)
    #     db.session.commit()
    #     print('Admin user created')



# import the routes
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
