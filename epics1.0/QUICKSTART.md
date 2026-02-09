# Quick Start Guide - Healthcare Management System

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
pip install fastapi uvicorn sqlalchemy pymysql mysql-connector-python python-multipart bcrypt python-jose pydantic cryptography
```

### Step 2: Setup MySQL Database (2 minutes)

```bash
# Start MySQL
sudo systemctl start mysql  # Linux
# or start from XAMPP/WAMP control panel on Windows

# Create database and import schema
mysql -u root -p
```

```sql
CREATE DATABASE healthcare_db;
EXIT;
```

```bash
mysql -u root -p healthcare_db < database_schema.sql
```

### Step 3: Configure Database Connection (30 seconds)

Edit `config.py` and update these lines:

```python
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_mysql_password'  # Change this!
```

### Step 4: Start the Server (30 seconds)

```bash
python main.py
```

### Step 5: Access the Application (30 seconds)

Open your browser:
- **Frontend**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs

## 🎉 You're Done!

### Test the System

1. Go to the **Register** tab
2. Fill in patient registration form
3. Click "Register as Patient"
4. Go to **Login** tab and login
5. Check the **Doctors** tab to see available doctors

## 📋 Default Test Data

After running `database_schema.sql`, you get:
- **Admin Account**: admin@healthcare.com / password123 (default bcrypt hash)

## 🔧 Common Issues

**Can't connect to MySQL?**
```bash
# Check MySQL is running
sudo systemctl status mysql
```

**Port 8000 already in use?**
```bash
# Change port in main.py last line:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use 8001
```

**Import errors?**
```bash
pip install -r requirements.txt
```

## 🚀 Next Steps

1. **Explore the API**: http://localhost:8000/docs
2. **Create a doctor account** (use API or SQL)
3. **Book an appointment**
4. **Read full documentation**: README.md

## 💡 Quick API Test

```bash
# Test health endpoint
curl http://localhost:8000/health

# Register a patient (replace with your data)
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "email": "test@example.com",
      "password": "test12345",
      "user_type": "patient",
      "first_name": "Test",
      "last_name": "User",
      "country": "India"
    }
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test12345"}'
```

## 📚 Learn More

- Full API documentation: `/docs` endpoint
- Database schema: `database_schema.sql`
- Complete guide: `README.md`

Happy coding! 🏥
