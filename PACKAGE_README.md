# 📦 FY.WB.Midway Container Package

## 🎯 Package Contents

This package contains everything needed to run the FY.WB.Midway application using Docker containers.

### 📁 Included Files & Folders

#### **Core Application Code**
- `FrontEnd/` - Complete Next.js React frontend application
- `BackEnd/` - Complete ASP.NET Core Web API backend application

#### **Infrastructure & Configuration**
- `Infrastructure/` - Database initialization scripts, Nginx configuration, environment settings
  - `Infrastructure/database/init/` - SQL Server database setup scripts
  - `Infrastructure/nginx/` - Reverse proxy configuration
  - `Infrastructure/environments/` - Environment-specific configurations

#### **Docker Configuration**
- `docker-compose.yml` - Main Docker orchestration file
- `docker-compose.override.yml` - Development environment overrides
- `Dockerfile.backend` - Backend container build instructions
- `Dockerfile.frontend` - Frontend container build instructions

#### **Documentation**
- `README_DOCKER.md` - Complete Docker setup guide with troubleshooting
- `README_STARTUP_ISSUES.md` - Common startup problems and solutions

## 🚀 Quick Start Instructions

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose (included with Docker Desktop)
- Minimum 8GB RAM and 20GB free disk space

### Installation Steps

1. **Extract the package** to your desired location
2. **Open terminal/command prompt** in the extracted folder
3. **Run the application**:
   ```bash
   docker-compose up --build
   ```

### Access Points
Once running, access the application at:
- **Frontend**: http://localhost:4000
- **Backend API**: http://localhost:5002
- **API Documentation**: http://localhost:8080
- **Database**: localhost:1433 (SQL Server)

### Default Login Credentials
- **Admin Email**: `admin@example.com`
- **Admin Password**: `AdminPass123!`

## 🔧 Container Architecture

The application runs 6 containers:
1. **Frontend** (Next.js) - Port 4000
2. **Backend** (ASP.NET Core) - Port 5002
3. **Database** (SQL Server 2022) - Port 1433
4. **Cache** (Redis) - Port 6379
5. **API Docs** (Swagger UI) - Port 8080
6. **Load Balancer** (Nginx) - Port 80

## 📞 Support

For detailed setup instructions, troubleshooting, and advanced configuration, see:
- `README_DOCKER.md` - Complete Docker guide
- `README_STARTUP_ISSUES.md` - Common problems and solutions

## 🔄 Development Workflow

### Making Changes
- Backend changes: `docker-compose up --build backend`
- Frontend changes: `docker-compose up --build frontend`
- View logs: `docker-compose logs [service-name]`

### Stopping the Application
```bash
# Stop all services
docker-compose down

# Stop and remove all data (⚠️ This deletes the database)
docker-compose down -v
```

## 📋 Package Information

- **Package Size**: ~400MB compressed
- **Total Services**: 6 Docker containers
- **Database**: SQL Server 2022 with automatic initialization
- **Frontend**: Next.js with Tailwind CSS
- **Backend**: ASP.NET Core with Entity Framework
- **Architecture**: Multi-tenant SAAS application

---

**Created**: June 17, 2025  
**Version**: Container Package v1.0  
**Repository**: https://github.com/Founder-yClients/FY.WB.Midway