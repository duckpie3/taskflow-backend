import unittest
import json
import os
from app import app, db, User, Task


class TaskFlowTestCase(unittest.TestCase):

    def setUp(self):
        """Configure test mode: unit (test client) or integration (HTTP)."""
        self.integration = os.getenv('INTEGRATION') == '1' or bool(os.getenv('BASE_URL'))
        self.base_url = os.getenv('BASE_URL', 'http://localhost:5000')

        if self.integration:
            # Lazy import to avoid dependency when not needed
            import requests  # noqa: F401
            # Quick health check so tests fail if server isn't running
            try:
                import requests
                r = requests.get(f"{self.base_url}/api/health", timeout=3)
                assert r.status_code == 200, "Health check failed"
            except Exception as e:
                raise AssertionError(f"Backend not reachable at {self.base_url}: {e}")
        else:
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            self.app = app.test_client()
            # Ensure a clean schema per test
            with app.app_context():
                db.drop_all()
                db.create_all()

    # Simple HTTP wrappers to unify unit/integration modes
    def _with_headers(self, headers):
        base = {'Content-Type': 'application/json'}
        if headers:
            base.update(headers)
        return base

    def _post(self, path, data=None, headers=None):
        if self.integration:
            import requests
            return requests.post(self.base_url + path, data=data, headers=self._with_headers(headers), timeout=5)
        return self.app.post(path, data=data, headers=headers, content_type='application/json')

    def _get(self, path, headers=None):
        if self.integration:
            import requests
            return requests.get(self.base_url + path, headers=self._with_headers(headers), timeout=5)
        return self.app.get(path, headers=headers)

    def _put(self, path, data=None, headers=None):
        if self.integration:
            import requests
            return requests.put(self.base_url + path, data=data, headers=self._with_headers(headers), timeout=5)
        return self.app.put(path, data=data, headers=headers, content_type='application/json')

    def _delete(self, path, headers=None):
        if self.integration:
            import requests
            return requests.delete(self.base_url + path, headers=self._with_headers(headers), timeout=5)
        return self.app.delete(path, headers=headers)

    def _json(self, response):
        """Parse JSON body for both requests and Flask test responses."""
        if self.integration:
            return response.json()
        return json.loads(response.data)

    def tearDown(self):
        """Clean DB session after each test."""
        with app.app_context():
            db.session.remove()

    def register_user(self, username="testuser", email="test@test.com", password="testpass123"):
        """Método auxiliar para registrar un usuario"""
        return self._post('/api/register',
                          data=json.dumps({
                              'username': username,
                              'email': email,
                              'password': password
                          }))

    def login_user(self, username="testuser", password="testpass123"):
        """Método auxiliar para hacer login"""
        return self._post('/api/login',
                          data=json.dumps({
                              'username': username,
                              'password': password
                          }))

    def get_auth_headers(self, token):
        """Método auxiliar para obtener headers de autenticación"""
        return {'Authorization': f'Bearer {token}'}

    # Tests de Autenticación
    def test_register_user_success(self):
        """Test: Registro exitoso de usuario"""
        response = self.register_user()
        self.assertEqual(response.status_code, 201)
        
        data = self._json(response)
        self.assertIn('User registered successfully', data['message'])
        self.assertEqual(data['user']['username'], 'testuser')

    def test_register_user_duplicate_username(self):
        """Test: Error al registrar usuario con nombre duplicado"""
        self.register_user()
        response = self.register_user()
        
        self.assertEqual(response.status_code, 409)
        data = self._json(response)
        self.assertIn('Username already exists', data['message'])

    def test_register_user_missing_fields(self):
        """Test: Error al registrar usuario sin campos requeridos"""
        response = self._post('/api/register', data=json.dumps({'username': 'test'}))
        
        self.assertEqual(response.status_code, 400)
        data = self._json(response)
        self.assertIn('required', data['message'])

    def test_login_success(self):
        """Test: Login exitoso"""
        self.register_user()
        response = self.login_user()
        
        self.assertEqual(response.status_code, 200)
        data = self._json(response)
        self.assertIn('token', data)
        self.assertIn('Login successful', data['message'])

    def test_login_invalid_credentials(self):
        """Test: Login con credenciales inválidas"""
        self.register_user()
        response = self.login_user(password="wrongpassword")
        
        self.assertEqual(response.status_code, 401)
        data = self._json(response)
        self.assertIn('Invalid credentials', data['message'])

    def test_login_missing_fields(self):
        """Test: Login sin campos requeridos"""
        response = self._post('/api/login',
                               data=json.dumps({'username': 'test'}))
        
        self.assertEqual(response.status_code, 400)

    # Tests de Tareas
    def test_create_task_success(self):
        """Test: Creación exitosa de tarea"""
        # Registrar y hacer login
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        # Crear tarea
        response = self._post('/api/tasks',
                              data=json.dumps({
                                  'title': 'Mi primera tarea',
                                  'description': 'Descripción de la tarea',
                                  'priority': 'high'
                              }),
                              headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 201)
        data = self._json(response)
        self.assertEqual(data['task']['title'], 'Mi primera tarea')
        self.assertEqual(data['task']['priority'], 'high')
        self.assertFalse(data['task']['completed'])

    def test_create_task_missing_title(self):
        """Test: Error al crear tarea sin título"""
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        response = self._post('/api/tasks',
                              data=json.dumps({'description': 'Sin título'}),
                              headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 400)
        data = self._json(response)
        self.assertIn('Title is required', data['message'])

    def test_create_task_without_auth(self):
        """Test: Error al crear tarea sin autenticación"""
        response = self._post('/api/tasks', data=json.dumps({'title': 'Tarea sin auth'}))
        
        self.assertEqual(response.status_code, 401)

    def test_get_tasks_success(self):
        """Test: Obtener tareas del usuario"""
        # Setup
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        # Crear algunas tareas
        self._post('/api/tasks',
                   data=json.dumps({'title': 'Tarea 1'}),
                   headers=self.get_auth_headers(token))
        
        self._post('/api/tasks',
                   data=json.dumps({'title': 'Tarea 2'}),
                   headers=self.get_auth_headers(token))
        
        # Obtener tareas
        response = self._get('/api/tasks', headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = self._json(response)
        # Two tasks are returned because only the ones created in this test exist
        self.assertEqual(len(data['tasks']), 2)

    def test_update_task_success(self):
        """Test: Actualización exitosa de tarea"""
        # Setup
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        # Crear tarea
        create_response = self._post('/api/tasks',
                                     data=json.dumps({'title': 'Tarea original'}),
                                     headers=self.get_auth_headers(token))
        
        task_id = self._json(create_response)['task']['id']
        
        # Actualizar tarea
        response = self._put(f'/api/tasks/{task_id}',
                             data=json.dumps({
                                 'title': 'Tarea actualizada',
                                 'completed': True
                             }),
                             headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = self._json(response)
        self.assertEqual(data['task']['title'], 'Tarea actualizada')
        self.assertTrue(data['task']['completed'])

    def test_update_nonexistent_task(self):
        """Test: Error al actualizar tarea inexistente"""
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        response = self._put('/api/tasks/999',
                             data=json.dumps({'title': 'No existe'}),
                             headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 404)

    def test_delete_task_success(self):
        """Test: Eliminación exitosa de tarea"""
        # Setup
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        # Crear tarea
        create_response = self._post('/api/tasks',
                                     data=json.dumps({'title': 'Tarea a eliminar'}),
                                     headers=self.get_auth_headers(token))
        
        task_id = self._json(create_response)['task']['id']
        
        # Eliminar tarea
        response = self._delete(f'/api/tasks/{task_id}', headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que fue eliminada
        get_response = self._get('/api/tasks', headers=self.get_auth_headers(token))
        data = self._json(get_response)
        # The list should be empty after deleting the only task created in this test
        self.assertEqual(len(data['tasks']), 0)

    def test_delete_nonexistent_task(self):
        """Test: Error al eliminar tarea inexistente"""
        self.register_user()
        login_response = self.login_user()
        token = self._json(login_response)['token']
        
        response = self._delete('/api/tasks/999', headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 404)

    def test_health_check(self):
        """Test: Endpoint de salud"""
        response = self._get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = self._json(response)
        self.assertEqual(data['status'], 'healthy')

    def test_task_isolation_between_users(self):
        """Test: Las tareas están aisladas entre usuarios"""
        # Registrar dos usuarios
        self.register_user("user1", "user1@test.com")
        self.register_user("user2", "user2@test.com")
        
        # Login de ambos usuarios
        token1 = self._json(self.login_user("user1"))['token']
        token2 = self._json(self.login_user("user2"))['token']
        
        # Usuario 1 crea una tarea
        self._post('/api/tasks',
                   data=json.dumps({'title': 'Tarea de user1'}),
                   headers=self.get_auth_headers(token1))
        
        # Usuario 2 obtiene sus tareas (debe estar vacío)
        response = self._get('/api/tasks', headers=self.get_auth_headers(token2))
        
        data = self._json(response)
        self.assertEqual(len(data['tasks']), 0)

if __name__ == '__main__':
    unittest.main()
