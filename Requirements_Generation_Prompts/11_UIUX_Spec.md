# UI/UX Specification Document (UXDMD) – Prompt Template

> Optimised for multi-tenant SaaS apps built with LLM-assisted pipelines

You are an **expert UI/UX Designer, Front-end Architect, and Technical Writer** with a proven track record of shipping enterprise-grade, multi-tenant SaaS platforms.
Your deliverable is a **COMPREHENSIVE, DEVELOPER-READY UI/UX Design & Mapping Document (UXDMD)** for **\[PROJECT NAME]**, fully traceable to source requirements.

**🚨 CRITICAL INSTRUCTION: You MUST analyze the ACTUAL requirements provided in the FRD document context. Do NOT rely on template examples. Extract EVERY requirement ID (REQ-FUNC-001, REQ-FUNC-020, etc.) and ensure ALL functional areas are covered in your UI/UX specification, including CRM functionality, broker roles, pipeline management, kanban boards, and any other features mentioned in the requirements.**

**📋 ARTIFACT INTEGRATION REQUIREMENTS:**
1. **Visual References**: If screenshots or competitor analysis exist in /Requirements_Artifacts/visual_references/, reference them explicitly and extract UI patterns
2. **Detailed Specs**: If functional requirements exist in /Requirements_Artifacts/detailed_specs/, use them as the PRIMARY source, not generic templates
3. **JSON Blueprints**: If UI specifications exist in /Requirements_Artifacts/json_blueprints/, implement them exactly as specified
4. **User Stories**: If user scenarios exist in /Requirements_Artifacts/user_stories/, ensure all user journeys are covered
5. **Acceptance Criteria**: If testable criteria exist in /Requirements_Artifacts/acceptance_criteria/, include them in the specifications

**🎯 SPECIFICITY MANDATE**: When detailed requirements exist (like FR-01 to FR-10 style functional requirements), you MUST implement every single requirement with full fidelity. Generic templates are ONLY used when specific requirements are missing.**

---

## MUST-HAVE UP-FRONT CONTEXT

1. **Functional Requirements Document** (FRD)
2. **Product Requirements Document** (PRD)
3. **API / OpenAPI Spec**
4. **Technical Requirements Doc** (TRD)
5. **Brand & Theme Catalogue** – include at least one named **STYLE\_ID** to lock-in before code generation *(e.g., “brand-default-2025” or “customer-blue-dark”)*

---

## CRITICAL CONTENT REQUIREMENTS

* ≥ 3 000 words total
* Full completion of every section listed below
* **Explicit partitioning** of views into **Public**, **Tenant (Authenticated)**, and **Admin** areas
* **Permissions & Role Matrix** per view, component, and API call
* Reference the chosen **STYLE\_ID** and surface all **design tokens** (colours, typography, spacing, motion)
* Complete traceability to FRD, PRD, API endpoints, NFRs

---

## MANDATORY SECTIONS & MINIMUM DEPTH

1. Purpose & Scope (300 + words)
2. **Application Context & SaaS Partitioning** (300 + words) ⚠️ *new*
3. Screen / View Catalogue (400 + words)
4. **Role & Permission Mapping** (250 + words + matrix) ⚠️ *new*
5. Information Architecture (300 + words)
6. Data Map (200 + words)
7. Per-View Specifications (1 000 + words in total)
8. Interaction Flows (300 + words)
9. Visual & **Style-Theme Guidelines** (250 + words) ⚠️ *expanded*
10. Performance Requirements (200 + words)
11. Security Requirements (200 + words)
12. Component Library Integration (200 + words)
13. Form Specifications
14. Open Issues / Questions

*(Section numbering adjusted; update downstream references as needed.)*

---

## UPDATED FRONT-MATTER (YAML)

```yaml
docCode: UXDMD
version: 1.0
derivedFrom:
  - FRD-*
  - PRD-*
  - API-OPEN-*
authors: [UX-Lead, Frontend-Architect]
updated: 2025-06-18
generated_at: [TIMESTAMP]
id: UIUX_SPEC
status: generated
refined_count: 0
style_id: [SELECTED STYLE_ID]      # <-- lock theme before coding
tenant_model: multi-tenant-saas    # enum: single-tenant | multi-tenant-saas
partitions:
  - public
  - tenant
  - admin
```

---

