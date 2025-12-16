# Library Management System 📚

A RESTful API built with Flask for managing library operations including users, books, loans, and audit logging.

## ✨ Features

- **User Management**: Create and manage library patrons and librarians
- **Book Catalog**: Add and update books with inventory tracking
- **Loan System**: Borrow and return books with automatic due date calculation (14-day loan period)
- **Fine Calculation**: Automatic fine calculation for overdue books ($0.50/day, max $25.00)
- **Audit Logging**: Complete audit trail for all system operations
- **Health Monitoring**: Built-in health check endpoint

## 🛠️ Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

---

## 🚀 Quick Start Guide

### Prerequisites

**Windows Users:**
- Docker Desktop for Windows ([Download here](https://www.docker.com/products/docker-desktop))

**Mac Users:**
- Docker Desktop for Mac ([Download here](https://www.docker.com/products/docker-desktop))

**Linux Users:**
- Docker and Docker Compose
  ```bash
  sudo apt-get update
  sudo apt-get install docker.io docker-compose
  ```

### Installation & Setup

#### 1️⃣ Organize Your Files

Place all project files in one directory:

```
library-management-system/
├── app.py
├── database.py
├── audit.py
├── conftest.py
├── test_app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

#### 2️⃣ Start the Application

**On Windows (Command Prompt):**
```cmd
cd C:\Users\YourName\library-management-system
docker-compose up --build
```

**On Windows (PowerShell):**
```powershell
cd C:\Users\YourName\library-management-system
docker-compose up --build
```

**On Mac/Linux (Terminal):**
```bash
cd ~/library-management-system
docker-compose up --build
```

#### 3️⃣ Verify It's Running

**Option 1 - Browser:**
- Open: http://localhost:5000/health

**Option 2 - Command Line:**

Windows (PowerShell):
```powershell
Invoke-WebRequest -Uri http://localhost:5000/health | Select-Object -Expand Content
```

Mac/Linux:
```bash
curl http://localhost:5000/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "statistics": {
    "total_users": 0,
    "total_books": 0,
    "total_loans": 0,
    "active_loans": 0
  },
  "timestamp": "2024-12-16T10:30:00.123456"
}
```

---

## 📖 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints Overview

#### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | System health check with statistics |

#### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user |
| GET | `/users` | List all users |
| GET | `/users/<id>` | Get user details with active loans |

#### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/books` | Create a new book |
| GET | `/books` | List all books |
| GET | `/books/<id>` | Get book details |
| PATCH | `/books/<id>` | Update book (e.g., add more copies) |

#### Loans
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/loans` | Create a new loan (borrow a book) |
| GET | `/loans` | List all loans |
| GET | `/loans/<id>` | Get loan details |
| PATCH | `/loans/<id>/return` | Return a book |
| GET | `/loans/overdue` | List all overdue loans |

#### Audit Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit-logs` | List audit logs (with optional filters) |
| GET | `/audit-logs/<id>` | Get specific audit log entry |

---

## 💻 Example API Usage

### Using Python (Recommended)

Create a file `test_api.py`:

```python
import requests

BASE_URL = 'http://localhost:5000'

# 1. Create a user
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "role": "patron"
}
response = requests.post(f'{BASE_URL}/users', json=user_data)
print("User created:", response.json())
user_id = response.json()['id']

# 2. Create a book
book_data = {
    "title": "1984",
    "author": "George Orwell",
    "isbn": "9780451524935"
}
response = requests.post(f'{BASE_URL}/books', json=book_data)
print("Book created:", response.json())
book_id = response.json()['id']

# 3. Create a loan
loan_data = {
    "user_id": user_id,
    "book_id": book_id
}
response = requests.post(f'{BASE_URL}/loans', json=loan_data)
print("Loan created:", response.json())
loan_id = response.json()['loan']['id']

# 4. List all books
response = requests.get(f'{BASE_URL}/books')
print("All books:", response.json())

# 5. Return the book
response = requests.patch(f'{BASE_URL}/loans/{loan_id}/return')
print("Book returned:", response.json())
```

Run it:
```bash
python test_api.py
```

### Using curl (Mac/Linux)

**Create a User:**
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "role": "patron"
  }'
```

**Create a Book:**
```bash
curl -X POST http://localhost:5000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "9780743273565"
  }'
