import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app, db, Transaction


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_add_and_invoice(client):
    response = client.post('/add', data={'description': 'Test', 'amount': '100', 'type': 'income'}, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        t = Transaction.query.first()
        assert t.amount == 100
    response = client.get('/invoice/1')
    assert b'Invoice #1' in response.data
