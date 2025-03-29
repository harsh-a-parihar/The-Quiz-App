from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from extension import db
from models.models import User, Subject, Chapter, Quiz, Question

admin = Blueprint('admin', __name__)

#####################################
# Admin Auth / Login / Register
#####################################

@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin_user = User.query.filter_by(username=username, is_admin=True).first()

        if admin_user and check_password_hash(admin_user.password, password):
            session['admin_logged_in'] = True
            session['admin_name'] = admin_user.full_name
            flash('Login Successful', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid Credentials!', 'danger')
    return render_template('admin/login.html')


@admin.route('/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['full_name']
        dob_str = request.form['dob']
        qualification = request.form['qualification']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('admin.admin_register'))

        # Convert DOB
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format! Please use YYYY-MM-DD.", "danger")
            return redirect(url_for('admin.admin_register'))

        # Check username
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin.admin_register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_admin = User(
            username=username,
            password=hashed_password,
            is_admin=True,
            full_name=full_name,
            dob=dob,
            qualification=qualification
        )
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin account created successfully! Please log in.', 'success')
        return redirect(url_for('admin.admin_login'))

    return render_template('admin/register.html')


@admin.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_name', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))


#####################################
# Admin Dashboard
#####################################

@admin.route('/dashboard')
def dashboard():
    """
    Show some overall stats + the subjects/chapters overview.
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    subjects_count = Subject.query.count()
    chapters_count = Chapter.query.count()
    quizzes_count = Quiz.query.count()
    questions_count = Question.query.count()

    subjects = Subject.query.all()

    return render_template(
        'admin/dashboard.html',
        subjects_count=subjects_count,
        chapters_count=chapters_count,
        quizzes_count=quizzes_count,
        questions_count=questions_count,
        subjects=subjects
    )

#####################################
# Subjects
#####################################

@admin.route('/subjects', methods=['GET'])
def subjects():
    """
    Just a separate page listing all subjects.
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)


@admin.route('/add_subject', methods=['POST'])
def add_subject():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    subject_name = request.form.get('subject_name')
    description = request.form.get('description', '')

    existing_subject = Subject.query.filter_by(name=subject_name).first()
    if existing_subject:
        flash('Subject already exists!', 'danger')
        return redirect(url_for('admin.dashboard'))

    new_subject = Subject(name=subject_name, description=description)
    db.session.add(new_subject)
    db.session.commit()

    flash('New subject added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/edit_subject/<int:subject_id>', methods=['POST'])
def edit_subject(subject_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form['subject_name']
    subject.description = request.form['description']
    db.session.commit()

    flash('Subject updated successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    subject = Subject.query.get_or_404(subject_id)
    # Also remove chapters
    Chapter.query.filter_by(subject_id=subject_id).delete()

    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))


#####################################
# Questions Management
#####################################

@admin.route('/questions/<int:quiz_id>', methods=['GET', 'POST'])
def manage_questions(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # Fetch the quiz using the provided quiz_id
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        # Process the form data to add a new question
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = request.form['correct_option']

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
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.manage_questions', quiz_id=quiz.id))

    # For GET request, fetch all questions for this quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template('admin/manage_questions.html', quiz=quiz, questions=questions)


@admin.route('/questions/edit/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # Fetch the question to edit
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        # Update the question details with form data
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = request.form['correct_option']

        db.session.commit()
        flash("Question updated successfully!", "success")
        return redirect(url_for('admin.manage_questions', quiz_id=question.quiz_id))

    return render_template('admin/edit_question.html', question=question)


@admin.route('/questions/delete/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id  # store quiz id to redirect back
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))

#####################################
# Chapters
#####################################

@admin.route('/get_chapters/<int:subject_id>')
def get_chapters(subject_id):
    """
    Returns JSON list of chapters for the given subject.
    Used by the front-end JS to populate the chapter dropdown.
    """
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"chapters": []})

    chapters_data = [
        {"id": c.id, "name": c.name} for c in subject.chapters
    ]
    return jsonify({"chapters": chapters_data})