```

**List All Books:**
```bash
curl http://localhost:5000/books
```

**Create a Loan:**
```bash
curl -X POST http://localhost:5000/loans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "book_id": 1
  }'
```

**Return a Book:**
```bash
curl -X PATCH http://localhost:5000/loans/1/return
```

**Get Overdue Loans:**
```bash
curl http://localhost:5000/loans/overdue
```

### Using PowerShell (Windows)

**Create a User:**
```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    username = "john_doe"
    email = "john@example.com"
    phone = "555-1234"
    role = "patron"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/users -Method Post -Headers $headers -Body $body
```

**List All Users:**
```powershell
Invoke-RestMethod -Uri http://localhost:5000/users
```

---

## 🎮 Docker Commands Reference

### Starting the Application

```bash
# Start in foreground (see logs in real-time)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Rebuild and start (after code changes)
docker-compose up --build
```

### Stopping the Application

```bash
# Stop containers (keeps database)
docker-compose down

# Stop and remove database
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Running Tests

```bash
# Run all tests
docker-compose exec library-api pytest -v

# Run specific test file
docker-compose exec library-api pytest test_app.py -v

# Run with coverage
docker-compose exec library-api pytest --cov=. --cov-report=html
```

### Other Useful Commands

```bash
# Restart services
docker-compose restart

# Access container shell
docker-compose exec library-api /bin/bash

# View running containers
docker-compose ps

# Remove all containers and volumes
docker-compose down -v
```

---

## 📊 Business Rules

- **Loan Period**: 14 days from loan date
- **Fine Rate**: $0.50 per day overdue
- **Maximum Fine**: $25.00
- **Book Availability**: Automatically tracked when books are loaned/returned
- **User Roles**: `patron` (default) or `librarian`

---

## 🗄️ Database Schema

### Users Table
```
- id (Primary Key)
- username (Unique)
- email (Unique)
- phone (Unique)
- role (patron/librarian)
- created_at (Timestamp)
```

### Books Table
```
- id (Primary Key)
- title
- author
- isbn (Unique)
- total_copies
- available_copies
```

### Loans Table
```
- id (Primary Key)
- user_id (Foreign Key → Users)
- book_id (Foreign Key → Books)
- loan_date (Timestamp)
- due_date (Timestamp)
- return_date (Nullable)
- fine (Default: 0.0)
```

### AuditLog Table
```
- id (Primary Key)
- action
- entity_type
- entity_id
- user_id (Nullable)
- timestamp
- details (JSON)
- ip_address
```

---

## 🧪 Testing

### Run All Tests
```bash
docker-compose exec library-api pytest -v
```

### Run Specific Test File
```bash
docker-compose exec library-api pytest test_app.py -v
```

### Run Tests with Coverage
```bash
docker-compose exec library-api pytest --cov=. --cov-report=html
```

### Test Coverage Includes:
- ✅ User creation and retrieval
- ✅ Book management
- ✅ Loan creation and validation
- ✅ Book return with fine calculation
- ✅ Overdue loan tracking
- ✅ Audit log generation
- ✅ Health check endpoints

---

## 🔧 Local Development (Without Docker)

If you prefer to run without Docker:

### 1. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

### 4. Run Tests
```bash
pytest -v
```

The application will be available at http://localhost:5000

---

## 🚨 Troubleshooting

### Port 5000 Already in Use

