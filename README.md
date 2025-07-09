# FastAPI CRUD Project

This is a robust and scalable FastAPI project that demonstrates a complete CRUD (Create, Read, Update, Delete) application. It includes user authentication, database integration with SQLAlchemy, data validation with Pydantic, and a clean, modular project structure.

The entire development and production environment is containerized using Docker and Docker Compose for easy setup and consistent deployment.

## ✨ Features

- **Modern Tech Stack**: FastAPI, Pydantic, SQLAlchemy, and Docker.
- **Full CRUD Operations**: For Users, Products, and Orders.
- **Authentication**: JWT token-based authentication for securing endpoints.
- **Asynchronous Database Support**: Using `asyncio` and `asyncpg`.
- **Dependency Injection**: FastAPI's powerful dependency injection system is used throughout the app.
- **Clear Project Structure**: A modular design that separates concerns (API routes, business logic, data models).
- **Containerized**: Fully configured with Docker, Docker Compose, and a multi-stage `Dockerfile` for lean production images.
- **Live Reload & Debugging**: Pre-configured for a smooth development experience with hot-reloading and VS Code debugging.

---

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing.

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.
- [Visual Studio Code](https://code.visualstudio.com/) (Recommended) with the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) extensions.

### ⚙️ Installation & Running the App

The project is designed to be run entirely within Docker containers.

**1. Clone the Repository**

```bash
git clone <your-repository-url>
cd <repository-name>
2. Run for Development (with Hot-Reload)This is the standard way to run the application for development. It will start the FastAPI server, and any changes you make to the code will automatically trigger a server reload.docker-compose up --build
The API will be available at http://localhost:8000.3. Run for Debugging (with VS Code)This project is pre-configured for debugging with VS Code.Open the project folder in VS Code.Go to the Run and Debug panel (Ctrl+Shift+D).Select "Docker: Python - FastAPI" from the configuration dropdown.Press the F5 key or click the green play button.Docker Compose will start the containers, and the VS Code debugger will automatically attach to the application. You can now set breakpoints anywhere in your code!📚 API DocumentationOnce the application is running, you can access the interactive API documentation (powered by Swagger UI) at:http://localhost:8000/docsYou can also access the alternative ReDoc documentation at:http://localhost:8000/redoc🧪 Running TestsThe project includes a suite of tests using pytest. To run the tests, execute the following command in your terminal:docker-compose exec app pytest
This command runs the pytest command inside the running app service container.📂 Project StructureThe project follows a modular and scalable structure, separating different components of the application into logical directories..
├── app/
│   ├── core/                 # Core application logic (config, security, etc.)
│   │   ├── config.py         # Application configuration (from env vars).
│   │   ├── dependencies.py   # FastAPI dependency injection functions.
│   │   ├── logger.py         # Logging configuration.
│   │   └── security.py       # Authentication and password hashing logic.
│   │
│   ├── crud/                 # CRUD operations (database logic).
│   │   ├── orders.py         # Database functions for orders.
│   │   ├── product.py        # Database functions for products.
│   │   └── user.py           # Database functions for users.
│   │
│   ├── database/             # Database connection and session management.
│   │   └── db.py             # SQLAlchemy engine and session setup.
│   │
│   ├── models/               # SQLAlchemy ORM models (database table schemas).
│   │   ├── orders.py
│   │   ├── product.py
│   │   └── users.py
│   │
│   ├── routes/               # API endpoint definitions (the "controllers").
│   │   ├── orders.py
│   │   ├── product.py
│   │   └── user.py
│   │
│   ├── schemas/              # Pydantic models (data validation and serialization).
│   │   ├── errors.py         # Error response schemas.
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   │
│   ├── tests/                # Application tests.
│   │   ├── conftest.py       # Pytest fixtures and test setup.
│   │   ├── test_order.py
│   │   └── test_product.py
│   │
│   ├── utils/                # Utility functions.
│   │   └── file.py
│   │
│   └── main.py               # Main FastAPI application instance and entry point.
│
├── static/                   # Static files (e.g., images for products).
│
├── .vscode/
│   └── launch.json           # VS Code debugger configuration.
│
├── .gitignore                # Files and directories to be ignored by Git.
├── Dockerfile                # Instructions to build the production Docker image.
├── docker-compose.yml        # Docker Compose for development environment.
├── docker-compose.override.yml # Docker Compose for debug environment (used by VS Code).
├── pyproject.toml            # Project metadata and dependencies for Poetry.
├── poetry.lock               # Exact versions of dependencies.
└── README.md                 # This file.
