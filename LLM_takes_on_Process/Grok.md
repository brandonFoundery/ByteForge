Requirements Document Prompts with Traceability
This artifact contains prompts for generating the 23 documents in the requirements stack, ensuring consistency and traceability across projects. Each prompt includes instructions for maintaining a standardized structure and traceability system.
1. PRD (Product Requirements Document)
Purpose: Define the vision, goals, personas, and high-level epics for the product.Upstream: User brief.Downstream: FRD, NFRD.
Prompt:
You are an expert product manager. Your job is to create a comprehensive Product Requirements Document (PRD) based on the provided user brief.

**Traceability Instructions**:
- Assign a unique ID to each major section (e.g., PRD-1 for Vision, PRD-2 for Goals).
- Within each epic, assign sub-IDs (e.g., PRD-3.1 for Feature 1 under Epic 3).
- Include YAML front-matter with:
  - id: PRD
  - title: Product Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [User Brief]
  - downstream: [FRD, NFRD]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Vision (ID: PRD-1)
4. Goals (ID: PRD-2)
5. Personas (ID: PRD-3)
6. Epics (ID: PRD-4.x)
   - For each epic:
     - Epic Title
     - Features (ID: PRD-4.x.y)
       - Description
       - Acceptance Criteria
7. Additional Analysis

**Your reply should be a complete PRD document in Markdown format, including all traceability elements. Start with "```markdown" and end with "```".**

2. FRD (Functional Requirements Document)
Purpose: Detail user stories and acceptance criteria grouped by epic.Upstream: PRD.Downstream: DRD, BRD, UXSMD, UXDMD.
Prompt:
You are an expert product manager. Your job is to create a Functional Requirements Document (FRD) based on the provided PRD.

**Traceability Instructions**:
- Each user story or feature should reference the corresponding PRD ID.
- Assign IDs in the format FRD-<PRD-ID>.<x> (e.g., FRD-4.1 for Feature 1 under PRD Epic 4).
- Include YAML front-matter with:
  - id: FRD
  - title: Functional Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [PRD]
  - downstream: [DRD, BRD, UXSMD, UXDMD]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Features (grouped by PRD epics)
   - For each epic from PRD:
     - Epic Title (with PRD ID)
     - User Stories / Features
       - ID: FRD-<PRD-ID>.<x>
       - Description
       - Acceptance Criteria
       - Source: [PRD ID]

**Your reply should be a complete FRD document in Markdown format, including all traceability elements. Start with "```markdown" and end with "```".**

3. NFRD (Non-Functional Requirements Document)
Purpose: Define performance, security, compliance, SLA, etc.Upstream: PRD.Downstream: BRD, Test Plan.
Prompt:
You are an expert product manager. Your job is to create a Non-Functional Requirements Document (NFRD) based on the provided PRD.

**Traceability Instructions**:
- Assign IDs in the format NFRD-<n> for each non-functional requirement.
- Include YAML front-matter with:
  - id: NFRD
  - title: Non-Functional Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [PRD]
  - downstream: [BRD, Test Plan]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Non-Functional Requirements
   - For each requirement:
     - ID: NFRD-<n>
     - Description
     - Verification Method
     - Source: [PRD ID]

**Your reply should be a complete NFRD document in Markdown format, including all traceability elements. Start with "```markdown" and end with "```".**

4. DRD (Data Requirements Document)
Purpose: Define entities, data dictionary, CRUD rules, etc.Upstream: FRD.Downstream: DB-SCHEMA, API-OPEN.
Prompt:
You are an expert data architect. Your job is to create a Data Requirements Document (DRD) based on the provided FRD.

**Traceability Instructions**:
- Assign IDs in the format DRD-<FRD-ID>.<x> for each data requirement.
- Include YAML front-matter with:
  - id: DRD
  - title: Data Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [FRD]
  - downstream: [DB-SCHEMA, API-OPEN]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Entities
   - For each entity:
     - ID: DRD-<FRD-ID>.<x>
     - Name
     - Fields
     - CRUD Rules
     - Source: [FRD ID]

**Your reply should be a complete DRD document in Markdown format, including all traceability elements. Start with "```markdown" and end with "```".**

5. DB-SCHEMA (Database Schemas)
Purpose: Define logical and physical database schemas.Upstream: DRD.Downstream: API-OPEN, Server Guide.
Prompt:
You are an expert database designer. Your job is to create database schemas based on the provided DRD.

