# Lead Processing System

An ASP.NET Core 8 web application for automated lead processing using Elsa Workflows and Hangfire.

## Features

- **Automated Lead Scraping** - Scheduled jobs to collect leads from multiple sources
- **Workflow Processing** - Each lead goes through enrichment, vetting, scoring, and CRM integration
- **Background Jobs** - Reliable processing using Hangfire with retry policies
- **Web Dashboard** - Monitor leads and jobs through web interface
- **API Endpoints** - RESTful API for lead management
- **Azure Ready** - Configured for Azure App Service deployment

## Quick Start

### Option 1: Using Batch Scripts (Recommended)

1. **Start the application**
   ```cmd
   start-app.bat
   ```
   This will:
   - Kill any processes running on ports 7001, 5000, and 3000
   - Start the ASP.NET Core backend in a new terminal window
   - Start the Next.js frontend in another terminal window
   - Automatically install frontend dependencies

2. **Stop the application**
   ```cmd
   stop-app.bat
   ```

3. **Access the application**
   - **Dashboard**: `http://localhost:3000/dashboard` (Main UI with real-time updates)
   - **Backend API**: `https://localhost:7001/api/lead`
   - **Hangfire Dashboard**: `https://localhost:7001/hangfire`

### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LeadProcessing
   ```

2. **Install backend dependencies**
   ```bash
   dotnet restore
   ```

3. **Set up database**
   ```bash
   dotnet ef database update
   ```

4. **Start the backend**
   ```bash
   dotnet run
   ```

5. **Install frontend dependencies** (in a new terminal)
   ```bash
   cd FrontEnd
   npm install
   ```

6. **Start the frontend**
   ```bash
   npm run dev
   ```

7. **Access the application**
   - **Dashboard**: `http://localhost:3000/dashboard`
   - **Backend API**: `https://localhost:7001/api/lead`
   - **Hangfire Dashboard**: `https://localhost:7001/hangfire`

## Architecture

The system is built with:
- **ASP.NET Core 8** - Web framework
- **Entity Framework Core** - Data access
- **ASP.NET Core Identity** - Authentication
- **Elsa Workflows 3.4** - Workflow orchestration
- **Hangfire** - Background job processing
- **SQL Server** - Database storage

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed development guidance and architecture information.

## License

This project is licensed under the MIT License.