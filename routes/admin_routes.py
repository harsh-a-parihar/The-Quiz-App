from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import User
from models.models import Subject, Chapter
from extension import db

admin = Blueprint('admin', __name__)


# admin login route
@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        # check if the user is admin
        admin_user = User.query.filter_by(username=username, is_admin=True).first()

        if admin_user and admin_user.password == password:
            # login susccessful
            session['admin_logged_in'] = True
            flash('Login Successful', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid Credentials!', 'danger')
        
    return render_template('admin/login.html')


# admin dashboard route
@admin.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Render the admin dashboard template
    return render_template('admin/dashboard.html')


# Admin subjects management route
@admin.route('/subjects', methods=['GET', 'POST'])
def manage_subjects():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Create a new subject
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully!", "success")

    # Fetch all subjects to display in the dashboard
    subjects = Subject.query.all()
    return render_template('admin/manage_subjects.html', subjects=subjects)


# Admin logout route
@admin.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('admin.admin_login'))

# Add Chapter Route
@admin.route('/chapters/<int:subject_id>', methods=['GET', 'POST'])
def manage_chapters(subject_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Fetch the subject
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        # Create a new chapter under the subject
        new_chapter = Chapter(name=name, description=description, subject_id=subject.id)
        db.session.add(new_chapter)
        db.session.commit()
        flash("chapter added successfully!", "success")

    # Fetch all chapters of the subject to display in the dashboard
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    return render_template('admin/manage_chapters.html', subject=subject, chapters=chapters)