**Traceability Instructions**:
- Each table should include a `related_requirements` field listing DRD IDs.
- Use snake_case for naming.
- Include YAML front-matter with:
  - id: DB-SCHEMA
  - title: Database Schemas
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [DRD]
  - downstream: [API-OPEN, Server Guide]

**Output Format**:
YAML format with traceability:
```yaml
[TableName]:
  related_requirements: [DRD-1.1, DRD-1.2]
  - name: [columnName]
    type: [type]
    ...

Your reply should be the complete DB-SCHEMA in YAML format, including traceability. Start with "yaml" and end with "".

## 6. BRD (Backend Requirements Document)
**Purpose**: Define service responsibilities, domain services, and workflows.  
**Upstream**: FRD, NFRD.  
**Downstream**: API-OPEN, API-ASYNC.

**Prompt**:
```markdown
You are an expert software architect. Your job is to create a Backend Requirements Document (BRD) based on the provided FRD and NFRD.

**Traceability Instructions**:
- Assign IDs in the format BRD-<n> for each requirement (e.g., API endpoint, realtime event).
- Reference corresponding FRD and NFRD IDs.
- Include YAML front-matter with:
  - id: BRD
  - title: Backend Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [FRD, NFRD]
  - downstream: [API-OPEN, API-ASYNC]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. API Requirements
   - ID: BRD-<n>
   - Endpoint
   - Description
   - Related Requirements: [FRD-1.1, NFRD-1]
4. Realtime Requirements
   - ID: BRD-<m>
   - Event Name
   - Description
   - Related Requirements: [FRD-1.2]

**Your reply should be a complete BRD document in Markdown format, including all traceability elements. Start with "```markdown" and end with "```".**

7. API-OPEN (OpenAPI Specification)
Purpose: Define REST API paths, payloads, and errors.Upstream: BRD, DB-SCHEMA.Downstream: Server Guide, Test Plan, SDK Gen.
Prompt:
You are an expert API designer. Your job is to create an OpenAPI 3.0.0 specification based on the BRD and DB-SCHEMA.

**Traceability Instructions**:
- Include `x-requirement-ids` in each path’s description to list related BRD IDs.
- Include YAML front-matter with:
  - id: API-OPEN
  - title: OpenAPI Specification
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [BRD, DB-SCHEMA]
  - downstream: [Server Guide, Test Plan, SDK Gen]

**Output Format**:
OpenAPI 3.0.0 YAML with traceability:
```yaml
paths:
  /users:
    get:
      summary: Get users
      x-requirement-ids: [BRD-1]
      ...

Your reply should be the complete OpenAPI specification in YAML format, including traceability. Start with "yaml" and end with "".

## 8. API-ASYNC (AsyncAPI Specification)
**Purpose**: Define event-driven topics and payloads.  
**Upstream**: BRD.  
**Downstream**: Message Broker Implementation.

**Prompt**:
```markdown
You are an expert API designer. Your job is to create an AsyncAPI specification based on the BRD.

**Traceability Instructions**:
- Include `x-requirement-ids` for each topic to list related BRD IDs.
- Include YAML front-matter with:
  - id: API-ASYNC
  - title: AsyncAPI Specification
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [BRD]
  - downstream: [Message Broker Implementation]

**Output Format**:
AsyncAPI YAML with traceability:
```yaml
channels:
  user/created:
    x-requirement-ids: [BRD-2]
    ...

Your reply should be the complete AsyncAPI specification in YAML format, including traceability. Start with "yaml" and end with "".

## 9. SERVER-GUIDE (Implementation & Ops Guide)
**Purpose**: Define folder structure, DevOps, and observability hooks.  
**Upstream**: API-OPEN, API-ASYNC, BRD.  
**Downstream**: DevOps, SRE.

**Prompt**:
```markdown
You are an expert DevOps engineer. Your job is to create a Server Implementation & Ops Guide based on the API-OPEN, API-ASYNC, and BRD.

**Traceability Instructions**:
- Reference related BRD IDs for each section.
- Include YAML front-matter with:
  - id: SERVER-GUIDE
  - title: Server Implementation & Ops Guide
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [API-OPEN, API-ASYNC, BRD]
  - downstream: [DevOps, SRE]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Folder Structure
   - Description
   - Related Requirements: [BRD-1]
4. DevOps Configuration
5. Observability Hooks

