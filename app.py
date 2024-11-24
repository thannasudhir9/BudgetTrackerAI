from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
db = SQLAlchemy(app)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return jsonify([{
        'id': t.id,
        'description': t.description,
        'amount': t.amount,
        'category': t.category,
        'date': t.date.strftime('%Y-%m-%d'),
        'type': t.type
    } for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    transaction = Transaction(
        description=data['description'],
        amount=float(data['amount']),
        category=data['category'],
        type=data['type']
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction added successfully'})

if __name__ == '__main__':
    app.run(debug=True)
