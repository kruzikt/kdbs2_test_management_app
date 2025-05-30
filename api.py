from flask import Blueprint, request, jsonify
from extensions import db
from models import User, Project, TestCase, TestResult, TestStatus
from sqlalchemy.exc import IntegrityError

api = Blueprint('api', __name__)

# --- USERS ---
@api.route('/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'tester')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User already exists'}), 400

@api.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([
        {'id': u.id, 'username': u.username, 'email': u.email, 'role': u.role} for u in users
    ])

# --- PROJECTS ---
@api.route('/projects', methods=['POST'])
def create_project():
    data = request.json
    project = Project(
        name=data['name'],
        description=data.get('description'),
        created_by=data['created_by']
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'id': project.id}), 201

@api.route('/projects', methods=['GET'])
def list_projects():
    projects = Project.query.all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'description': p.description, 'created_by': p.created_by} for p in projects
    ])

# --- TEST CASES ---
@api.route('/testcases', methods=['POST'])
def create_test_case():
    data = request.json
    test_case = TestCase(
        project_id=data['project_id'],
        title=data['title'],
        description=data.get('description'),
        steps=data.get('steps'),
        expected_result=data.get('expected_result'),
        status_id=data['status_id'],
        created_by=data['created_by']
    )
    db.session.add(test_case)
    db.session.commit()
    return jsonify({'id': test_case.id}), 201

@api.route('/testcases', methods=['GET'])
def list_test_cases():
    cases = TestCase.query.all()
    return jsonify([
        {
            'id': c.id,
            'project_id': c.project_id,
            'title': c.title,
            'description': c.description,
            'steps': c.steps,
            'expected_result': c.expected_result,
            'status_id': c.status_id,
            'created_by': c.created_by
        } for c in cases
    ])

# --- TEST RESULTS ---
@api.route('/testresults', methods=['POST'])
def create_test_result():
    data = request.json
    test_result = TestResult(
        test_case_id=data['test_case_id'],
        executed_by=data['executed_by'],
        result_id=data['result_id'],
        notes=data.get('notes')
    )
    db.session.add(test_result)
    db.session.commit()
    return jsonify({'id': test_result.id}), 201

@api.route('/testresults', methods=['GET'])
def list_test_results():
    results = TestResult.query.all()
    return jsonify([
        {
            'id': r.id,
            'test_case_id': r.test_case_id,
            'executed_by': r.executed_by,
            'executed_at': r.executed_at,
            'result_id': r.result_id,
            'notes': r.notes
        } for r in results
    ])

# --- TEST STATUS (číselník) ---
@api.route('/statuses', methods=['GET'])
def list_statuses():
    statuses = TestStatus.query.all()
    return jsonify([
        {'id': s.id, 'name': s.name} for s in statuses
    ])
