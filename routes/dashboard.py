from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Attempt, Quiz

dash_bp = Blueprint('dash', __name__)

@dash_bp.get('/')
@login_required
def student_dashboard():
    attempts = Attempt.query.filter_by(user_id=current_user.id).all()
    # aggregate simple stats
    total_quizzes = len({a.quiz_id for a in attempts})
    total_attempts = len(attempts)
    avg_score = round(sum(a.score for a in attempts)/sum(a.total for a in attempts)*100, 1) if attempts else 0.0
    latest = attempts[-5:] if attempts else []
    quizzes = {q.id: q for q in Quiz.query.all()}
    return render_template('dashboard_student.html',
                           total_quizzes=total_quizzes,
                           total_attempts=total_attempts,
                           avg_score=avg_score,
                           latest=latest,
                           quizzes=quizzes)