@admin.route('/add_chapter/<int:subject_id>', methods=['POST'])
def add_chapter(subject_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    chapter_name = request.form['chapter_name']
    description = request.form.get('description', '')

    new_chapter = Chapter(name=chapter_name, description=description, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()

    flash('Chapter added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/edit_chapter/<int:chapter_id>', methods=['POST'])
def edit_chapter(chapter_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    chapter = Chapter.query.get_or_404(chapter_id)
    chapter.name = request.form['chapter_name']
    chapter.description = request.form['description']
    db.session.commit()

    flash('Chapter updated successfully!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()

    flash('Chapter deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))


#####################################
# Quizzes
#####################################

@admin.route('/quizzes', methods=['GET'])
def quizzes():
    """
    We will fetch all quizzes (and from each quiz we can access quiz.chapter, quiz.chapter.subject).
    Then in the template we do the card-based layout.
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # We also need all subjects for the <select> (Subject) in "Add Quiz" form
    subjects = Subject.query.all()
    # All quizzes
    quizzes = Quiz.query.all()

    return render_template('admin/quizzes.html', subjects=subjects, quizzes=quizzes)


@admin.route('/quizzes/add/<int:chapter_id>', methods=['POST'])
def add_quiz(chapter_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    chapter = Chapter.query.get_or_404(chapter_id)
    date_str = request.form['date_of_quiz']   # e.g. "2025-03-01"
    time_duration = request.form['time_duration']
    remark = request.form['remark']

    # Convert date_str into a real Python date object:
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format! Please use YYYY-MM-DD.", "danger")
        return redirect(url_for('admin.quizzes'))

    new_quiz = Quiz(
        chapter_id=chapter.id,
        date_of_quiz=date_obj,  # pass the date object here
        time_duration=time_duration,
        remark=remark
    )
    db.session.add(new_quiz)
    db.session.commit()
    flash('Quiz added successfully!', 'success')
    return redirect(url_for('admin.quizzes'))


@admin.route('/quizzes/edit/<int:quiz_id>', methods=['POST'])
def edit_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    quiz = Quiz.query.get_or_404(quiz_id)

    date_str = request.form['date_of_quiz']
    time_duration = request.form['time_duration']
    remark = request.form['remark']

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format! Please use YYYY-MM-DD.", "danger")
        return redirect(url_for('admin.quizzes'))

    quiz.date_of_quiz = date_obj
    quiz.time_duration = time_duration
    quiz.remark = remark

    db.session.commit()
    flash('Quiz updated successfully!', 'success')
    return redirect(url_for('admin.quizzes'))


@admin.route('/quizzes/delete/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quizzes'))


#####################################
# Summary
#####################################
@admin.route('/summary')
def summary():
    """
    Summarize data in charts. For example:
    - Subject-wise top scores
    - Subject-wise user attempts
    - (Any other interesting stats)
    """
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # EXAMPLE: We'll create some placeholder lists for demonstration.
    # In reality, you'd gather these from your Score or Quiz or Chapter models.

    # Let's say we want to gather data for each Subject:
    #   - 'attempts' = how many total attempts (across all quizzes in that subject)
    #   - 'top_score' = the highest score for that subject
    #   - 'avg_score' = the average score for that subject, etc.

    import random

    subject_data = []
    subjects = Subject.query.all()

    for sub in subjects:
        # Hypothetically: 
        # attempts = Score.query.join(Quiz).join(Chapter).filter(Chapter.subject_id == sub.id).count()
        # top_score = ...
        # For demonstration, let's just use random integers:

        attempts = random.randint(10, 100)
        top_score = random.randint(50, 100)

        subject_data.append({
            'name': sub.name,
            'attempts': attempts,
            'top_score': top_score
        })

    # This subject_data is a list of dicts, e.g.:
    # [
    #   {"name": "Life", "attempts": 52, "top_score": 89},
    #   {"name": "Love is Everything.", "attempts": 90, "top_score": 95},
    #   ...
    # ]

    return render_template(
        'admin/summary.html',
        subject_data=subject_data
    )