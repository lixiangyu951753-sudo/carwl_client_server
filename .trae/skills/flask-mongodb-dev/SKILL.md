---
name: "flask-mongodb-dev"
description: "Assists with Flask + MongoDB project development, including API creation, database integration, Docker deployment, and troubleshooting. Invoke when working on Flask MongoDB projects or needing deployment guidance."
---

# Flask + MongoDB Development Assistant

This skill helps developers work with Flask applications integrated with MongoDB, including:

## Key Features

### 1. Project Setup
- Creating Flask applications with MongoDB integration
- Setting up proper directory structure
- Configuring MongoDB connections
- Managing environment variables

### 2. API Development
- Creating RESTful APIs with Flask Blueprints
- Implementing CRUD operations with MongoDB
- Handling request validation and error responses
- Best practices for API design

### 3. Database Operations
- MongoDB collection design and indexing
- Query optimization
- Data modeling best practices
- Connection management

### 4. Docker Deployment
- Creating Dockerfiles for Flask applications
- Docker Compose configuration
- Environment variable management in containers
- Networking and service discovery

### 5. Troubleshooting
- Common MongoDB connection issues
- Flask application errors
- Docker container problems
- Performance optimization

### 6. Security Best Practices
- Input validation
- Authentication and authorization
- Environment variable security
- Database access control

## Usage Examples

**Example 1: Setting up MongoDB connection**
```python
from pymongo import MongoClient
import os

# Use environment variables for connection string
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
mongo_client = MongoClient(mongo_uri)
db = mongo_client['your_database']
```

**Example 2: Dockerfile for Flask app**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "run.py"]
```

**Example 3: Docker Compose configuration**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MONGO_URI=mongodb://mongo:27017/
      - MONGO_DB=your_database
    depends_on:
      - mongo
  
  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

## Common Issues and Solutions

### MongoDB Connection Issues
- **Problem**: Connection refused
- **Solution**: Check MongoDB service status, verify connection string, ensure network access

### Docker Deployment Issues
- **Problem**: Container can't connect to MongoDB
- **Solution**: Use proper network configuration, check environment variables

### Performance Issues
- **Problem**: Slow queries
- **Solution**: Add indexes, optimize query patterns, use projection

This skill provides comprehensive guidance for developing and deploying Flask + MongoDB applications, with a focus on best practices and troubleshooting common issues.