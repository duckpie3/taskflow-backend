# tests/test_app.py
import unittest
import json
import tempfile
import os
from app import app, db, User, Task

class TaskFlowTestCase(unittest.TestCase):
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
    def tearDown(self):
        """Limpieza después de cada prueba"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def register_user(self, username="testuser", email="test@test.com", password="testpass123"):
        """Método auxiliar para registrar un usuario"""
        return self.app.post('/api/register',
                           data=json.dumps({
                               'username': username,
                               'email': email,
                               'password': password
                           }),
                           content_type='application/json')

    def login_user(self, username="testuser", password="testpass123"):
        """Método auxiliar para hacer login"""
        return self.app.post('/api/login',
                           data=json.dumps({
                               'username': username,
                               'password': password
                           }),
                           content_type='application/json')

    def get_auth_headers(self, token):
        """Método auxiliar para obtener headers de autenticación"""
        return {'Authorization': f'Bearer {token}'}

    # Tests de Autenticación
    def test_register_user_success(self):
        """Test: Registro exitoso de usuario"""
        response = self.register_user()
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('User registered successfully', data['message'])
        self.assertEqual(data['user']['username'], 'testuser')

    def test_register_user_duplicate_username(self):
        """Test: Error al registrar usuario con nombre duplicado"""
        self.register_user()
        response = self.register_user()
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertIn('Username already exists', data['message'])

    def test_register_user_missing_fields(self):
        """Test: Error al registrar usuario sin campos requeridos"""
        response = self.app.post('/api/register',
                               data=json.dumps({'username': 'test'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('required', data['message'])

    def test_login_success(self):
        """Test: Login exitoso"""
        self.register_user()
        response = self.login_user()
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('Login successful', data['message'])

    def test_login_invalid_credentials(self):
        """Test: Login con credenciales inválidas"""
        self.register_user()
        response = self.login_user(password="wrongpassword")
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('Invalid credentials', data['message'])

    def test_login_missing_fields(self):
        """Test: Login sin campos requeridos"""
        response = self.app.post('/api/login',
                               data=json.dumps({'username': 'test'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)

    # Tests de Tareas
    def test_create_task_success(self):
        """Test: Creación exitosa de tarea"""
        # Registrar y hacer login
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        # Crear tarea
        response = self.app.post('/api/tasks',
                               data=json.dumps({
                                   'title': 'Mi primera tarea',
                                   'description': 'Descripción de la tarea',
                                   'priority': 'high'
                               }),
                               headers=self.get_auth_headers(token),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'Mi primera tarea')
        self.assertEqual(data['task']['priority'], 'high')
        self.assertFalse(data['task']['completed'])

    def test_create_task_missing_title(self):
        """Test: Error al crear tarea sin título"""
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        response = self.app.post('/api/tasks',
                               data=json.dumps({'description': 'Sin título'}),
                               headers=self.get_auth_headers(token),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Title is required', data['message'])

    def test_create_task_without_auth(self):
        """Test: Error al crear tarea sin autenticación"""
        response = self.app.post('/api/tasks',
                               data=json.dumps({'title': 'Tarea sin auth'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 401)

    def test_get_tasks_success(self):
        """Test: Obtener tareas del usuario"""
        # Setup
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        # Crear algunas tareas
        self.app.post('/api/tasks',
                     data=json.dumps({'title': 'Tarea 1'}),
                     headers=self.get_auth_headers(token),
                     content_type='application/json')
        
        self.app.post('/api/tasks',
                     data=json.dumps({'title': 'Tarea 2'}),
                     headers=self.get_auth_headers(token),
                     content_type='application/json')
        
        # Obtener tareas
        response = self.app.get('/api/tasks',
                              headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['tasks']), 2)

    def test_update_task_success(self):
        """Test: Actualización exitosa de tarea"""
        # Setup
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        # Crear tarea
        create_response = self.app.post('/api/tasks',
                                      data=json.dumps({'title': 'Tarea original'}),
                                      headers=self.get_auth_headers(token),
                                      content_type='application/json')
        
        task_id = json.loads(create_response.data)['task']['id']
        
        # Actualizar tarea
        response = self.app.put(f'/api/tasks/{task_id}',
                              data=json.dumps({
                                  'title': 'Tarea actualizada',
                                  'completed': True
                              }),
                              headers=self.get_auth_headers(token),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'Tarea actualizada')
        self.assertTrue(data['task']['completed'])

    def test_update_nonexistent_task(self):
        """Test: Error al actualizar tarea inexistente"""
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        response = self.app.put('/api/tasks/999',
                              data=json.dumps({'title': 'No existe'}),
                              headers=self.get_auth_headers(token),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 404)

    def test_delete_task_success(self):
        """Test: Eliminación exitosa de tarea"""
        # Setup
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        # Crear tarea
        create_response = self.app.post('/api/tasks',
                                      data=json.dumps({'title': 'Tarea a eliminar'}),
                                      headers=self.get_auth_headers(token),
                                      content_type='application/json')
        
        task_id = json.loads(create_response.data)['task']['id']
        
        # Eliminar tarea
        response = self.app.delete(f'/api/tasks/{task_id}',
                                 headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que fue eliminada
        get_response = self.app.get('/api/tasks',
                                  headers=self.get_auth_headers(token))
        data = json.loads(get_response.data)
        self.assertEqual(len(data['tasks']), 0)

    def test_delete_nonexistent_task(self):
        """Test: Error al eliminar tarea inexistente"""
        self.register_user()
        login_response = self.login_user()
        token = json.loads(login_response.data)['token']
        
        response = self.app.delete('/api/tasks/999',
                                 headers=self.get_auth_headers(token))
        
        self.assertEqual(response.status_code, 404)

    def test_health_check(self):
        """Test: Endpoint de salud"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_task_isolation_between_users(self):
        """Test: Las tareas están aisladas entre usuarios"""
        # Registrar dos usuarios
        self.register_user("user1", "user1@test.com")
        self.register_user("user2", "user2@test.com")
        
        # Login de ambos usuarios
        token1 = json.loads(self.login_user("user1"))['token']
        token2 = json.loads(self.login_user("user2"))['token']
        
        # Usuario 1 crea una tarea
        self.app.post('/api/tasks',
                     data=json.dumps({'title': 'Tarea de user1'}),
                     headers=self.get_auth_headers(token1),
                     content_type='application/json')
        
        # Usuario 2 obtiene sus tareas (debe estar vacío)
        response = self.app.get('/api/tasks',
                              headers=self.get_auth_headers(token2))
        
        data = json.loads(response.data)
        self.assertEqual(len(data['tasks']), 0)

if __name__ == '__main__':
    unittest.main()