**Solution:** Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8000:5000"  # Change 8000 to any available port
```

Then access the API at http://localhost:8000

### Docker Desktop Not Starting (Windows)

**Solution:**
1. Enable Hyper-V and WSL 2
2. Open PowerShell as Administrator:
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```
3. Restart your computer

### Changes to Code Don't Appear

**Solution:** Rebuild the container:
```bash
docker-compose down
docker-compose up --build
```

### Database Has Old/Incorrect Data

**Solution:** Reset the database:
```bash
docker-compose down -v
docker-compose up --build
```

### Cannot Connect to Docker Daemon

**Solution:**
- **Windows/Mac**: Make sure Docker Desktop is running
- **Linux**: Start Docker service
  ```bash
  sudo systemctl start docker
  ```

### Permission Errors (Linux)

**Solution:** Add your user to the docker group:
```bash
sudo usermod -aG docker $USER
```
Log out and log back in for changes to take effect.

---

## 📁 Project Structure

```
library-management-system/
├── app.py                 # Main Flask application
├── database.py            # Database models and initialization
├── audit.py               # Audit logging functionality
├── conftest.py            # Pytest configuration and fixtures
├── test_app.py            # Integration tests
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose orchestration
├── .dockerignore          # Files to exclude from Docker build
├── README.md              # This file
└── library.db             # SQLite database (auto-created)
```

---

## 🎯 Common Use Cases

### Scenario 1: Student Borrows a Book

```python
import requests

# 1. Create student
student = requests.post('http://localhost:5000/users', json={
    "username": "alice_student",
    "email": "alice@university.edu",
    "phone": "555-0001",
    "role": "patron"
}).json()

# 2. Student borrows a book
loan = requests.post('http://localhost:5000/loans', json={
    "user_id": student['id'],
    "book_id": 1
}).json()

print(f"Due date: {loan['loan']['due_date']}")
```

### Scenario 2: Check Overdue Books

```python
import requests

overdue = requests.get('http://localhost:5000/loans/overdue').json()
print(f"Number of overdue loans: {overdue['count']}")

for loan in overdue['overdue_loans']:
    print(f"{loan['username']} has {loan['book_title']} overdue by {loan['days_overdue']} days")
    print(f"Fine: ${loan['potential_fine']}")
```

### Scenario 3: Return a Book Late

```python
import requests

# Return book (will calculate fine if late)
result = requests.patch('http://localhost:5000/loans/1/return').json()

if result['is_overdue']:
    print(f"Fine applied: ${result['fine']}")
    print(f"Days overdue: {result['days_overdue']}")
```

### Scenario 4: Track User Activity

```python
import requests

# Get user with their loans
user = requests.get('http://localhost:5000/users/1').json()

print(f"Active loans: {user['active_loans_count']}")
print(f"Total potential fines: ${user['total_potential_fines']}")

for loan in user['active_loans']:
    print(f"Book: {loan['book_title']}")
    print(f"Due: {loan['due_date']}")
    if loan['is_overdue']:
        print(f"OVERDUE by {loan['days_overdue']} days!")
```

---

## 🔐 Security Notes

**For Production Deployment:**

1. **Change Flask Secret Key**
2. **Use Production Database** (PostgreSQL, MySQL)
3. **Add Authentication & Authorization**
4. **Enable HTTPS**
5. **Set up Environment Variables** for sensitive data
6. **Implement Rate Limiting**
7. **Add Input Validation & Sanitization**

This is a development/educational project and should not be deployed to production without proper security measures.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 📞 Support

Having issues? Check the troubleshooting section above or:

1. Review the logs: `docker-compose logs -f`
2. Check Docker Desktop is running
3. Verify port 5000 is available
4. Ensure all files are in the same directory

---

## 🎓 Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Docker Documentation**: https://docs.docker.com/
- **pytest Documentation**: https://docs.pytest.org/

---

**Ready to get started? Just run:**

```bash
docker-compose up --build
```

**Then visit:** http://localhost:5000/health

Happy coding! 🎉