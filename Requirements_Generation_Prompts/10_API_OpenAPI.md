# OpenAPI Specification Document - Prompt Template

## Primary Prompt

```markdown
You are an expert API Architect and Backend Developer with extensive experience designing RESTful APIs and creating comprehensive OpenAPI 3.0 specifications. You excel at translating functional requirements into well-structured, developer-friendly API contracts.

## Your Task

Generate a complete OpenAPI 3.0 Specification for [PROJECT NAME] based on the provided functional requirements and technical architecture.

**IMPORTANT: Split Document Structure**
Your generated specification will be automatically split into multiple linked documents for better maintainability:

1. **Master Document** - Overview, basic OpenAPI info, and navigation links
2. **Security Schemes** - Authentication and authorization patterns
3. **Common Components** - Reusable schemas and data models
4. **Error Handling** - Standardized error response patterns
5. **Common Patterns** - Shared parameters, headers, response structures
6. **Feature Documents** - Separate documents for each major functional area:
   - Customer Management APIs
   - Payment Processing APIs
   - Load Booking and Tracking APIs
   - Invoice Processing and Reporting APIs
   - Carrier Management APIs

Generate the complete specification as a single comprehensive document, and the system will automatically extract and organize the content into the appropriate split documents.

## Input Context Required

1. **Architecture Document**: [Complete Architecture Document with foundational architecture and technology stack]
2. **Functional Requirements Document**: [Complete FRD with data operations]
3. **Data Requirements Document**: [DRD with entity definitions]
4. **Technical Requirements Document**: [TRD with integration patterns]
5. **Non-Functional Requirements**: [Performance, security requirements]
6. **Technology Stack**: [ASP.NET Core 8.0+ with Azure services]
7. **Authentication Strategy**: [Azure AD B2C, JWT tokens, OAuth 2.0]

## Document Structure Requirements

Your OpenAPI specification must include the following with proper metadata:

```yaml
openapi: 3.0.3
info:
  title: [PROJECT NAME] API
  description: |
    # [PROJECT NAME] RESTful API
    
    This API provides comprehensive access to [PROJECT NAME] functionality.
    
    ## Authentication
    [Describe authentication method]
    
    ## Rate Limiting
    [Describe rate limits]
    
    ## Versioning
    [Describe versioning strategy]
    
    ## Traceability
    - Source Requirements: [FRD, DRD references]
    - Implementation Guide: [TRD references]
  version: 1.0.0
  contact:
    name: API Support Team
    email: api-support@example.com
    url: https://api-docs.example.com
  license:
    name: Proprietary
    url: https://example.com/license
servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server
  - url: http://localhost:8080/v1
    description: Development server
```

### 1. Security Schemes

```yaml
components:
  securitySchemes:
    azureADB2C:
      type: oauth2
      description: |
        Azure Active Directory B2C authentication.
        Supports multiple identity providers and custom policies.
        Source: Architecture Document - Security Architecture
      flows:
        authorizationCode:
          authorizationUrl: https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{policy}/oauth2/v2.0/authorize
          tokenUrl: https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{policy}/oauth2/v2.0/token
          scopes:
            https://{tenant}.onmicrosoft.com/{api}/user_impersonation: Access API on behalf of user
            https://{tenant}.onmicrosoft.com/{api}/read: Read access to resources
            https://{tenant}.onmicrosoft.com/{api}/write: Write access to resources

    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT token obtained from Azure AD B2C.
        Required for all authenticated endpoints.
        Token validation performed by ASP.NET Core JWT middleware.

    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
      description: |
        API key for service-to-service communication.
        Managed through Azure API Management.
        Contact support for API key generation.

security:
  - azureADB2C: []
  - bearerAuth: []
```

### 2. Common Components

```yaml
components:
  schemas:
    # Error Response Schema
    Error:
      type: object
      required:
        - code
        - message
        - timestamp
        - path
      properties:
        code:
          type: string
          description: Error code for programmatic handling
          example: "VALIDATION_ERROR"
        message:
          type: string
          description: Human-readable error message
          example: "Validation failed for field 'email'"
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
        timestamp:
          type: string
          format: date-time
          example: "2025-06-10T12:00:00Z"
        path:
          type: string
          example: "/api/v1/users"
        traceId:
          type: string
          description: Correlation ID for tracking
          example: "550e8400-e29b-41d4-a716-446655440000"
    
    # Pagination Schema
    Pagination:
      type: object
      properties:
        page:
          type: integer
          minimum: 1
          default: 1
        pageSize:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
        totalPages:
          type: integer
          example: 10
        totalItems:
          type: integer
          example: 200
        hasNext:
          type: boolean
        hasPrevious:
          type: boolean
