from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import User
from models.models import Subject, Chapter, Quiz, Question
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


# add routes for quiz management
@admin.route('/quizzes/<int:chapter_id>', methods=['GET', 'POST'])
def manage_quizzes(chapter_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # fetch the chapter
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        date_of_quiz_str = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remark = request.form['remark']

        # Convert the date string to a Python date object
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('admin.manage_quizzes', chapter_id=chapter.id))


        # Create a new quiz under the chapter
        new_quiz = Quiz(
            chapter_id=chapter.id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remark=remark
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")

    # Fetch all quizzes of the chapter to display in the dashboard
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
    return render_template('admin/manage_quizzes.html', chapter=chapter, quizzes=quizzes)


# Add routes for question management
@admin.route('/questions/<int:quiz_id>', methods=['GET', 'POST'])
def manage_questions(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # Fetch the quiz
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']

        # Create a new question under the quiz
        new_question = Question(
            quiz_id=quiz.id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")

    # Fetch all questions for this quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template('admin/manage_questions.html', quiz=quiz, questions=questions)


# Edit Question Route
@admin.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # Fetch the question to edit
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        # Update the question details
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = request.form['correct_option']
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.manage_questions', quiz_id=question.quiz_id))

    # Render the edit form with the existing question details
    return render_template('admin/edit_question.html', question=question)


# Delete Question Route
@admin.route('/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # Fetch the question to delete
    question = Question.query.get_or_404(question_id)

    # Delete the question from the database
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')

    # Redirect back to the manage questions page for the same quiz
    return redirect(url_for('admin.manage_questions', quiz_id=question.quiz_id))


