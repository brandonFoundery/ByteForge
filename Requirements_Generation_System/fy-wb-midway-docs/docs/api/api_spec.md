# LSOMigrator Enterprise Logistics Platform API

## Overview

This is the master document for the LSOMigrator Enterprise Logistics Platform API specification. The complete API documentation is organized into multiple linked documents for better maintainability and navigation.

## OpenAPI Specification

        - customerId
        - name
        - email
            - pending
            - completed
            - failed
        - paymentId
        - amount
        - itemId
        - name
        - quantity
        - Customer Management
        - Customer Management
        - Payment Processing

## Document Structure

The complete API specification is organized into the following documents:

### Architecture Documents
- **[Security Schemes](./api_spec_security.md)** - Authentication and authorization patterns
- **[Common Components](./api_spec_components.md)** - Reusable schemas and data models

### Cross-cutting Concerns
- **[Error Handling](./api_spec_errors.md)** - Standardized error response patterns
- **[Common Patterns](./api_spec_common.md)** - Shared parameters, headers, and response structures

### Feature-Specific API Endpoints

#### Customer Management
- **[Customer APIs](./api_spec_customers.md)** - Customer onboarding and management endpoints

#### Payment Processing
- **[Payment APIs](./api_spec_payments.md)** - Secure payment processing endpoints

#### Load Management
- **[Load APIs](./api_spec_loads.md)** - Load booking and tracking endpoints

#### Invoice Processing
- **[Invoice APIs](./api_spec_invoices.md)** - Invoice generation and reporting endpoints

#### Carrier Management
- **[Carrier APIs](./api_spec_carriers.md)** - Carrier registration and self-service endpoints

## Navigation

- [← Back to Requirements](../Requirements/)
- [Security Schemes →](./api_spec_security.md)
- [Common Components →](./api_spec_components.md)

## Traceability Matrix

| Document | Requirements Covered | Endpoints |
|----------|---------------------|-----------|
| [Customer APIs](./api_spec_customers.md) | FRD-3.1.1, DRD-2.1 | /customers |
| [Payment APIs](./api_spec_payments.md) | FRD-3.1.2 | /payments |
| [Load APIs](./api_spec_loads.md) | FRD-3.2.1, FRD-3.2.2, DRD-2.2 | /loads, /loads/{id}/track |
| [Invoice APIs](./api_spec_invoices.md) | FRD-3.3.1, FRD-3.3.2, DRD-2.3 | /invoices, /reports/financial |
| [Carrier APIs](./api_spec_carriers.md) | FRD-3.4.1, FRD-3.4.2, DRD-2.4 | /carrier/* |