**Your reply should be a complete guide in Markdown format, including traceability. Start with "```markdown" and end with "```".**

10. UXSMD (UX Site-Map Requirements Document)
Purpose: Define navigation hierarchy and route guard rules.Upstream: FRD.Downstream: UX-SM-STRUCT.
Prompt:
You are an expert UX designer. Your job is to create a UX Site-Map Requirements Document based on the FRD.

**Traceability Instructions**:
- Assign IDs in the format UXSMD-<FRD-ID>.<x> for each view or navigation rule.
- Include YAML front-matter with:
  - id: UXSMD
  - title: UX Site-Map Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [FRD]
  - downstream: [UX-SM-STRUCT]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Navigation Hierarchy
   - ID: UXSMD-<FRD-ID>.<x>
   - View Name
   - Route Guard Rules
   - Source: [FRD ID]

**Your reply should be a complete UXSMD document in Markdown format, including traceability. Start with "```markdown" and end with "```".**

11. UX-SM-STRUCT (UX Sitemap Structure JSON)
Purpose: Provide a machine-readable sitemap tree.Upstream: UXSMD.Downstream: REACT-ROOT.
Prompt:
You are an expert UX designer. Your job is to create a UX Sitemap Structure in JSON based on the UXSMD.

**Traceability Instructions**:
- Include `related_requirements` for each view referencing UXSMD IDs.
- Include YAML front-matter with:
  - id: UX-SM-STRUCT
  - title: UX Sitemap Structure
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [UXSMD]
  - downstream: [REACT-ROOT]

**Output Format**:
JSON with traceability:
```json
{
  "views": [
    {
      "id": "UV_Landing",
      "related_requirements": ["UXSMD-1.1"],
      ...
    }
  ]
}

Your reply should be the complete sitemap in JSON format, including traceability. Start with "json" and end with "".

## 12. UXDMD (UX Data-Map Requirements Document)
**Purpose**: Define data needs per screen.  
**Upstream**: FRD, API-OPEN.  
**Downstream**: UX-DM-STRUCT.

**Prompt**:
```markdown
You are an expert UX designer. Your job is to create a UX Data-Map Requirements Document based on the FRD and API-OPEN.

**Traceability Instructions**:
- Assign IDs in the format UXDMD-<FRD-ID>.<x> for each data requirement.
- Include YAML front-matter with:
  - id: UXDMD
  - title: UX Data-Map Requirements Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [FRD, API-OPEN]
  - downstream: [UX-DM-STRUCT]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Data Needs
   - ID: UXDMD-<FRD-ID>.<x>
   - Screen
   - Data Requirements
   - Source: [FRD ID, API-OPEN ID]

**Your reply should be a complete UXDMD document in Markdown format, including traceability. Start with "```markdown" and end with "```".**

13. UX-DM-STRUCT (UX Data Map Structure JSON)
Purpose: Provide a normalized data map with React-store bindings.Upstream: UXDMD.Downstream: REACT-STORE.
Prompt:
You are an expert UX designer. Your job is to create a UX Data Map Structure in JSON based on the UXDMD.

**Traceability Instructions**:
- Include `related_requirements` for each data binding referencing UXDMD IDs.
- Include YAML front-matter with:
  - id: UX-DM-STRUCT
  - title: UX Data Map Structure
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [UXDMD]
  - downstream: [REACT-STORE]

**Output Format**:
JSON with traceability:
```json
{
  "screens": [
    {
      "id": "UV_Landing",
      "related_requirements": ["UXDMD-1.1"],
      ...
    }
  ]
}

Your reply should be the complete data map in JSON format, including traceability. Start with "json" and end with "".

## 14. UX-DM-VIEWS (UX Data Map Views JSON)
**Purpose**: Define view-specific data slices.  
**Upstream**: UX-DM-STRUCT.  
**Downstream**: REACT-VIEW-GEN.

**Prompt**:
```markdown
You are an expert UX designer. Your job is to create a UX Data Map Views JSON based on the UX-DM-STRUCT.

**Traceability Instructions**:
- Include `related_requirements` for each view referencing UX-DM-STRUCT IDs.
- Include YAML front-matter with:
  - id: UX-DM-VIEWS
  - title: UX Data Map Views
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [UX-DM-STRUCT]
  - downstream: [REACT-VIEW-GEN]

