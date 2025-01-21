from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import User
from extension import db
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import Subject, Chapter, Quiz, Question, Score


user = Blueprint('user', __name__)

# User Registration
@user.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('user.register'))

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password, full_name=full_name)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('user.login'))

    return render_template('user/register.html')

# User Login
@user.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verify user
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_logged_in'] = True
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('user/login.html')

# User Logout
@user.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.login'))

# User Dashboard
@user.route('/dashboard')
def dashboard():
    if not session.get('user_logged_in'):
        return redirect(url_for('user.login'))

    # Render the dashboard template
    return render_template('user/dashboard.html', username=session['user_name'])


# List Subjects
@user.route('/subjects')
def list_subjects():
    if not session.get('user_logged_in'):
        return redirect(url_for('user.login'))

    subjects = Subject.query.all()
    return render_template('user/subjects.html', subjects=subjects)

# List Chapters under a Subject
@user.route('/chapters/<int:subject_id>')
def list_chapters(subject_id):
    if not session.get('user_logged_in'):
        return redirect(url_for('user.login'))

    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    return render_template('user/chapters.html', subject=subject, chapters=chapters)

# List Quizzes under a Chapter
@user.route('/quizzes/<int:chapter_id>')
def list_quizzes(chapter_id):
    if not session.get('user_logged_in'):
        return redirect(url_for('user.login'))

    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
    return render_template('user/quizzes.html', chapter=chapter, quizzes=quizzes)


# Take Quiz
@user.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)

    if request.method == 'POST':
        # Ensure `total_questions` is checked before any calculations
        if total_questions == 0:
            return render_template('user/no_questions.html', quiz=quiz)

        user_answers = request.form
        score = 0

        for question in questions:
            correct_option = str(question.correct_option)
            user_answer = user_answers.get(f'question_{question.id}')
            # Debugging output
            print(f"Question ID: {question.id}, Correct Option: {correct_option}, User Answer: {user_answer}")
            
            # Perform a case-insensitive comparison, if needed
            if user_answer and user_answer.strip().lower() == correct_option.strip().lower():
                score += 1

        percentage = (score / total_questions) * 100


        return render_template('user/quiz_result.html', quiz=quiz, score=score, total=total_questions, percentage=percentage)

    # Handle GET requests
    if total_questions == 0:
        return render_template('user/no_questions.html', quiz=quiz)

    return render_template('user/attempt_quiz.html', quiz=quiz, questions=questions)
