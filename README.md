# Mad 1 Project: Qize Master App
----------------------------------

### Create env and Activate
`python3 -m venv mad1env`

`source mad1env/bin/activate`  #linux/mac
`mad1env\Scripts\activate`      #windows

### Install the required dependencies and save to req.txt
`pip install flask flask-sqlalchemy flask-login`
`pip freeze > requirements.txt`

### Project structure
`
quiz_master_23f2000606/
├── mad1env/        # Virtual environment
├── static/         # CSS, JS, Images
    ├── css/
    ├── js/
    ├── images/       
├── templates/      # HTML templates
├── app.py          # Main Flask app
├── models/         # Database models
├── routes/         # Routes for admin and user
├── utils/          # Utility functions
├── requirements.txt
`

### Run the app
`flask run`

### Setup the database model

### Connet Flask to SQLite db

