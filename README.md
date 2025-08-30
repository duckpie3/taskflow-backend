# TaskFlow API - Backend con Flask

## Descripción General

Este repositorio contiene el código fuente de la API REST para la aplicación TaskFlow. El backend está desarrollado en Python utilizando el microframework Flask y sigue una arquitectura limpia para proporcionar un servicio robusto, seguro y escalable para la gestión de tareas y usuarios.

El proyecto fue desarrollado aplicando las prácticas de la metodología de Programación Extrema (XP), con un fuerte énfasis en la calidad del código, las pruebas automatizadas y la integración continua.

---

## Tabla de Contenidos

1.  [Arquitectura y Pila Tecnológica](#arquitectura-y-pila-tecnológica)
2.  [Características del Servicio](#características-del-servicio)
3.  [Configuración del Entorno Local](#configuración-del-entorno-local)
4.  [Estructura del Proyecto](#estructura-del-proyecto)
5.  [Documentación de la API](#documentación-de-la-api)
6.  [Estrategia de Pruebas](#estrategia-de-pruebas)
7.  [Modelo de Datos y Base de Datos](#modelo-de-datos-y-base-de-datos)
8.  [Aplicación de la Metodología XP](#aplicación-de-la-metodología-xp)
9.  [Equipo de Desarrollo](#equipo-de-desarrollo)

---

## Arquitectura y Pila Tecnológica

El backend está diseñado como una API RESTful que se comunica a través de JSON, desacoplada de cualquier cliente frontend.

*   **Framework:** Flask 2.3.3
*   **ORM (Object-Relational Mapper):** Flask-SQLAlchemy 3.0.5
*   **Autenticación:** JSON Web Tokens (PyJWT 2.8.0)
*   **Base de Datos:** SQLite (para portabilidad y facilidad de desarrollo)
*   **Gestión de CORS:** Flask-CORS 4.0.0
*   **Servidor WSGI:** Werkzeug 2.3.7 (para desarrollo)
*   **Lenguaje:** Python 3.8+

---

## Características del Servicio

*   **Autenticación Basada en Tokens:** Sistema de registro y login seguro que genera tokens JWT con tiempo de expiración para proteger las rutas.
*   **CRUD Completo para Tareas:** Operaciones para crear, leer, actualizar y eliminar tareas, asociadas a un usuario específico.
*   **Aislamiento de Datos:** La lógica de negocio asegura que un usuario solo pueda acceder y manipular sus propias tareas.
*   **Validación de Entradas:** Verificación de los datos recibidos en las peticiones para asegurar la integridad de la información.
*   **Manejo de Errores Estructurado:** Respuestas de error claras y con los códigos de estado HTTP apropiados.
*   **Persistencia de Datos:** Uso de SQLite para el almacenamiento de la información de usuarios y tareas.

---

## Configuración del Entorno Local

Siga los siguientes pasos para ejecutar la API en un entorno de desarrollo.

### Prerrequisitos

*   Python 3.8 o superior
*   `pip` (gestor de paquetes de Python)
*   `venv` (módulo para entornos virtuales)

### Pasos de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/taskflow-backend.git
    cd taskflow-backend
    ```

2.  **Crear y activar un entorno virtual:**
    Se recomienda encarecidamente utilizar un entorno virtual para aislar las dependencias del proyecto.
    ```bash
    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    Este comando iniciará el servidor de desarrollo de Flask. La base de datos `taskflow.db` se creará automáticamente en la primera ejecución.
    ```bash
    python app.py
    ```

    La API estará disponible en `http://localhost:5000`.

---

## Estructura del Proyecto```
taskflow-backend/
├── app.py              # Lógica principal de la aplicación, rutas y modelos
├── requirements.txt    # Dependencias del proyecto
├── tests/              # Suite de pruebas unitarias y de integración
│   └── test_app.py
└── venv/               # Entorno virtual (ignorado por Git)
 ```

---

## Documentación de la API

La API expone los siguientes endpoints. Todas las rutas de tareas requieren un `Authorization: Bearer <token>` header.

### Autenticación

*   **`POST /api/register`**
    Registra un nuevo usuario.
    *   **Body:** `{ "username": "string", "email": "string", "password": "string" }`
    *   **Respuesta Exitosa (201):** `{ "message": "User registered successfully", "user": { ... } }`

*   **`POST /api/login`**
    Autentica a un usuario y devuelve un token JWT.
    *   **Body:** `{ "username": "string", "password": "string" }`
    *   **Respuesta Exitosa (200):** `{ "message": "Login successful", "token": "string", "user": { ... } }`

### Tareas

*   **`GET /api/tasks`**
    Obtiene la lista de todas las tareas del usuario autenticado.

*   **`POST /api/tasks`**
    Crea una nueva tarea.
    *   **Body:** `{ "title": "string", "description": "string", "priority": "low|medium|high" }`

*   **`PUT /api/tasks/<task_id>`**
    Actualiza una tarea existente.
    *   **Body:** `{ "title": "string", "description": "string", "completed": boolean, "priority": "string" }` (todos los campos son opcionales).

*   **`DELETE /api/tasks/<task_id>`**
    Elimina una tarea específica.

---

## Estrategia de Pruebas

Se ha implementado una suite de pruebas unitarias utilizando el módulo `unittest` de Python para garantizar la fiabilidad del código. Las pruebas cubren:

*   El flujo completo de autenticación (registro, login, casos de error).
*   El ciclo de vida de las tareas (CRUD).
*   Casos límite, como la solicitud de recursos inexistentes.
*   El correcto aislamiento de datos entre diferentes usuarios.

Para ejecutar las pruebas, utilice el siguiente comando desde la raíz del proyecto:

```bash
python -m unittest discover tests
```

---

## Modelo de Datos y Base de Datos

La persistencia se gestiona a través de una base de datos SQLite. Se definieron dos modelos principales utilizando SQLAlchemy:

*   **`User`**: Almacena el nombre de usuario, correo electrónico y el hash de la contraseña.
*   **`Task`**: Contiene los detalles de la tarea y una clave foránea (`user_id`) que establece una relación uno a muchos con el modelo `User`.

Esta estructura relacional es fundamental para garantizar que cada tarea esté siempre asociada a un único usuario.

---

## Aplicación de la Metodología XP

El desarrollo de esta API se adhirió a los principios de la Programación Extrema:

*   **Diseño Simple:** Se mantuvo una arquitectura directa y un código base limpio, evitando la complejidad innecesaria.
*   **Desarrollo Guiado por Pruebas (TDD):** Las funcionalidades se desarrollaron junto con sus pruebas correspondientes, asegurando que cada pieza de código sea verificable y robusta.
*   **Refactorización Continua:** El código fue revisado y mejorado constantemente para mantener su legibilidad y mantenibilidad.
*   **Integración Continua:** Se utilizó un sistema de Pull Requests y revisiones de código para integrar los cambios, y se configuró GitHub Actions para ejecutar la suite de pruebas automáticamente ante cada cambio, asegurando la estabilidad de la rama principal.

---

## Equipo de Desarrollo

*   José Antonio García Hernández
*   José David Aguilar Uribe
*   José Manuel Evangelista Tiburcio
---
