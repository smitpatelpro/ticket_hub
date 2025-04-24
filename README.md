# TicketHub Project

## Setup and Installation

This guide will help you set up and install the project dependencies using UV.

### Prerequisites

- Python 3.12 or higher
- UV (Python-based package manager)

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd tickethub-project
   ```

2. **Install UV**

   If you haven't installed UV yet, you can do so via pip:

   ```bash
   pip install uv
   ```
   alternatively you can follow steps here: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

3. **Install Project Dependencies**

   Use UV to install the dependencies listed in the `uv.lock` file:

   ```bash
   uv sync
   ```
   This will create a new virtual environment (typically `.venv` directory), make sure that you activate it before running project

4. **Prepare .env file from .env.example file**

   Copy `.env.example` file and create `.env` file and update secrets

5. **migrate DB**

   After installing the dependencies, you can start the project:

   ```bash
   python manage.py migrate
   ```

6. **Collect static files**

   After installing the dependencies, you can start the project:

   ```bash
   python manage.py collectstatic
   ```

7. **Create super user for admin access**

   After installing the dependencies, you can start the project:

   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Project**

   After installing the dependencies, you can start the project:

   ```bash
   python manage.py runserver
   ```

9. **Run the Test Cases**

   After installing the dependencies, you can start the tests:

   ```bash
   python manage.py tests
   ```

### Additional Notes

- Ensure that you have the correct Python version set up in your environment.
- If you encounter any issues with missing dependencies, check the `uv.lock` file to ensure all packages are listed and correctly specified.
- SQLite DB and Inmemory Channel Layers are used for fast development. for production environment, we can easily switch to Sophisticated solutions like PostgreSQL and Redis and these secrets will be added into `.env` file
- Silk profiler is used to measure API DB calls and relative response time
- Web Socket based Django channels is implemented for realtime updates

### Django Admin
[http://localhost:8000/admin](http://localhost:8000/admin)

### Swagger UI
Run server and check below path
[http://localhost:8000/swagger/](http://localhost:8000/swagger/)

### Redoc UI
Run server and check below path
[http://localhost:8000/redoc/](http://localhost:8000/redoc/)

### Postman Collection
Postman collection is added at project root

### API Performance Profiling GUI using Silk
[http://localhost:8000/silk/](http://localhost:8000/silk/)

### Software Engineering Approach
Below principles are taken into account:
- [The Zen of Python](https://www.python.org/dev/peps/pep-0020/)
- [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [The Best Code is No Code At All](https://blog.codinghorror.com/the-best-code-is-no-code-at-all/)
- [Keep it simple, stupid!](https://en.wikipedia.org/wiki/KISS_principle)

### Error Response Structure
NOTE: This is default DRF response structure
Most of the places, DRF and Django defaults are preferred unless a change is required
 - Principle: Do not over-engineer unless its required.
   - The Zen of Python, DRY and The Best Code is No Code At All

The API will return errors in the following structure:
```{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is expired"
        }
    ]
}
```

## Architecture Overview
### Key Architecture Decisions
- UUID is used as primary key for all models
- Priority was to have minimal changes in built in Django features as per requirements to avoid unnecessary clutter and over-engineering
- Some effort is done to Avoid N+1 Query problem in APIs and Serializers
- 

### ***Realtime updates***
The TicketHub project leverages Django Channels to handle WebSocket connections, allowing for real-time features within the application. Below is an overview of the architecture:

1. **Django Application**: 
   - The core of the application, managing HTTP requests and responses, user authentication, and REST API endpoints using Django REST Framework.

2. **Django Channels**:
   - Adds support for handling WebSocket connections. Channels layers enable asynchronous communication, allowing the server to push updates to clients in real-time.

3. **WebSocket Consumer**:
   - Custom consumers are implemented to handle WebSocket connections. They define the actions to be taken when messages are received, sent, or connections are closed.

4. **Channel Layers**:
   - In-memory channel layers are configured for message passing between the consumer and other parts of the application. This can be replaced with a more robust solution like Redis for production.

5. **Asynchronous Task Handling**:
   - Tasks and events are processed asynchronously, enabling efficient handling of concurrent connections without blocking the main application thread.

6. **Frontend Client**:
   - The client establishes a WebSocket connection to receive real-time updates from the server. This could be a single-page application (SPA) using frameworks like React or Vue.js.

### Sequence of Events

1. **Client Connection**:
   - A client initiates a WebSocket connection to the server. The server authenticates the client using Django's authentication mechanisms.

2. **Message Handling**:
   - The WebSocket consumer manages incoming messages, processes them, and communicates with other parts of the Django application as needed.

3. **Real-Time Updates**:
   - The server sends updates to connected clients through the WebSocket, ensuring they receive data in real-time without needing to refresh the page.

4. **Disconnection**:
   - When a client disconnects, the WebSocket consumer handles the event, performing any necessary cleanup.

This architecture enables TicketHub to provide a responsive and interactive user experience, leveraging the power of Django Channels for real-time communication.

### API Structure

The TicketHub API is designed to provide a comprehensive and efficient interface for interacting with the TicketHub platform. Below is an overview of the API structure:

1. **Authentication**:
   - The API uses JWT (JSON Web Tokens) for authenticating requests. Clients must obtain a token by providing valid credentials and include it in the Authorization header of each request.

2. **Endpoints**:
   - **User Management**: Endpoints for user registration, login, profile management, and password reset.
   - **Projects**: Manage projects, including creating, updating, listing, and deleting projects.
   - **Tasks**: Endpoints to create, update, list, and delete tasks associated with projects.
   - **Comments**: Allows users to add, update, and delete comments on tasks.

3. **Versioning**:
   - The API supports versioning to ensure backward compatibility. The current version is specified in the URL (e.g., `/api/v1/...`).

4. **Error Handling**:
   - Errors are returned in a consistent structure with a `detail` key providing a human-readable error message and a `code` key for programmatic handling.

5. **Pagination**:
   - List endpoints support pagination to handle large sets of data efficiently. The default pagination strategy is limit-offset.

6. **Filtering**:
   - Endpoints provide filtering options, allowing clients to tailor responses according to specific criteria.

7. **Documentation**:
   - The API is documented using OpenAPI, providing a comprehensive guide to available endpoints, request/response formats, and authentication requirements.

This structure ensures that the TicketHub API is robust, flexible, and easy to use, providing a solid foundation for building applications that interact with the TicketHub platform.

<!-- ### User Invite Mechanism -->


### Scope of Improvement
- Test cases can be more comprehensive
- Moving logic from view to serializers/model can prove beneficial
- Scope of improvement in websocket handlers
- APIs are some what optimized for performance, but can be improved further
