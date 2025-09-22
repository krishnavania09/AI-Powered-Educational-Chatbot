from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models import db, Quiz, Question, Attempt

quiz_bp = Blueprint('quiz', __name__)

def _seed_quiz_if_empty():
    if Quiz.query.count() == 0:
        qz = Quiz(title='Intro Quiz', topic='General')
        db.session.add(qz); db.session.commit()
        qs = [
            Question(quiz_id=qz.id, text='What is AI?', option_a='Artificial Intelligence', option_b='Awesome Icecream', option_c='Air Intake', option_d='None', correct='A'),
            Question(quiz_id=qz.id, text='RAG stands for?', option_a='Read-Answer-Generate', option_b='Retrieval-Augmented Generation', option_c='Random AI Guessing', option_d='Recurrent Agent Graph', correct='B'),
        ]
        db.session.add_all(qs); db.session.commit()

@quiz_bp.get('/')
@login_required
def list_quizzes():
    _seed_quiz_if_empty()
    quizzes = Quiz.query.filter_by(is_active=True).all()
    return render_template('quiz_list.html', quizzes=quizzes)

@quiz_bp.get('/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_take.html', quiz=quiz, questions=questions)

@quiz_bp.post('/<int:quiz_id>/submit')
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    score = 0
    for q in questions:
        ans = request.form.get(f'q{q.id}')
        if ans and ans.upper() == q.correct.upper():
            score += 1
    attempt = Attempt(user_id=current_user.id, quiz_id=quiz_id, score=score, total=len(questions))
    db.session.add(attempt); db.session.commit()
    return redirect(url_for('quiz.result', attempt_id=attempt.id))

@quiz_bp.get('/result/<int:attempt_id>')
@login_required
def result(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)
    quiz = Quiz.query.get_or_404(attempt.quiz_id)
    return render_template('quiz_result.html', attempt=attempt, quiz=quiz)
    