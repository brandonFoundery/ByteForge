# 🚀 FY.WB.Midway Upload Service

A comprehensive file upload service built with ASP.NET Core 8.0, designed to handle secure file uploads, storage, and management for the FY.WB.Midway Enterprise Logistics Platform.

## 📋 Features

### Core Upload Features
- **Single & Multiple File Upload** - Support for uploading individual files or batches
- **File Validation** - Comprehensive validation including size, type, and security checks
- **Flexible Storage** - Support for both local file storage and Azure Blob Storage
- **File Metadata** - Rich metadata support including categories, tags, and descriptions
- **Access Control** - Public/private file access with user-based permissions

### Security Features
- **File Type Validation** - MIME type detection and extension validation
- **Size Limits** - Configurable file size restrictions
- **Security Scanning** - Built-in checks for malicious file patterns
- **JWT Authentication** - Secure API access with JWT tokens
- **User Authorization** - Role-based access control

### Advanced Features
- **Image Processing** - Automatic image metadata extraction (dimensions, format)
- **File Expiration** - Automatic cleanup of expired files
- **Download Tracking** - Track file access and download counts
- **Search & Filtering** - Full-text search and category filtering
- **Statistics** - Comprehensive file usage statistics

## 🏗️ Architecture

### Service Structure
```
UploadService/
├── Controllers/          # API Controllers
├── Services/            # Business Logic Services
├── Models/              # Data Models
├── Data/                # Database Context
├── Configuration/       # Configuration Classes
└── Validators/          # Input Validation
```

### Key Components
- **UploadController** - Main API endpoints for file operations
- **FileUploadService** - Core business logic for file management
- **BlobStorageService** - Abstraction for storage operations (local/Azure)
- **FileValidationService** - File validation and security checks
- **UploadDbContext** - Entity Framework database context

## 🐳 Docker Setup

### Quick Start with Docker Compose

1. **Start the Upload Service**
   ```bash
   docker-compose -f docker-compose.upload.yml up --build
   ```

2. **Access the Service**
   - **Upload API**: http://localhost:5003
   - **Swagger Documentation**: http://localhost:5003
   - **MinIO Console** (if using): http://localhost:9001

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ASPNETCORE_ENVIRONMENT` | Environment (Development/Production) | Development |
| `ConnectionStrings__DefaultConnection` | Database connection string | SQL Server connection |
| `Upload__MaxFileSize` | Maximum file size in bytes | 104857600 (100MB) |
| `Upload__AllowedExtensions` | Comma-separated allowed extensions | pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,txt,csv |
| `Upload__UploadPath` | Local storage path | /app/uploads |
| `BlobStorage__ConnectionString` | Azure Blob Storage connection | Empty (uses local storage) |
| `BlobStorage__ContainerName` | Blob container name | uploads |
| `Authentication__JwtSecret` | JWT signing secret | development-secret-key-change-in-production |

## 📚 API Documentation

### Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Core Endpoints

#### Upload Single File
```http
POST /api/upload/single
Content-Type: multipart/form-data

Parameters:
- file: File to upload (required)
- category: File category (optional)
- description: File description (optional)
- tags: Comma-separated tags (optional)
- isPublic: Whether file is publicly accessible (optional, default: false)
- expiresAt: Expiration date (optional)
```

#### Upload Multiple Files
```http
POST /api/upload/multiple
Content-Type: multipart/form-data

Parameters:
- files: Multiple files to upload (required)
- category: File category (optional)
- isPublic: Whether files are publicly accessible (optional, default: false)
```

#### Get File Information
```http
GET /api/upload/{fileId}
```

#### Download File
```http
GET /api/upload/{fileId}/download
```

#### List Files
```http
GET /api/upload?skip=0&take=20&category=documents&search=invoice&myFiles=true
```

#### Update File Metadata
```http
PUT /api/upload/{fileId}
Content-Type: application/json

{
  "description": "Updated description",
  "tags": ["tag1", "tag2"],
  "category": "documents",
  "isPublic": true
}
```

#### Delete File
```http
DELETE /api/upload/{fileId}
```

#### Get Statistics
```http
GET /api/upload/statistics?myStats=true
```

#### Cleanup Expired Files (Admin Only)
```http
POST /api/upload/cleanup
```

### Response Examples

#### Successful Upload Response
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "originalFileName": "document.pdf",
  "storedFileName": "document_20231215_143022_a1b2c3d4.pdf",
  "fileExtension": ".pdf",
  "contentType": "application/pdf",
  "fileSizeBytes": 1048576,
  "fileHash": "d41d8cd98f00b204e9800998ecf8427e",
  "uploadedBy": "user123",
  "uploadedAt": "2023-12-15T14:30:22.123Z",
  "category": "documents",
  "description": "Important document",
  "tags": "[\"invoice\", \"2023\"]",
  "isPublic": false,
  "status": 0,
  "downloadCount": 0
}
```

