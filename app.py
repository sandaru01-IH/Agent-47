from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income or expense
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.id}>"


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    balance = sum(t.amount if t.type == 'income' else -t.amount for t in transactions)
    return render_template('index.html', transactions=transactions, balance=balance)


@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        ttype = request.form['type']
        transaction = Transaction(description=description, amount=amount, type=ttype)
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_transaction.html')


@app.route('/invoice/<int:transaction_id>')
def invoice(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('invoice.html', transaction=transaction)


if __name__ == '__main__':
    app.run(debug=True)
