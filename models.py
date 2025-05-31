from extensions import db
from datetime import datetime

class TestStatus(db.Model):
    __tablename__ = 'test_status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('tester', 'manager', 'admin'), default='tester', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    configuration = db.Column(db.JSON)  # Přidán sloupec pro JSON konfiguraci
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator = db.relationship('User', backref='projects')

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    steps = db.Column(db.Text)
    expected_result = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey('test_status.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = db.relationship('Project', backref='test_cases')
    status = db.relationship('TestStatus')
    creator = db.relationship('User')

class TestResult(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    result_id = db.Column(db.Integer, db.ForeignKey('test_status.id'), nullable=False)
    notes = db.Column(db.Text)
    test_case = db.relationship('TestCase', backref='test_results')
    executor = db.relationship('User')
    result_status = db.relationship('TestStatus')
