from flask import Flask, render_template, redirect, url_for, request, flash
import os
from api import api
from extensions import db, migrate
from sqlalchemy import text

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
    # Získání počtu testů pro každý projekt pomocí DB funkce
    test_counts = {}
    with db.engine.connect() as conn:
        for project in projects:
            result = conn.execute(text('SELECT get_test_count_by_project(:pid) AS test_count'), {'pid': project.id})
            test_counts[project.id] = result.scalar() or 0
    return render_template('projects.html', projects=projects, test_counts=test_counts)

@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        created_by = request.form['created_by']
        config = request.form.get('configuration')
        config_error = None
        project = Project(name=name, description=description, created_by=created_by)
        if config:
            import json
            try:
                project.configuration = json.loads(config)
            except Exception:
                config_error = 'Project configuration is not valid JSON.'
        if config_error:
            users = User.query.all()
            return render_template('new_project.html', users=users, config_error=config_error, name=name, description=description, created_by=created_by, configuration=config)
        db.session.add(project)
        db.session.commit()
        flash('Project created!')
        return redirect(url_for('list_projects_page'))
    users = User.query.all()
    return render_template('new_project.html', users=users)

@app.route('/testcases')
def list_test_cases_page():
    project_id = request.args.get('project_id', type=int)
    projects = Project.query.all()
    if project_id:
        testcases = TestCase.query.filter_by(project_id=project_id).all()
    else:
        testcases = TestCase.query.all()
    # Získání posledních výsledků z pohledu v_last_test_result
    last_results = {}
    with db.engine.connect() as conn:
        if project_id:
            ids = tuple(tc.id for tc in testcases)
            if ids:
                placeholders = ','.join([str(i) for i in ids])
                sql = f'SELECT * FROM v_last_test_result WHERE test_case_id IN ({placeholders})'
                result = conn.execute(text(sql))
            else:
                result = []
        else:
            result = conn.execute(text('SELECT * FROM v_last_test_result'))
        for row in result:
            row_map = row._mapping if hasattr(row, '_mapping') else row
            last_results[row_map['test_case_id']] = {'result': row_map['result'], 'executed_at': row_map['executed_at']}
    return render_template('testcases.html', testcases=testcases, projects=projects, selected_project_id=project_id, last_results=last_results)

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