```

### 3. Resource Schemas

For each major entity from DRD:

```yaml
components:
  schemas:
    # Customer Schema (Source: DRD-ENTITY-001)
    Customer:
      type: object
      required:
        - companyName
        - email
        - phone
      properties:
        customerId:
          type: string
          format: uuid
          readOnly: true
          description: Unique identifier
          example: "550e8400-e29b-41d4-a716-446655440000"
        customerNumber:
          type: string
          readOnly: true
          pattern: "^CUS-[0-9]{6}$"
          description: Human-readable customer number
          example: "CUS-123456"
        companyName:
          type: string
          minLength: 1
          maxLength: 255
          description: Legal company name
          example: "Acme Corporation"
        email:
          type: string
          format: email
          description: Primary contact email
          example: "contact@acme.com"
        phone:
          type: string
          pattern: "^\\+?[1-9]\\d{1,14}$"
          description: E.164 format phone number
          example: "+1234567890"
        creditLimit:
          type: number
          format: decimal
          minimum: 0
          description: Maximum credit allowed
          example: 50000.00
        status:
          type: string
          enum: [ACTIVE, INACTIVE, SUSPENDED]
          description: Account status
          example: "ACTIVE"
        metadata:
          type: object
          additionalProperties: true
          description: Additional custom fields
        createdAt:
          type: string
          format: date-time
          readOnly: true
        updatedAt:
          type: string
          format: date-time
          readOnly: true
    
    CustomerInput:
      allOf:
        - $ref: '#/components/schemas/Customer'
        - type: object
          required:
            - companyName
            - email
            - phone
          properties:
            customerId:
              readOnly: true
            customerNumber:
              readOnly: true
            createdAt:
              readOnly: true
            updatedAt:
              readOnly: true
```

### 4. API Endpoints

For each functional requirement:

```yaml
paths:
  # Customer Management (Source: FRD-001)
  /customers:
    get:
      tags:
        - Customers
      summary: List customers
      description: |
        Retrieve a paginated list of customers with optional filtering.
        
        **Source Requirements:**
        - FRD-001: Customer list retrieval
        - NFR-PERF-001: Response time <200ms
      operationId: listCustomers
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: pageSize
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: status
          in: query
          schema:
            type: string
            enum: [ACTIVE, INACTIVE, SUSPENDED]
          description: Filter by status
        - name: search
          in: query
          schema:
            type: string
          description: Search in company name or email
        - name: sortBy
          in: query
          schema:
            type: string
            enum: [companyName, createdAt, creditLimit]
            default: companyName
        - name: sortOrder
          in: query
          schema:
            type: string
            enum: [asc, desc]
            default: asc
      responses:
        '200':
          description: Customer list retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Customer'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
              examples:
                success:
                  value:
                    data:
                      - customerId: "550e8400-e29b-41d4-a716-446655440000"
                        customerNumber: "CUS-123456"
                        companyName: "Acme Corporation"
                        email: "contact@acme.com"
                        phone: "+1234567890"
                        creditLimit: 50000.00
                        status: "ACTIVE"
                        createdAt: "2025-06-01T10:00:00Z"
                        updatedAt: "2025-06-10T15:30:00Z"
                    pagination:
                      page: 1
                      pageSize: 20
                      totalPages: 10
                      totalItems: 200
                      hasNext: true
                      hasPrevious: false
        '400':
          description: Bad request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '403':
          description: Forbidden
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []
      x-rate-limit:
        requests: 100
        period: minute
    
    post:
      tags:
        - Customers
      summary: Create customer
      description: |
        Create a new customer account.
        
        **Source Requirements:**
        - FRD-002: Customer creation
        - BR-001: Credit limit validation
      operationId: createCustomer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomerInput'
            examples:
              newCustomer:
                value:
                  companyName: "New Company Ltd"
                  email: "contact@newcompany.com"
                  phone: "+1234567890"
                  creditLimit: 25000.00
                  metadata:
                    industry: "Technology"
                    employees: 50
      responses:
        '201':
          description: Customer created successfully
          headers:
            Location:
              schema:
                type: string
              description: URL of created resource
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                validationError:
                  value:
                    code: "VALIDATION_ERROR"
                    message: "Validation failed"
                    details:
                      - field: "email"
                        message: "Email already exists"
                    timestamp: "2025-06-10T12:00:00Z"
                    path: "/api/v1/customers"
        '409':
          description: Conflict - duplicate customer
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []
  
  /customers/{customerId}:
    parameters:
      - name: customerId
        in: path
        required: true
        schema:
          type: string
          format: uuid
        description: Customer unique identifier
    
    get:
      tags:
        - Customers
      summary: Get customer details
      description: |
        Retrieve detailed information for a specific customer.
        
        **Source Requirements:**
        - FRD-003: Customer detail retrieval
      operationId: getCustomer
      responses:
        '200':
          description: Customer details retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '404':
          description: Customer not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []
    
    put:
      tags:
        - Customers
      summary: Update customer
      description: |
        Update an existing customer's information.
        
        **Source Requirements:**
        - FRD-004: Customer update
        - BR-002: Status change validation
      operationId: updateCustomer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomerInput'
      responses:
        '200':
          description: Customer updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: Customer not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Conflict - concurrent update
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []
    
    delete:
      tags:
        - Customers
      summary: Delete customer
      description: |
        Soft delete a customer (set status to INACTIVE).
        
        **Source Requirements:**
        - FRD-005: Customer deletion
        - BR-003: Cannot delete with active orders
      operationId: deleteCustomer
      responses:
        '204':
          description: Customer deleted successfully
        '400':
          description: Cannot delete - business rule violation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: Customer not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
      security:
        - bearerAuth: []
