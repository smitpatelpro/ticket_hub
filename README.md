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

3. **Install Project Dependencies**

   Use UV to install the dependencies listed in the `uv.lock` file:

   ```bash
   uv sync
   ```

4. **Run the Project**

   After installing the dependencies, you can start the project:

   ```bash
   python manage.py runserver
   ```

### Additional Notes

- Ensure that you have the correct Python version set up in your environment.
- If you encounter any issues with missing dependencies, check the `uv.lock` file to ensure all packages are listed and correctly specified.

### Software Engineering Approach
Below principles are taken into account:
- [The Zen of Python](https://www.python.org/dev/peps/pep-0020/)
- [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [The Best Code is No Code At All](https://blog.codinghorror.com/the-best-code-is-no-code-at-all/)

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