## 1 Purpose & Scope

*(unchanged – include SaaS-specific business goals, personas, devices, WCAG 2.2 AA, supported browsers, etc.)*

## 2 Application Context & SaaS Partitioning ⚠️

Describe how the application is segmented:

| Partition  | Description                      | Typical Routes             | AuthN    | AuthZ Strategy          | Example Roles                |
| ---------- | -------------------------------- | -------------------------- | -------- | ----------------------- | ---------------------------- |
| **Public** | Marketing & onboarding pages     | `/`, `/pricing`, `/signup` | Optional | N/A                     | anonymous                    |
| **Tenant** | Authenticated customer workspace | `/app`, `/app/*`           | Required | RBAC per tenant         | viewer, editor               |
| **Admin**  | Global or tenant-admin consoles  | `/admin`, `/tenant-admin`  | Required | RBAC + tenant isolation | platform-admin, tenant-admin |

State cross-partition navigation rules, deep-link constraints, and brand-override mechanisms (e.g., tenant-level themes or logo swaps).

## 3 Screen / View Catalogue

*Add two new columns:* **Partition** (Public / Tenant / Admin) and **Auth Level** (Anonymous | Authenticated | Role\:XYZ).

| View-ID          | Title     | Route            | Partition | Upstream FRD | API Endpoint(s)          | Auth Level           |
| ---------------- | --------- | ---------------- | --------- | ------------ | ------------------------ | -------------------- |
| `view-home`      | Home      | `/`              | Public    | REQ-FUNC-001 | —                        | Anonymous            |
| `view-dashboard` | Dashboard | `/app/dashboard` | Tenant    | REQ-FUNC-003 | `GET /dashboard/metrics` | Role\:user           |
| `view-crm-board` | CRM Board | `/app/crm`       | Tenant    | REQ-FUNC-020 | `GET /crm/pipeline`      | Role\:broker         |
| `view-user-mgmt` | User Mgmt | `/admin/users`   | Admin     | REQ-FUNC-015 | `GET/POST /admin/users`  | Role\:platform-admin |

**IMPORTANT**: Use the ACTUAL requirement IDs from the provided FRD document, not these examples. These are just format examples.

## 4 Role & Permission Mapping ⚠️

Provide a matrix linking **Roles → Permissions → Views/Components → API endpoints**.

| Role             | Inherits | Permissions                                         | Views              | API Endpoints |
| ---------------- | -------- | --------------------------------------------------- | ------------------ | ------------- |
| `platform-admin` | —        | `user.manage`, `billing.view`, `tenant.impersonate` | user-mgmt, billing | `/admin/*`    |
| `tenant-admin`   | user     | `user.manage`, `billing.view`                       | team-mgmt          | `/tenant/*`   |
| `user`           | —        | `data.read`, `data.write`                           | dashboard          | `/app/*`      |

Document default vs tenant-overridden roles, and any feature-flag gates.

## 5 Information Architecture & Navigation

*(Emphasise partition-aware menus, breadcrumb patterns, guard rules, and lazy-loaded route chunks.)*

## 6 Data Map

*(Unchanged structure – ensure caching and security columns reflect tenant isolation.)*

## 7 Per-View Specification

Add these **extra fields**: `Partition`, `Required Permissions`, `Style Tokens Used`.
Example row snippet:

| **Partition**            | Tenant                            |
| ------------------------ | --------------------------------- |
| **Required Permissions** | `data.read`                       |
| **Style Tokens Used**    | `color.primary.500`, `spacing.md` |

## 8 Interaction Flows

*(Ensure flows reference partition boundaries and auth redirects.)*

## 9 Visual & Style-Theme Guidelines ⚠️

* State the locked-in **STYLE\_ID** and its source (Figma file / Storybook build URL).
* List core token namespaces (e.g., `color.*`, `spacing.*`, `radius.*`).
* Document *tenant-override rules* (allowed token overrides or custom CSS-vars).
* Include **motion guidelines** consistent with WCAG 2.2 reduced-motion settings.

## 10 Performance & Offline Behaviour

*(Add partition-aware budgets – e.g., public pages ≤ 150 kB first-load, tenant console ≤ 300 kB after code-split.)*

## 11 Security Requirements

*(Reinforce multi-tenant isolation, row-level security, and SSRF / BFF patterns.)*