```

### 5. Webhooks (if applicable)

```yaml
webhooks:
  customerCreated:
    post:
      summary: Customer created event
      description: |
        Webhook triggered when a new customer is created.
        
        **Source Requirements:**
        - FRD-020: Event notifications
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                eventType:
                  type: string
                  enum: [customer.created]
                eventId:
                  type: string
                  format: uuid
                timestamp:
                  type: string
                  format: date-time
                data:
                  $ref: '#/components/schemas/Customer'
      responses:
        '200':
          description: Webhook processed successfully
        '400':
          description: Bad request
```

### 6. API Tags and Groups

```yaml
tags:
  - name: Authentication
    description: |
      Authentication and authorization endpoints
      
      **Related Requirements:**
      - FRD-AUTH-*: Authentication requirements
      - NFR-SEC-001: Security requirements
    
  - name: Customers
    description: |
      Customer management operations
      
      **Related Requirements:**
      - FRD-CUST-*: Customer management
      - DRD-ENTITY-001: Customer data model
    
  - name: Orders
    description: |
      Order processing and management
      
      **Related Requirements:**
      - FRD-ORD-*: Order management
      - DRD-ENTITY-002: Order data model
```

### 7. Request/Response Examples

For each endpoint, provide comprehensive examples:

```yaml
paths:
  /auth/login:
    post:
      tags:
        - Authentication
      summary: User login
      requestBody:
        content:
          application/json:
            examples:
              emailLogin:
                summary: Login with email
                value:
                  email: "user@example.com"
                  password: "SecurePass123!"
              usernameLogin:
                summary: Login with username
                value:
                  username: "john.doe"
                  password: "SecurePass123!"
              mfaLogin:
                summary: Login with MFA
                value:
                  email: "user@example.com"
                  password: "SecurePass123!"
                  mfaCode: "123456"
```

## Traceability Instructions

1. **Requirement Mapping**: Link each endpoint to source requirements
2. **Schema References**: Map schemas to DRD entities
3. **Security Implementation**: Reference security NFRs
4. **Performance Constraints**: Note relevant performance NFRs
5. **Business Rules**: Document validation rules from FRD

## Quality Criteria

Your OpenAPI specification must:
- Be valid OpenAPI 3.0 syntax
- Include all CRUD operations from FRD
- Define all request/response schemas
- Document all error scenarios
- Include authentication details
- Provide comprehensive examples
- Map to requirements for traceability
- Support API versioning strategy

## Output Format

Provide the complete OpenAPI specification in YAML format with:
- Full metadata and server configuration
- Security scheme definitions
- Reusable component schemas
- Complete endpoint definitions
- Request/response examples
- Error handling patterns
- Webhook definitions (if applicable)

## Chain-of-Thought Instructions

When creating the API specification:
1. Extract all data operations from FRD
2. Map entities from DRD to schemas
3. Design RESTful endpoints
4. Define security requirements
5. Add validation rules
6. Include error responses
7. Provide rich examples
8. Document rate limits
```

## Iterative Refinement Prompts

### Refinement Round 1: Completeness
```markdown
Review the OpenAPI spec and enhance it by:
1. Ensuring all FRD operations have endpoints
2. Adding missing schema properties
3. Including all validation rules
4. Documenting all error codes
5. Adding missing examples
```

### Refinement Round 2: Best Practices
```markdown
Refine the OpenAPI spec by:
1. Ensuring RESTful design principles
2. Optimizing endpoint structures
3. Improving schema reusability
4. Standardizing error responses
5. Enhancing security definitions
```

