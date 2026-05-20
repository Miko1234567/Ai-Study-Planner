from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    plans = db.relationship('StudyPlan', backref='author', lazy=True)

class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Жаңа байланыстар: Тапсырмалар мен Квиздер
    tasks = db.relationship('Task', backref='plan', cascade="all, delete-orphan", lazy=True)
    quizzes = db.relationship('QuizQuest', backref='plan', cascade="all, delete-orphan", lazy=True)

# 1-ФИШКА ҮШІН: Әр күннің тапсырмалар чек-листі
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plan.id'), nullable=False)

# 2-ФИШКА ҮШІН: AI жасаған тест сұрақтарын сақтау
class QuizQuest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False) # 'A', 'B', немесе 'C'
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plan.id'), nullable=False)