## 12 Component Library Integration

*(Highlight any component variants restricted to certain partitions.)*

## 13 Form Specifications, 14 Open Issues / Questions

*(Unchanged, but include permission & role clarifications as needed.)*

---

## QUALITY GATES

* **Partition Coverage**: every view must declare `Partition` & `Auth Level`.
* **Permission Declarations**: no page or component without explicit `Required Permissions`.
* **Theme Consistency**: must reference `STYLE_ID` tokens – no hard-coded colours!
* **Traceability**: maintain `FRD-X`, `PRD-X`, `API-X` links throughout.
* **Multi-Tenancy Compliance**: no cross-tenant data leakage in examples, state RS256 JWT audience rules.
* **Accessibility, Performance, Security**: all sections must meet base thresholds.

---

## CHAIN-OF-THOUGHT / WORK STEPS

1. **CRITICAL: Parse ALL requirements from the provided FRD document** - Do NOT use template examples. Extract EVERY requirement ID (e.g., REQ-FUNC-001, REQ-FUNC-020, etc.) and map each to appropriate UI views.
2. **Identify ALL functional areas** from the requirements including but not limited to: authentication, dashboards, customer management, payment processing, load management, carrier management, CRM functionality, broker roles, pipeline management, kanban boards, etc.
3. Group views by partition, assign routes & roles based on ACTUAL requirements.
4. Create IA / navigation skeleton with guards.
5. Lock STYLE\_ID, pull design tokens & atom/organism molecules.
6. Flesh out per-view specs for EVERY functional area found in requirements, interaction patterns, error states.
7. Map API calls & state slices; add caching & performance notes.
8. Write role-permission matrix including ALL roles mentioned in requirements (e.g., broker, admin, user, etc.); validate every spec uses it.
9. Add localisation hooks, multi-theme notes, analytics events.
10. **VERIFY: Ensure ALL requirements from FRD are covered** - No requirement should be missing from the UI/UX specification.
11. Compile doc, run internal completeness checklist (sections, word counts).
12. Generate **clarification questions** as YAML records (`UX-QUESTION-###`).

---

## OUTPUT

You have two output strategies—choose based on project size:

1. **Monolithic Document**

   * Suitable for smaller applications or initial scoping phases.
   * Produces a single `UIUX_SPEC.md` file following the full structure above.

2. **Modular Documents** ⚠️ *recommended for large-scale apps*

   * **Phase 1: Partition-Level Breakout**
     • Generate one document for **Tenant pages** (all views under `/app/*`)
     • Generate one document for **Admin pages** (all views under `/admin/*`)
   * **Phase 2: Feature-Level Modules**
     • For each major feature (e.g., Authentication, Dashboard, Reporting), create a dedicated module `UIUX-[Feature].md` containing its Per-View Specs, Interaction Flows, and Data Map.
   * **Phase 3: Master Index Document**
     • Create `UIUX-Index.md` listing all partition and feature modules, their scopes, and inter-document dependencies for easy navigation and traceability.

### Master Index Front-matter Example

```yaml
id: UIUX_INDEX
version: 1.0
style_id: [SELECTED STYLE_ID]
partitions:
  - tenant-pages
  - admin-pages
modules:
  - partition: tenant-pages
    file: UIUX-Tenant.md
    title: Tenant Workspace Overview
  - partition: admin-pages
    file: UIUX-Admin.md
    title: Administration Console Overview
  - partition: feature
    file: UIUX-Authentication.md
    title: Authentication & Onboarding
  - partition: feature
    file: UIUX-Dashboard.md
    title: Tenant Dashboard
  - partition: feature
    file: UIUX-Reporting.md
    title: Reporting Suite
```

Each module begins with its own front-matter:

```yaml
id: UIUX-Authentication
derivedFrom:
  - FRD-1.0
authors: [UX-Lead]
moduleScope: authentication
parentIndex: UIUX_INDEX
```

Choose **Modular Documents** for large applications to:

* Keep file sizes manageable
* Enable parallel editing by different teams
* Minimise merge conflicts

### BEGIN SPEC GENERATION NOW

> **Note:** The prompt template concludes here. From this point onward, your system or LLM should *generate the actual UI/UX specification document* based on the structure and guidelines defined above. You do **not** need to repeat the template — simply start populating each section in the output document with the project-specific details.