### Refinement Round 3: Developer Experience
```markdown
Enhance the OpenAPI spec by:
1. Adding more detailed descriptions
2. Providing richer examples
3. Improving parameter documentation
4. Clarifying authentication flows
5. Adding SDK generation hints

## Iterative Requirements Elicitation

After generating the initial API OpenAPI Specification Document, perform a comprehensive analysis to identify gaps, ambiguities, and areas requiring clarification. Create a structured list of questions for the client that will help refine and complete the API requirements.

### 10. Client Clarification Questions

Think critically about API endpoints, data models, authentication, error handling, performance, and integration patterns that might not have been fully considered or might be unclear. Generate specific, actionable questions organized by category:

```yaml
id: API-QUESTION-001
category: [Endpoints|Data Models|Authentication|Error Handling|Performance|Versioning|Security|Integration|Other]
question: [Specific question for the client]
rationale: [Why this question is important for API success]
related_requirements: [API-XXX, TRD-XXX, or FRD-XXX references if applicable]
priority: High|Medium|Low
expected_impact: [How the answer will affect the API requirements]
```

#### Question Categories:

**API-Specific Questions:**
- Clarifications on API design, data schemas, integration patterns, and service contracts
- Edge cases and exception scenarios
- Integration and dependency requirements
- Performance and quality expectations
- Compliance and governance needs

### Instructions for Question Generation:

1. **Be Specific**: Ask precise questions that will yield actionable answers
2. **Prioritize Impact**: Focus on questions that will significantly affect API requirements
3. **Consider Edge Cases**: Think about unusual scenarios and exceptions
4. **Validate Assumptions**: Question any assumptions made in the initial requirements
5. **Ensure Completeness**: Look for gaps in API design, data schemas, integration patterns, and service contracts
6. **Think Downstream**: Consider how answers will affect implementation
7. **Maintain Traceability**: Link questions to specific requirements when applicable

### Answer Integration Process:

When client answers are received, they should be integrated back into the API OpenAPI Specification Document using this process:

1. **Create Answer Records**:
```yaml
id: API-ANSWER-001
question_id: API-QUESTION-001
answer: [Client's response]
provided_by: [Stakeholder name/role]
date_received: YYYY-MM-DD
impact_assessment: [How this affects existing requirements]
```

2. **Update Affected Requirements**: Modify existing requirements based on answers
3. **Create New Requirements**: Add new requirements identified through answers
4. **Update Traceability**: Ensure all changes maintain proper traceability links
5. **Document Changes**: Track what was modified and why

This iterative approach ensures comprehensive API requirements that address all critical aspects and reduce implementation risks.

```

## Validation Checklist

Before finalizing the OpenAPI spec, ensure:

- [ ] Valid OpenAPI 3.0 syntax (use validator)
- [ ] All CRUD operations implemented
- [ ] Schemas match DRD entities
- [ ] Security properly configured
- [ ] Error responses standardized
- [ ] Examples are realistic
- [ ] Rate limits documented
- [ ] Versioning strategy clear
- [ ] Traceability maintained
- [ ] Developer-friendly documentation

## Pro Tips for LLM Users

1. **FRD First**: Extract all operations from functional requirements
2. **RESTful Design**: Follow REST principles consistently
3. **Schema Reuse**: Define common components once
4. **Rich Examples**: Provide multiple realistic examples
5. **Error Patterns**: Standardize error responses
6. **Security Focus**: Document auth clearly
7. **Version Ready**: Design for API evolution
8. **Split-Ready**: Organize content clearly by functional areas for automatic splitting

## Split Document Generation

When generating the API specification, ensure clear organization by functional areas:

### Customer Management Section
- Include all `/customers` endpoints
- Customer-related schemas and examples
- Customer-specific error responses

### Payment Processing Section
- Include all `/payments` endpoints
- Payment-related schemas and examples
- Payment-specific error responses

### Load Management Section
- Include all `/loads` endpoints and `/loads/{id}/track`
- Load-related schemas and examples
- Load-specific error responses

### Invoice Processing Section
- Include all `/invoices` and `/reports/financial` endpoints
- Invoice-related schemas and examples
- Invoice-specific error responses

### Carrier Management Section
- Include all `/carrier/*` endpoints
- Carrier-related schemas and examples
- Carrier-specific error responses

The generation system will automatically extract these sections and create linked documents for better maintainability.

## Example Usage

```markdown
Generate an OpenAPI spec using this template with the following context:
- FRD: "Customer CRUD operations, Order processing, Payment handling..."
- DRD: "Customer entity with 15 fields, Order with line items..."
- Auth: "JWT tokens with 1-hour expiry, OAuth2 for partners..."
- Performance: "100ms response time, 1000 requests/minute limit..."
[Continue with all required inputs]