#### File Statistics Response
```json
{
  "totalFiles": 150,
  "totalSizeBytes": 157286400,
  "totalDownloads": 1250,
  "filesByCategory": {
    "documents": 75,
    "images": 50,
    "reports": 25
  },
  "filesByExtension": {
    ".pdf": 60,
    ".jpg": 40,
    ".xlsx": 30,
    ".png": 20
  },
  "filesByStatus": {
    "0": 145,
    "1": 3,
    "2": 2
  }
}
```

## 🔧 Configuration

### Upload Settings
```json
{
  "Upload": {
    "MaxFileSize": 104857600,
    "AllowedExtensions": "pdf,doc,docx,xls,xlsx,jpg,jpeg,png,gif,txt,csv",
    "UploadPath": "/app/uploads",
    "EnableVirusScanning": false,
    "GenerateThumbnails": true,
    "ThumbnailSize": 200,
    "EnableCompression": false
  }
}
```

### Blob Storage Settings
```json
{
  "BlobStorage": {
    "ConnectionString": "DefaultEndpointsProtocol=https;AccountName=...",
    "ContainerName": "uploads",
    "UseAzureStorage": true,
    "EnableCdn": false,
    "CdnEndpoint": "",
    "AccessTier": "Hot"
  }
}
```

## 🔒 Security Considerations

### File Validation
- **Extension Checking** - Only allowed file extensions are accepted
- **MIME Type Detection** - Files are validated by content, not just extension
- **Size Limits** - Configurable maximum file sizes prevent abuse
- **Malicious Pattern Detection** - Scans for suspicious file patterns

### Access Control
- **User-based Permissions** - Users can only access their own files (unless public)
- **Admin Privileges** - Administrators can access all files and perform cleanup
- **JWT Authentication** - Secure token-based authentication
- **Public/Private Files** - Granular control over file visibility

### Storage Security
- **Unique File Names** - Prevents file name conflicts and guessing
- **Metadata Isolation** - File metadata stored separately from content
- **Soft Deletion** - Files are marked as deleted rather than immediately removed

## 🚀 Deployment

### Production Checklist
- [ ] Change JWT secret key
- [ ] Configure Azure Blob Storage (recommended for production)
- [ ] Set up proper database connection
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure file size limits appropriately
- [ ] Set up backup strategy for uploaded files

### Environment-Specific Settings

#### Development
```json
{
  "BlobStorage": {
    "UseAzureStorage": false
  },
  "Upload": {
    "MaxFileSize": 104857600
  }
}
```

#### Production
```json
{
  "BlobStorage": {
    "UseAzureStorage": true,
    "ConnectionString": "your-azure-connection-string",
    "EnableCdn": true,
    "CdnEndpoint": "https://your-cdn-endpoint.com"
  },
  "Upload": {
    "MaxFileSize": 524288000,
    "EnableVirusScanning": true
  }
}
```

## 🔍 Monitoring & Logging

### Health Checks
The service includes health checks for:
- Database connectivity
- Upload directory accessibility
- Azure Blob Storage (if configured)

Access health status at: `GET /health`

### Logging
Structured logging with Serilog:
- Console output for development
- File logging with rotation
- Configurable log levels
- Request/response logging

### Metrics
Track important metrics:
- Upload success/failure rates
- File storage usage
- Download patterns
- User activity

## 🛠️ Development

### Prerequisites
- .NET 8.0 SDK
- Docker Desktop
- SQL Server (or Docker container)

### Local Development Setup
1. **Clone the repository**
2. **Start dependencies**
   ```bash
   docker-compose up sqlserver redis
   ```
3. **Run the upload service**
   ```bash
   cd UploadService
   dotnet run
   ```

### Testing
```bash
# Run unit tests
dotnet test

# Test file upload
curl -X POST "http://localhost:5003/api/upload/single" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-file.pdf" \
  -F "category=test" \
  -F "description=Test upload"
```

## 📞 Support

For issues and questions:
1. Check the logs in `/app/logs/` or console output
2. Verify configuration settings
3. Test database and storage connectivity
4. Review the API documentation at `/swagger`

## 🔗 Integration

### Frontend Integration
The upload service is designed to integrate seamlessly with the FY.WB.Midway frontend:
- CORS configured for frontend domain
- RESTful API design
- Comprehensive error responses
- File metadata for UI display

### Backend Integration
- Shared database with main application
- JWT token compatibility
- Consistent logging and monitoring
- Event-driven architecture ready

## 📈 Performance

### Optimization Features
- Streaming file uploads for large files
- Efficient database queries with pagination
- Configurable file size limits
- CDN support for fast file delivery
- Connection pooling and async operations

### Scalability
- Stateless design for horizontal scaling
- External storage support (Azure Blob)
- Database optimization with indexes
- Configurable resource limits