**Output Format**:
JSON with traceability:
```json
{
  "views": [
    {
      "id": "UV_Landing",
      "related_requirements": ["UX-DM-STRUCT-1"],
      ...
    }
  ]
}

Your reply should be the complete views JSON, including traceability. Start with "json" and end with "".

## 15. REACT-STORE (React Global Store Specification)
**Purpose**: Define state tree, reducers, and RTK query hooks.  
**Upstream**: UX-DM-STRUCT.  
**Downstream**: Developers.

**Prompt**:
```markdown
You are an expert React developer. Your job is to create a React Global Store Specification based on the UX-DM-STRUCT.

**Traceability Instructions**:
- Include comments referencing UX-DM-STRUCT IDs for each state slice.
- Include YAML front-matter with:
  - id: REACT-STORE
  - title: React Global Store Specification
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [UX-DM-STRUCT]
  - downstream: [Developers]

**Output Format**:
TypeScript code with traceability comments:
```typescript
// State slice for UV_Landing, see UX-DM-STRUCT-1
const landingSlice = createSlice({
  ...
});

Your reply should be the complete store specification in TypeScript, including traceability. Start with "typescript" and end with "".

## 16. REACT-ROOT (Root App Shell Specification)
**Purpose**: Define app provider wiring, routing, and theming.  
**Upstream**: UX-SM-STRUCT.  
**Downstream**: Developers.

**Prompt**:
```markdown
You are an expert React developer. Your job is to create a React Root Component Specification based on the UX-SM-STRUCT.

**Traceability Instructions**:
- Include comments referencing UX-SM-STRUCT IDs for each route.
- Include YAML front-matter with:
  - id: REACT-ROOT
  - title: React Root Component Specification
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [UX-SM-STRUCT]
  - downstream: [Developers]

**Output Format**:
TypeScript JSX with traceability comments:
```tsx
// Route for UV_Landing, see UX-SM-STRUCT-1
<Route path="/" element={<UV_Landing />} />

Your reply should be the complete root component in TypeScript JSX, including traceability. Start with "tsx" and end with "".

## 17. REACT-VIEW-GEN (Generated View Blueprint)
**Purpose**: Provide skeleton JSX with placeholder data hooks.  
**Upstream**: UX-DM-VIEWS.  
**Downstream**: Designers, Developers.

**Prompt**:
```markdown
You are an expert React developer. Your job is to create a Generated View Blueprint based on the UX-DM-VIEWS.

**Traceability Instructions**:
- Include comments referencing UX-DM-VIEWS IDs for each view.
- Include YAML front-matter with:
  - id: REACT-VIEW-GEN
  - title: Generated View Blueprint
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [UX-DM-VIEWS]
  - downstream: [Designers, Developers]

**Output Format**:
TypeScript JSX with traceability comments:
```tsx
// View for UV_Landing, see UX-DM-VIEWS-1
const UV_Landing: React.FC = () => {
  ...
};

Your reply should be the complete view blueprint in TypeScript JSX, including traceability. Start with "tsx" and end with "".

## 18. LAYOUT-DOC (Design-System / Layout Document)
**Purpose**: Provide Figma/Storybook references and accessibility notes.  
**Upstream**: REACT-VIEW-GEN.  
**Downstream**: Component Library.

**Prompt**:
```markdown
You are an expert designer. Your job is to create a Design-System / Layout Document based on the REACT-VIEW-GEN.

**Traceability Instructions**:
- Reference REACT-VIEW-GEN IDs for each layout.
- Include YAML front-matter with:
  - id: LAYOUT-DOC
  - title: Design-System / Layout Document
  - version: 1.0
  - status: Draft
  - created_by: [Your Name]
  - created_on: 2025-06-10
  - last_updated: 2025-06-10
  - upstream: [REACT-VIEW-GEN]
  - downstream: [Component Library]

**Document Structure**:
1. YAML Front-Matter
2. Introduction
3. Layouts
   - ID: LAYOUT-DOC-<n>
   - Figma/Storybook Reference
   - Accessibility Notes
   - Source: [REACT-VIEW-GEN ID]

**Your reply should be a complete layout document in Markdown format, including traceability. Start with "```markdown" and end with "```".**

19. LIB-INDEX (Component Library Index)
Purpose: Provide Storybook/Chromatic links and props table.Upstream: LAYOUT-DOC.Downstream: Developers.
Prompt:
You are an expert designer. Your job is to create a Component Library Index based on the LAYOUT-DOC.

**

