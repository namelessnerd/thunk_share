
# thunk_share

## Overview

`thunk_share` is a Python-based project that includes functionality for interacting with AI models (e.g., `openai` and others) and managing client-specific operations. The project is structured to run within a Docker environment, utilizing the FastAPI framework for building APIs.

## Flow of the Application

1. Takes NCT_ID as input.
2. Uses the ClinicalTrials.gov API to fetch the trial description.
3. For the creatives service, retrieves configured services (simulating a service configuration tool such as Consul).
4. Invokes each configured AI by generating the appropriate prompt using the Prompt42 template.
5. Returns the generated creatives.

## Project Structure

```
├── aiml_api_root
│   ├── clients
│   ├── api_clients
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── .env
├── docker-compose.yml
├── README.md
└── .gitignore
```

### Key Directories:

- **`aiml_api_root/clients/`**: Contains client-side functionality, including API clients for external services.
- **`aiml_api_root/api_clients/dao`**: Data models and service integrations.
- **`requirements.txt`**: Lists the Python dependencies needed for the project.
- **`docker-compose.yml`**: Used for orchestrating Docker containers in the project.

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

- Docker
- Python 3.8 or higher
- `pip` (Python package manager)

### Steps

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd thunk_share
   ```

2. **Install Dependencies**:

   If you're running the project locally without Docker, you can install the Python dependencies using:

   ```bash
   pip install -r aiml_api_root/requirements.txt
   ```

3. **Set Up Environment Variables**:

   The `.env` file contains environment variables required for the project. Ensure that all necessary keys and values are provided in the `.env` file before running the project.

4. **Run the Application with Docker**:

   You can use Docker Compose to spin up the necessary containers:

   ```bash
   docker-compose up --build
   ```

5. **Access the API**:

   After starting the Docker container, the API will be available at:

   ```
   http://localhost:8000
   ```

## Additional Resources

There is a `sundries` folder that contains non-executable code, such as:
- **React front-end examples**: Demonstrates the UI component structure.
- **GraphQL and Graphene examples**: Shows how to interact with GraphQL APIs using Graphene in Python.
- **Screenshots and screen video grabs**: Visuals showcasing example workflows or application states.

## API Documentation

The API documentation can be accessed through the `/docs` endpoint when the server is running:

```
http://localhost:8000/docs
```

## License

This project is licensed under the MIT License.
