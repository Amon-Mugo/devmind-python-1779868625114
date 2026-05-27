from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import NotFound, BadRequest, InternalServerError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'description': self.description, 'completed': self.completed}

# Create the database tables
with app.app_context():
    db.create_all()

# Create a new todo item
@app.route('/todos', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('No data provided')
        if 'title' not in data or 'description' not in data:
            raise BadRequest('Title and description are required')
        new_todo = Todo(title=data['title'], description=data['description'])
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get all todo items
@app.route('/todos', methods=['GET'])
def get_all_todos():
    try:
        todos = Todo.query.all()
        return jsonify([todo.to_dict() for todo in todos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get a single todo item
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo is None:
            raise NotFound('Todo not found')
        return jsonify(todo.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a todo item
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo is None:
            raise NotFound('Todo not found')
        data = request.get_json()
        if 'title' in data:
            todo.title = data['title']
        if 'description' in data:
            todo.description = data['description']
        if 'completed' in data:
            todo.completed = data['completed']
        db.session.commit()
        return jsonify(todo.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete a todo item
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        if todo is None:
            raise NotFound('Todo not found')
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'Todo deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)