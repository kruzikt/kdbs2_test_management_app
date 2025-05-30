from flask import Flask, render_template, redirect, url_for, request, flash
import os
from api import api
from extensions import db, migrate

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # for flash messages

# Konfigurace připojení k MySQL
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'test_management_app')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
app.register_blueprint(api, url_prefix='/api')

from models import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def list_projects_page():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        created_by = request.form['created_by']
        project = Project(name=name, description=description, created_by=created_by)
        db.session.add(project)
        db.session.commit()
        flash('Project created!')
        return redirect(url_for('list_projects_page'))
    users = User.query.all()
    return render_template('new_project.html', users=users)

@app.route('/testcases')
def list_test_cases_page():
    testcases = TestCase.query.all()
    return render_template('testcases.html', testcases=testcases)

@app.route('/testcases/new', methods=['GET', 'POST'])
def new_test_case():
    if request.method == 'POST':
        project_id = request.form['project_id']
        title = request.form['title']
        description = request.form['description']
        steps = request.form['steps']
        expected_result = request.form['expected_result']
        created_by = request.form['created_by']
        # Nastavit status_id na výchozí hodnotu (např. 'Not Run')
        default_status = TestStatus.query.filter_by(name='Not Run').first()
        testcase = TestCase(
            project_id=project_id,
            title=title,
            description=description,
            steps=steps,
            expected_result=expected_result,
            status_id=default_status.id if default_status else 1,
            created_by=created_by
        )
        db.session.add(testcase)
        db.session.commit()
        # Vytvoření záznamu v test_results
        test_result = TestResult(
            test_case_id=testcase.id,
            executed_by=created_by,
            # result_id není nastavován, trigger v DB nastaví výchozí hodnotu
            notes='Automatically created with test case.'
        )
        db.session.add(test_result)
        db.session.commit()
        flash('Test case created!')
        return redirect(url_for('list_test_cases_page'))
    projects = Project.query.all()
    statuses = TestStatus.query.all()
    users = User.query.all()
    return render_template('new_testcase.html', projects=projects, statuses=statuses, users=users)

@app.route('/users')
def list_users_page():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_hash = request.form['password_hash']
        role = request.form['role']
        user = User(username=username, email=email, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()
        flash('User created!')
        return redirect(url_for('list_users_page'))
    return render_template('new_user.html')

@app.route('/testresults')
def list_test_results_page():
    testresults = TestResult.query.all()
    return render_template('testresults.html', testresults=testresults)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
