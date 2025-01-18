from flask import Flask
from extension import db

app = Flask(__name__)
app.secret_key = "something"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)    # bind the db to the app

# initialize the db
with app.app_context():
    # importing models
    from models.models import User, Subject, Chapter, Quiz, Question, Score

    # Create the database tables if they don't exist
    db.create_all()

    # Create the admin user if it doesn't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password='admin123',
            full_name='Quiz Master Admin',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created')




@app.route('/')
def home():
    return "Quiz Master App is Running!"

if __name__ == "__main__":
    app.run(debug=True)
