from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, StudyPlan, Task, QuizQuest
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ai_service import generate_study_plan, generate_quiz_data
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Базаны қайта құру (Ескі базаны өшіріп, жаңа кестелермен іске қосу үшін)
with app.app_context():
    # Егер бұрын база болса, жаңа кестелер қосылуы үшін оны жаңартамыз
    db.create_all()

@app.route('/')
@login_required
def home():
    user_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', plans=user_plans)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return "Бұл есім бос емес!"
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        return "Қате логин немесе құпия сөз!"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    topic = request.form.get('topic')
    days = request.form.get('days')
    
    ai_content = generate_study_plan(topic, days)
    
    new_plan = StudyPlan(title=topic, duration=int(days), content=ai_content, user_id=current_user.id)
    db.session.add(new_plan)
    db.session.commit()
    
    # Автоматты түрде чек-лист үшін 3 негізгі тапсырма құрып қосамыз
    for i in range(1, int(days) + 1):
        task = Task(text=f"{i}-күннің сабағын оқу және конспектілеу", plan_id=new_plan.id)
        db.session.add(task)
    db.session.commit()
    
    return redirect(url_for('home'))

# 1-ФИШКА: Тапсырманы орындалды/орындалмады деп белгілеу
@app.route('/toggle-task/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('home'))

# 2-ФИШКА: AI Тест құрастыру
@app.route('/make-quiz/<int:plan_id>')
@login_required
def make_quiz(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    # Егер бұрын тест жасалмаған болса, жаңадан AI-дан сұраймыз
    if not plan.quizzes:
        quiz_data = generate_quiz_data(plan.title)
        for q in quiz_data:
            quest = QuizQuest(
                question=q['question'],
                option_a=q['A'],
                option_b=q['B'],
                option_c=q['C'],
                correct_option=q['correct'],
                plan_id=plan.id
            )
            db.session.add(quest)
        db.session.commit()
    return redirect(url_for('home'))

# Тест нәтижесін тексеру
@app.route('/check-quiz/<int:plan_id>', methods=['POST'])
@login_required
def check_quiz(plan_id):
    plan = StudyPlan.query.get_or_404(plan_id)
    score = 0
    total = len(plan.quizzes)
    
    for q in plan.quizzes:
        selected = request.form.get(f"question_{q.id}")
        if selected == q.correct_option:
            score += 1
            
    flash(f"Сіздің нәтижеңіз: {total} сұрақтан {score} дұрыс жауап!")
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_plan(id):
    plan = StudyPlan.query.get_or_404(id)
    if plan.user_id == current_user.id:
        new_title = request.form.get('new_title')
        if new_title:
            plan.title = new_title
            db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
@login_required
def delete_plan(id):
    plan_to_delete = StudyPlan.query.get_or_404(id)
    if plan_to_delete.user_id == current_user.id:
        db.session.delete(plan_to_delete)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)