import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from app import app
from unittest.mock import patch

app.config.update(TESTING=True, SECRET_KEY='test-secret')
client = app.test_client()

with patch('routes.usuario.mongo.db.usuarios.replace_one', return_value=None) as mock_replace:
    response = client.post('/usuario/registro', data={'rut':'12345678','nombre':'Ana','apellido':'Perez'}, follow_redirects=False)
    print('status', response.status_code)
    print('location', response.headers.get('Location'))
    print('call_count', mock_replace.call_count)
    with client.session_transaction() as session:
        print('session', dict(session))
