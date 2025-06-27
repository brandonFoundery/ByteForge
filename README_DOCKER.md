# 🐳 FY.WB.Midway Docker Setup Guide

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (usually included with Docker Desktop)
- **Git** for cloning the repository
- **Minimum 8GB RAM** and **20GB free disk space**

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Founder-yClients/FY.WB.Midway.git
cd FY.WB.Midway
```

### 2. Start All Services
```bash
# Build and start all containers
docker-compose up --build

# Or run in background (detached mode)
docker-compose up --build -d
```

### 3. Access the Application
- **Frontend**: http://localhost:4000
- **Backend API**: http://localhost:5002
- **Swagger Documentation**: http://localhost:8080
- **Database**: localhost:1433 (SQL Server)
- **Redis Cache**: localhost:6379

## 🔐 Default Login Credentials

### Admin Account
- **Email**: `admin@example.com`
- **Password**: `AdminPass123!`
- **Role**: System Administrator

### Tenant User Accounts
All tenant users have the password: `Test123!`

#### TechCorp Solutions
- **Email**: `alex.rodriguez@techcorp.com`
- **Company**: TechCorp Solutions

#### GlobalTrade Inc
- **Email**: `sarah.johnson@globaltrade.com`
- **Company**: GlobalTrade Inc

#### LogiFlow Systems
- **Email**: `mike.chen@logiflow.com`
- **Company**: LogiFlow Systems

## 📦 Container Architecture

### Services Overview
| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| Frontend | `fy-wb-midway-frontend` | 4000 | Next.js React Application |
| Backend | `fy-wb-midway-backend` | 5002 | ASP.NET Core Web API |
| Database | `fy-wb-midway-sqlserver` | 1433 | SQL Server 2022 |
| Cache | `fy-wb-midway-redis` | 6379 | Redis Cache |
| Swagger | `fy-wb-midway-swagger` | 8080 | API Documentation |
| Nginx | `fy-wb-midway-nginx` | 80 | Load Balancer/Proxy |

## 🛠️ Docker Commands

### Basic Operations
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ This will delete all data)
docker-compose down -v

# Rebuild containers
docker-compose up --build

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a
```

### Individual Service Management
```bash
# Start specific service
docker-compose up frontend
docker-compose up backend

# Restart specific service
docker-compose restart backend

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### Database Operations
```bash
# Connect to SQL Server container
docker exec -it fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!"

# Backup database
docker exec fy-wb-midway-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "StrongPassword123!" -Q "BACKUP DATABASE [FYWBMidway] TO DISK = '/var/opt/mssql/backup/FYWBMidway.bak'"

# View database logs
docker-compose logs sqlserver
```

### Debugging Commands
```bash
# Enter container shell
docker exec -it fy-wb-midway-backend bash
docker exec -it fy-wb-midway-frontend sh

# Check container health
docker inspect fy-wb-midway-backend | grep Health

# View container resource usage
docker stats

# Clean up unused containers/images
docker system prune
```

## 🔧 Configuration

### Environment Variables
The application uses the following key environment variables:

#### Backend (.env or docker-compose.yml)
```bash
ASPNETCORE_ENVIRONMENT=Development
ConnectionStrings__DefaultConnection=Server=sqlserver;Database=FYWBMidway;User Id=sa;Password=StrongPassword123!;TrustServerCertificate=True;
JWT_SECRET=development-secret-key-change-in-production
```

#### Frontend
```bash
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:5002
NEXT_PUBLIC_APP_NAME=FY.WB.Midway
```

### Custom Configuration
To override default settings, create a `.env` file in the root directory:

```bash
# .env file example
POSTGRES_PASSWORD=your_custom_password
JWT_SECRET=your_jwt_secret_key
NEXT_PUBLIC_API_URL=http://your-backend-url:5002
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :4000
netstat -ano | findstr :5002

# Kill process using the port (Windows)
taskkill /PID <PID> /F

# Change ports in docker-compose.yml if needed
```

#### 2. Database Connection Issues
```bash
# Check if SQL Server container is running
docker ps | grep sqlserver

# Check SQL Server logs
docker-compose logs sqlserver

# Restart database container
docker-compose restart sqlserver
```

#### 3. Frontend Can't Connect to Backend
```bash
# Check backend health
curl http://localhost:5002/health

# Check backend logs
docker-compose logs backend

# Verify CORS settings in backend configuration
```

#### 4. Container Build Failures
```bash
# Clean Docker cache
docker builder prune

# Remove all containers and rebuild
docker-compose down
docker-compose up --build --force-recreate
```

### Health Checks
```bash
# Check all container health status
docker-compose ps

# Test API endpoints
curl http://localhost:5002/api/health
curl http://localhost:5002/api/Auth/login -X POST -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"AdminPass123!"}'
```

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose logs

# Specific service with timestamps
docker-compose logs -t backend

# Follow logs in real-time
docker-compose logs -f --tail=100 backend

# Save logs to file
docker-compose logs backend > backend.log
```

### Performance Monitoring
```bash
# Container resource usage
docker stats

# Detailed container info
docker inspect fy-wb-midway-backend
```

## 🔄 Development Workflow

### Making Changes

#### Backend Changes
```bash
# Rebuild only backend
docker-compose up --build backend

# Or restart after code changes
docker-compose restart backend
```

#### Frontend Changes
```bash
# Rebuild only frontend
docker-compose up --build frontend

# For development with hot reload, run locally:
cd FrontEnd
npm install
npm run dev
```

### Database Migrations
```bash
# The application automatically handles database creation and seeding
# To reset database completely:
docker-compose down -v
docker-compose up --build
```

## 🚀 Production Deployment

### Production Build
```bash
# Build for production
docker-compose -f docker-compose.prod.yml up --build -d
```

### Security Considerations
- Change default passwords
- Use environment variables for secrets
- Enable HTTPS
- Configure proper CORS settings
- Set up proper logging and monitoring

## 📞 Support

If you encounter issues:

1. **Check the logs** using the commands above
2. **Verify all containers are running** with `docker ps`
3. **Test API connectivity** with curl commands
4. **Check the troubleshooting section** for common solutions
5. **Review the main README.md** for additional information

## 🔗 Related Documentation

- [Main README](README.md) - Project overview and features
- [Frontend README](FrontEnd/README.md) - Frontend-specific documentation
- [Startup Issues Guide](README_STARTUP_ISSUES.md) - Common startup problems and solutions
