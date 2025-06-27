# API Common Patterns and Shared Components

This document defines common patterns, shared parameters, headers, and response structures used across all API endpoints.

## Common Parameters

### Pagination Parameters
- `page`: Page number for pagination (1-based)
- `pageSize`: Number of items per page
- `sortBy`: Field to sort by
- `sortOrder`: Sort order (asc/desc)

### Search and Filter Parameters
- `search`: Search term for text-based filtering
- `fromDate`: Filter items from this date
- `toDate`: Filter items to this date
- `status`: Filter by status

## Common Headers

### Request Headers
- `Content-Type`: Content type of the request body
- `Authorization`: Bearer token for authentication
- `X-API-Key`: API key for service-to-service authentication

### Response Headers
- `X-Request-Id`: Request tracking identifier
- `X-RateLimit-*`: Rate limiting information
- `Location`: URL of created resource (for 201 responses)

## Navigation

- [← Back to Master Document](./api_spec.md)
- [← Error Handling](./api_spec_errors.md)
- [Customer APIs →](./api_spec_customers.md)