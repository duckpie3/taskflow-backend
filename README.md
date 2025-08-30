# TaskFlow API (Flask)

Backend en Flask para la gestión de usuarios y tareas con JWT. Incluye CRUD de tareas, autenticación y pruebas básicas.

---

## Pila Tecnológica

- Framework: Flask 2.3.3
- ORM: Flask-SQLAlchemy 3.0.5
- JWT: PyJWT 2.8.0
- CORS: Flask-CORS 4.0.0
- DB: SQLite (archivo `taskflow.db`)
- Python: 3.8+

---

## Puesta en Marcha

1) Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

2) Ejecutar la API
```bash
python app.py
```

- La API queda en `http://localhost:5000`.
- La BD `taskflow.db` se crea automáticamente al iniciar.
- En producción cambia `app.config['SECRET_KEY']` (ver `flask_backend.py`).

---

## Estructura del Proyecto

```
.
├── app.py               # Shim para importaciones de pruebas
├── flask_backend.py     # App Flask: modelos, rutas y lógica
├── backend_tests.py     # Pruebas con unittest
├── requirements.txt     # Dependencias
├── instance/            # Carpeta de instancia (si aplica)
└── venv/                # Entorno virtual (local)
```

---

## Endpoints Principales

- Autenticación:
  - `POST /api/register` — Crea usuario. Body: `{username, email, password}`
  - `POST /api/login` — Devuelve `{token, user}`

- Tareas (requiere header `Authorization: Bearer <token>`):
  - `GET /api/tasks` — Lista tareas del usuario
  - `POST /api/tasks` — Crea tarea. Body: `{title, description?, priority?}`
  - `PUT /api/tasks/<id>` — Actualiza. Body opcional: `{title, description, completed, priority}`
  - `DELETE /api/tasks/<id>` — Elimina tarea

- Salud:
  - `GET /api/health` — Estado del servicio

---

## Ejecutar Pruebas

```bash
python3 backend_tests.py
```

Nota: Hay un caso de prueba que usa `json.loads(self.login_user("user"))` en lugar de leer `response.data`. El patrón correcto es `json.loads(response.data)` como se utiliza en el resto del archivo.

---

## Notas Técnicas

- Inicialización BD: Se expone `create_tables()` (sin decorador `before_first_request` para compatibilidad con Flask 3). La creación también ocurre al iniciar la app (`if __name__ == '__main__'`).
- Seguridad: Cambia la clave `SECRET_KEY` en producción y usa una base de datos distinta a SQLite si se requiere concurrencia/escala.

---

## Autores

- José Antonio García Hernández
- José David Aguilar Uribe
- José Manuel Evangelista Tiburcio
