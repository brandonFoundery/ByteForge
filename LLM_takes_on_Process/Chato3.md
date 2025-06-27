Great. I’ll define a canonical structure and Markdown-based prompt for each key requirements document in your stack, ensuring they support full traceability with standardized IDs and interlinked references.

I’ll also define optional but useful additions like onboarding docs or analytics specs, if they provide meaningful value to the requirements pipeline. All prompts will include both inline YAML metadata and compatibility with a centralized Traceability Matrix (RTM).

I’ll get started and let you know once the structured documentation and prompt library is ready.


# Requirements Document Prompt Library

This library provides standardized Markdown templates and LLM prompt guidelines for core requirements documents in a web application development stack. Each document template includes a clear purpose, defined inputs/outputs, intended audience, and a canonical structure with example *inline* YAML for key elements (fields like `id`, `title`, `description`, `verif_method`, `source`, `status`). The documents reference their upstream and downstream counterparts by consistent IDs (e.g., **PRD-1**, **FRD-1.1**, **TRD-1**, **TEST-1.1.1**) to ensure end-to-end traceability. Using unique IDs for each requirement makes it easy to trace across documents, and a Requirements Traceability Matrix (RTM) can map requirements to design and test artifacts. The following sections describe each core document along with an LLM prompt template for generating it.

## Product Requirements Document (PRD)

* **Purpose:** Defines **what the product should do** from the user's perspective, and everything that must be included for the product release to be considered complete. It captures high-level **business and user needs** and the key product features (functional requirements) along with essential **non-functional needs** (e.g. reliability, security, scalability) to meet those goals.
* **Inputs:** Business objectives, market or customer needs, stakeholder interviews, and any **Vision/Business Requirements** documentation. The PRD logically frames the problems to solve and high-level requirements in relation to customer needs (including any non-negotiable requirements or constraints).
* **Outputs:** A clear set of **product features and requirements** that define the scope of the product. These serve as a foundation for downstream documents (the Functional and Non-functional requirements specs, design, and testing). The PRD also often defines success metrics or acceptance criteria for the product.
* **Intended Audience:** Product managers and owners (who typically author it), stakeholders (for approval), and the development team leads (to understand high-level scope and priorities).

**Upstream/Downstream Traceability:** The PRD is generally the top-level requirements document (upstream inputs are business goals or a Market Requirements Document if available). Each PRD requirement is uniquely identified (e.g., **PRD-1, PRD-2, ...**) so that downstream documents can reference them. The **Functional Requirements Document (FRD)** will break down these high-level requirements; for example, PRD-1 might spawn FRD-1.1, FRD-1.2, etc. “Source” references for PRD items might include stakeholder names or strategy documents (since PRD has no formal upstream doc), while **downstream references** are the corresponding FRD IDs (captured in the FRD’s `source` field).

**Structure:** A typical PRD contains the following sections:

* **Introduction & Product Overview:** Context about the product vision, target users, and objectives. This includes the problem statement and how the product will solve it, aligning with business goals.
* **Scope and Objectives:** Definition of what’s in scope for this product/release (key features) and what’s out of scope. Also list assumptions, constraints, and success criteria.
* **User Personas/Use Cases:** *(Optional)* High-level user scenarios or personas to ground the requirements in real usage contexts.
* **High-Level Requirements:** A bullet list or subsection for each major product requirement (feature). Each requirement is documented as a **YAML block** with the fields below, enabling structured traceability. For example:

  ```yaml
  id: PRD-1
  title: "User Account Creation"
  description: "The product shall provide a way for new users to register an account using email or social login."
  verif_method: "Stakeholder acceptance demo"
  source: "Stakeholder interviews"  # origin of this requirement
  status: "Approved"
  ```

  *(In the above, `id` is the unique requirement ID, `verif_method` indicates how the fulfillment will be verified (e.g., via a demo or UAT), `source` notes where the requirement came from, and `status` shows its approval state.)* Each PRD item may encompass a broad feature; later documents will refine these.
* **Non-Functional Requirements:** If not handled separately, list key non-functional needs here (performance, security, compliance, etc. relevant to the product). These can also be captured as requirements with IDs (e.g., **PRD-NFR-1**) or included in the above list, and will trace to design and test considerations.
* **Dependencies and Constraints:** Any external factors, third-party components, or constraints (e.g., regulatory requirements, platform limitations) that impact the product.
* **Appendices/Glossary:** *(Optional)* Definitions of terms or acronyms used.

**LLM Prompt Template (PRD):** Use the following prompt to guide an LLM in generating a structured PRD. This prompt assumes you have background information on the product (features, goals, etc.) to provide the model:

```text
You are an expert product manager drafting a **Product Requirements Document (PRD)** for a new web application project called "[PROJECT NAME]". The PRD should be written in **Markdown** and include YAML-formatted requirement entries for each high-level requirement.

Include the following in the PRD:
- **Introduction**: Provide the product vision, target users, and key objectives.
- **Scope & Objectives**: Outline what's in scope (major features) and out of scope. List any assumptions or constraints.
- **High-Level Requirements**: For each major feature or need, provide a YAML block with fields: 
  `id` (PRD-#), `title`, `description` (what the product must do to fulfill the user need), `verif_method` (how you will verify this requirement, e.g. "User acceptance test" or "Demo"), `source` (origin, e.g. stakeholder or business goal), and `status` (e.g. Draft or Approved). Ensure each requirement is succinct but clear.
- **Non-Functional Requirements**: List critical NFRs (e.g. performance, security), also in YAML format with unique IDs (PRD-NFR-# or include in the main sequence).
- **Dependencies/Constraints**: Mention any external dependencies or constraints affecting these requirements.

Make sure the **IDs are consistent** (use "PRD-1", "PRD-2", etc.) and the content is **clear and concise**. The PRD should read as a high-level guide for stakeholders and the dev team, and each requirement should trace forward to more detailed specifications in later documents.
```

## Functional Requirements Document (FRD)

* **Purpose:** Translates the high-level product requirements from the PRD into **detailed functional specifications** that describe how the system will behave to fulfill those requirements. The FRD focuses on the functionality from a user’s perspective (what the user will observe the system doing) without detailing internal implementation. Each functional requirement corresponds to one or more PRD items.
* **Inputs:** The approved PRD (each PRD feature will be expanded), along with any **user stories, use case scenarios, or UI/UX input** that elaborate user interactions. Business rules and domain details are also inputs for fleshing out functional behavior.
* **Outputs:** A comprehensive set of **functional requirements** ready for design and development. These include detailed descriptions of system behaviors, covering all user interactions and system responses. The FRD may also produce supporting artifacts like use case diagrams or wireframes for clarity. This document guides developers and testers on exactly what to build and verify.
* **Intended Audience:** Business analysts or system analysts (often the authors), the development team, QA engineers, UX designers, and project stakeholders for review. It ensures all team members have a shared understanding of each function.

**Upstream/Downstream Traceability:** Every functional requirement in the FRD is traced **back to a PRD requirement**. This is captured by using a hierarchical ID or a reference field. For example, requirements derived from **PRD-1** might be labeled **FRD-1.1, FRD-1.2, ...** (where the prefix before the dot links to the PRD parent). In the YAML for each FRD item, the `source` field should list the corresponding PRD ID (or IDs) it satisfies. Downstream, the FRD’s requirements will be referenced by the technical design (TRD) and by test cases. (For example, a test case document might refer to **FRD-1.1** to show that the functionality is being verified.)

**Structure:** A typical FRD includes:

* **Introduction:** Brief overview of the document’s purpose and scope. Reference the PRD by ID/version and state that this FRD refines those high-level requirements. Include any background or system context needed (e.g. an overview of how the system works).
* **Overall Description:** *(Optional)* If needed, an outline of user needs or system context, and definitions of user roles or states. (This can also include any high-level **use case diagram or user flow** to contextualize the requirements.)
* **Functional Requirements:** A detailed list of each system function or feature broken down into granular requirements. It’s often structured by feature area or module:

  * For each PRD feature, create a subsection (or use a grouping) and list the specific requirements as YAML blocks. Each block should include:

    ```yaml
    id: FRD-1.1   # Derived from PRD-1 in this example
    title: "User provides email and password for registration"
    description: "The system shall present a registration form to the user and allow input of email, password, and username. Upon submission, it shall create a new user account."
    verif_method: "Functional test (form submission creates account)"
    source: "PRD-1"
    status: "Draft"
    ```

    *In this example, `FRD-1.1` corresponds to the first detailed requirement under PRD-1. The `source: "PRD-1"` indicates traceability to its parent product requirement.* Continue numbering (FRD-1.2, FRD-1.3, etc.) until PRD-1's aspects are covered, then proceed to FRD-2.x for PRD-2, and so on. If a functional requirement relates to multiple PRDs, list all in `source`. Each description should precisely state the behavior or criteria (including form field validations, system responses, etc.).
  * **User Interface details:** Include **wireframes or mockups** inline or as references for key screens, if applicable. FRDs often include UI/UX details to illustrate the intended behavior. For example, attach a screenshot or link for the registration form in the above requirement.
  * **Error handling and Alternate flows:** For each functional area, enumerate how the system should handle exceptions or alternate scenarios (e.g., "If the email is already registered, the system shall display an error message"). These can be written as additional requirements or sub-requirements (e.g., FRD-1.1a, FRD-1.1b) or simply described in the text under the main requirement.
* **Non-Functional Requirements:** *(If not a separate NFR document)* You can include a section listing performance, security, or usability requirements that apply to the functionality (e.g., "The registration form shall respond within 2 seconds (PRD-NFR-2)"). These may cross-reference an NFR spec or be listed with their own IDs.
* **Assumptions and Dependencies:** Note any assumptions made (e.g., "email service is available for verification emails") or dependencies on other systems or modules for these requirements.
* **Appendices:** *(Optional)* Additional diagrams, data dictionaries, or pseudo-code for complex logic, if it helps clarify the requirements.

**LLM Prompt Template (FRD):** Use this prompt to generate a Functional Requirements Document. Before using it, gather the PRD and any user stories or info about the features:

```text
You are a senior business analyst creating a **Functional Requirements Document (FRD)** for the project "[PROJECT NAME]". I will provide you the high-level requirements (from the PRD) and you will elaborate them into detailed functional requirements.

The FRD should be structured in **Markdown** and include:
- **Introduction**: State the purpose of the FRD and reference the PRD (e.g., "This document refines the Product Requirements (see PRD v1.0)...").
- **Functional Requirements**: For each high-level requirement from the PRD, create a subsection or list of detailed requirements. Use YAML-formatted blocks for each requirement with the fields:
  `id` (FRD-X.Y format, where X links to the PRD requirement number, Y is a sequence), `title`, `description` (detailed behavior the system must implement), `verif_method` (e.g. "Functional test", "Demo", etc.), `source` (the PRD ID it derives from), and `status`.
  - Ensure the `description` covers all necessary details: inputs, outputs, user interactions, and system responses for that function.
  - Include alternate flows or error conditions as separate requirements or clearly within the description.
- If relevant, integrate **UI/UX details** or refer to wireframes for clarity.
- **Assumptions/Dependencies**: List any assumptions or dependencies for these requirements.

Maintain **traceability** by correctly referencing PRD IDs in each `source` field. The writing should be clear and unambiguous, suitable for developers and testers to understand exactly what to build. Provide the output in Markdown format.
```

## Non-Functional Requirements (NFR) Specification

* **Purpose:** Captures the **quality attributes and constraints** of the system – how well the system performs certain functions, rather than what functions it performs. This includes requirements for performance, scalability, security, usability, reliability, maintainability, compliance, etc. These **quality requirements** define the expected level of service and user experience.
* **Inputs:** The PRD (which might outline some high-level NFR expectations or success metrics), regulatory or compliance standards, stakeholder expectations for system quality (e.g., uptime or response time targets), and technical constraints. Sometimes, specific NFRs come from industry standards or client SLAs.
* **Outputs:** A list of clear, testable **non-functional requirements** that the system design must accommodate and the testing must verify (e.g., *"System shall handle 10,000 concurrent users"* or *"99.9% availability is required"*). These inform the architecture and capacity planning and will be used to create performance tests, security tests, etc.
* **Intended Audience:** System architects and developers (to design the system to meet these criteria), QA/testing teams (to validate these criteria), and product/project managers to ensure the product meets business expectations (like performance and compliance).

**Traceability:** Each NFR can be treated as a requirement with an ID (e.g., **NFR-1, NFR-2, ...**). Upstream, some NFRs might trace to higher-level goals (for instance, a business goal of "fast user experience" translates to a performance NFR). In practice, we list the source as either a PRD item (if a PRD objective implies an NFR) or a stakeholder request. Downstream, NFRs trace to the **Technical Design (TRD)** decisions and to specific **test cases** (e.g., load testing scripts) that verify them.

**Structure:** The NFR document can be a standalone list or integrated into the PRD/FRD. As a separate document, a good structure is:

* **Introduction:** Purpose of the NFR spec, scope (which projects or modules it applies to), and context. Mention any standards or regulatory frameworks considered.
* **Categories of NFRs:** Organize requirements by category for clarity (Performance, Security, Usability, etc.). For each category, provide a brief description of its importance.
* **Non-Functional Requirements List:** Each NFR as a YAML item. For example:

  ```yaml
  id: NFR-1
  title: "Performance - Concurrent Users"
  description: "The application shall support at least 10,000 concurrent users with acceptable response time (<2 seconds for 95% of requests)."
  verif_method: "Load Test (simulate 10k users and measure response times)"
  source: "PRD-Objective-3"   # referencing a high-level performance goal in PRD, if exists
  status: "Proposed"
  ```

  Continue listing NFRs (NFR-2, NFR-3, ...) for other categories (throughput, security, etc.). Each description must be quantitative or verifiable where possible (e.g., specific performance metrics, security standards to comply with, usability survey targets).
* **Assumptions/Constraints:** Note any assumptions (e.g., hardware environment used for performance tests) or constraints (like compliance mandates) relevant to these NFRs.
* **Prioritization:** *(Optional)* Indicate which NFRs are must-have vs. nice-to-have, or their criticality (sometimes done via a “priority” field or in the description).

**LLM Prompt Template (NFR):** Use this when you need to generate a Non-Functional Requirements document:

```text
You are a system architect drafting a **Non-Functional Requirements (NFR) specification** for the project "[PROJECT NAME]". The goal is to list all quality and performance requirements the system must meet. Produce the document in **Markdown** with a structured list of NFRs.

Include:
- **Introduction**: Explain the purpose of NFRs and list the categories (performance, security, etc.) that will be covered.
- **NFR List**: Organize by category. Under each category, list the specific requirements as YAML blocks with fields:
  `id` (NFR-#), `title` (short name of the requirement), `description` (specific measurable criterion or condition the system must meet), `verif_method` (how to verify it, e.g. "Load testing", "Security audit"), `source` (if applicable, reference any origin like a PRD objective or compliance document), `status`.
  - Make sure each NFR is concrete (e.g. exact numbers for performance, named security standards, etc.) so they can be tested or validated.
- **Assumptions/Constraints**: Mention any context that affects these requirements (e.g. "Tests will be done on staging environment hardware X", or "Must comply with GDPR regulations" as a constraint).

Maintain consistency in formatting and IDs (use "NFR-1", "NFR-2", etc.). The tone should be clear and exact, since these requirements will guide architecture and testing.
```

## Technical Requirements & Design Document (TRD)

* **Purpose:** Describes the **system architecture and technical solution** that will fulfill the FRD and NFRs. The Technical Requirements Document (TRD) — also known as a Technical Design Specification — bridges requirements to implementation by detailing the software/hardware platform requirements, system components, interfaces, and design decisions. It ensures that the product is technically feasible and outlines how each functional requirement will be implemented.
* **Inputs:** The FRD (for functional needs), the NFR specification (for performance, security, and other constraints), and any corporate IT standards or technical guidelines. Design brainstorming outputs, architecture diagrams, and technology stack decisions also feed into this document.
* **Outputs:** A complete **technical blueprint** for developers. This includes the chosen architecture (e.g., client-server, microservices), component designs, data models (e.g., database schema), external interface specifications (APIs), and any hardware or platform requirements. It often enumerates technical requirements such as programming languages, frameworks, deployment environment, and third-party services, and addresses how NFRs will be met (e.g., caching for performance, clustering for scalability). This document guides the implementation phase and can be used for technical reviews.
* **Intended Audience:** System architects (often the authors), senior developers, DevOps engineers, and any stakeholder interested in the technical approach (including security/compliance officers for certain sections). It’s a reference for the development team during implementation.

**Traceability:** The TRD is traced **back to the FRD (and indirectly the PRD/NFRs)**. Each major design element or technical requirement should reference the functional requirement(s) it addresses. In practice, this can be done by listing FRD IDs in the `source` field of technical requirement items or by a traceability table. For example, a technical requirement "Implement database with encryption at rest" might have `source: FRD-3.4, NFR-5` if it supports a certain functional requirement and a security NFR. Using a consistent ID scheme (e.g., **TRD-1, TRD-2** for each technical requirement/decision) will allow mapping back to FRD IDs. Downstream, the TRD provides a basis for **code development tasks** and is referenced during testing (e.g., performance tests refer to design choices, security tests refer to security requirements). It may also link forward to **implementation tickets** or modules in code (though those are outside this documentation set).

**Structure:** A robust TRD typically contains:

* **Introduction & System Overview:** High-level summary of the design, including an **architectural context diagram** if applicable. State key design goals and reference the FRD/NFR inputs (e.g., "This design is intended to satisfy the requirements of FRD v1.0 and the performance/security criteria outlined in NFR v1.0").
* **Architecture Description:** Describe the overall architecture (e.g., layered architecture, microservice layout, client/server distribution). Include diagrams (embedded or linked) to illustrate components and their interactions.
* **Technical Requirements and Design Decisions:** This is the core of the document. Break it down by system components or by cross-cutting concerns:

  * **Component 1 (e.g., Web Frontend):** Requirements/decisions for this component.

    * For each significant requirement or decision, provide a YAML block. Example:

      ```yaml
      id: TRD-1
      title: "Web Application Frontend using React"
      description: "The client-side will be a single-page application built with React. It will communicate with the backend via a REST API. Rationale: ensures a responsive UX and reusability of components."
      verif_method: "Code review & UI integration testing"
      source: "FRD-2.1"
      status: "Approved"
      ```

      *This example defines a design decision to use React for a frontend, which addresses FRD-2.1 (say, a requirement for a responsive UI). The `verif_method` might be by code implementation and review, or later integration tests to validate the tech choice works.* Continue listing technical requirements/decisions (TRD-2, TRD-3, ...) covering all aspects: backend frameworks, database choices, API design, etc., each with rationale and mapping to requirements.
    * Include any relevant **interface specifications** (e.g., API endpoint definitions, communication protocols) and link them to requirements (e.g., "API /register (implements FRD-1.1) returns 201 on success...").
  * **Component 2 (e.g., Database)**, **Component 3 (e.g., Authentication Service)**, etc.: For each major subsystem, detail the design (schema, algorithms, third-party services, etc.) similarly with YAML items and narrative explanations.
* **Mapping to Requirements:** Optionally, a subsection that tabulates how each FRD/NFR is addressed by the design. (E.g., "FRD-2.1 is fulfilled by TRD-1 (React SPA) and TRD-3 (REST API); NFR-5 (Security) is fulfilled by TRD-7 (Encryption at rest)").
* **Infrastructure & Environment:** Specify environment needs (hosting, servers, cloud services), deployment architecture (dev, staging, prod), and any DevOps requirements.
* **Assumptions and Risks:** Document any technical assumptions (e.g., using a certain library version) and risks or technical debt (e.g., "SMS service single vendor risk, with mitigation X").
* **Appendices:** Additional diagrams (data flow, ER diagrams for database), code samples or pseudo-code for critical algorithms, etc.

**LLM Prompt Template (TRD):** Use the following prompt to generate a Technical Requirements/Design document:

```text
You are a lead software architect writing a **Technical Requirements & Design Document (TRD)** for "[PROJECT NAME]". The design should satisfy all functional requirements and non-functional criteria.

Produce a **Markdown** document with:
- **Introduction & Overview**: Summarize the system architecture and reference the FRD and NFR documents.
- **Architecture**: Describe the overall architecture (e.g., include a description of components like frontend, backend, database, and how they interact).
- **Technical Requirements/Design Decisions**: For each major system component or decision, list the technical requirements or design choices. Use YAML blocks for each, with:
  `id` (TRD-#), `title` (the component or decision name), `description` (details of the design decision and rationale), `verif_method` (how we'll verify or validate this decision – e.g., code review, unit testing, etc.), `source` (reference the FRD and/or NFR IDs that this design satisfies), `status`.
  - Cover all relevant areas (technology stack selection, module design, data model, interfaces, security measures, performance measures).
  - Provide rationale for decisions (why this approach).
- **Requirement Mapping**: After listing design items, ensure every FRD and key NFR is addressed. You can provide a brief mapping or ensure the `source` fields above cover all of them.
- **Infrastructure & Deployment**: Note any requirements for infrastructure or deployment.
- **Assumptions/Risks**: List assumptions and potential risks in the technical approach.

Keep the writing clear and **solution-oriented**, as this will guide developers. Maintain traceability by citing the relevant requirement IDs in each design item. Ensure the IDs (TRD-1, TRD-2, ...) are unique and consistent.
```

## Test Plan and Cases Document (QA/UAT Plan)

* **Purpose:** Defines the **quality assurance strategy and test cases** to verify that all requirements are met. The Test Plan outlines how the product will be tested (approach, environments, responsibilities), and the test cases detail specific scenarios to validate each functional and non-functional requirement. This ensures that for every requirement from the FRD and NFR, there is at least one corresponding test, achieving full coverage.
* **Inputs:** The FRD and NFR documents (as they list what needs to be tested), possibly the PRD for high-level acceptance criteria, and the Technical Design for any special testing considerations (like need for performance testing tools or security testing). Also, any corporate QA standards or test templates.
* **Outputs:** A **Test Plan** section describing testing scope, types of testing (unit, integration, system, UAT), schedule, and responsibilities; plus a **set of test cases** (or scenarios) each mapped to specific requirements. The output could be a combined document or separate test case specifications. For traceability, an RTM is often included or separate, mapping each requirement ID to one or more test case IDs and recording test results. The document results in a clear understanding of how the product will be validated and a repository of test cases for execution.
* **Intended Audience:** QA engineers (authors and executors of tests), developers (to understand how their work will be verified), project managers, and possibly client representatives for User Acceptance Testing (UAT).

**Traceability:** Each test case is linked **back to requirements**. We assign each test a unique ID that reflects the requirement it validates (for example, **TEST-1.1.1** could be the first test for requirement FRD-1.1). In the test case description or as a field, the requirement ID is referenced. This way, one can create an RTM that shows, for every FRD/NFR, the associated test(s) and their status. Upstream references for the test cases are the FRD or NFR IDs (and ultimately PRD through those). Downstream, each test case yields a result (Pass/Fail) and possibly links to defect IDs if failed. The test plan should also ensure **all** PRD/FRD requirements have at least one test (forward traceability) and every test ties to a requirement (backward traceability), avoiding extraneous tests.

**Structure:** A combined Test Plan & Cases document can be structured as:

* **Test Plan Overview:** Outline the overall testing strategy:

  * **Testing Scope:** What will be tested (functional features, performance, security) and what is out of scope.
  * **Test Levels:** Unit testing, integration testing, system testing, UAT – and which teams handle which.
  * **Test Environment:** Description of test environments (DEV, QA, Staging) and any data setup needed.
  * **Roles and Responsibilities:** Who writes and executes tests, who verifies fixes, etc.
  * **Schedule/Milestones:** Key testing phases (e.g., "Sprint testing", "Regression testing period", "UAT dates").
  * **Entry/Exit Criteria:** Criteria for starting testing and for accepting that testing is complete.
  * **Traceability Approach:** State that each requirement is mapped to tests (and possibly include an RTM table in an appendix or embedded).
* **Test Cases:** A list of individual test cases or scenarios, typically grouped by feature or requirement area:

  * Organize by FRD section or feature. For each requirement (or group of related requirements), list one or more test cases. Each test case can be formatted with YAML front-matter for structured info. Example:

    ```yaml
    id: TEST-1.1.1
    title: "Signup with valid details"
    description: "Verify that a new user can successfully register with a unique email and valid password."
    requirement: "FRD-1.1"
    expected_result: "New account is created and confirmation email is sent."
    status: "Planned"
    ```

    *In this example, `TEST-1.1.1` is a test case ID indicating it's for FRD-1.1. The `requirement` field explicitly links to the requirement being tested. The `expected_result` describes the pass criteria.* Continue listing tests: e.g., **TEST-1.1.2** for "Signup with an already-used email (should get error)", etc., covering alternate scenarios. Then move to **TEST-1.2.x** for FRD-1.2, and so on.
  * Include test cases for **Non-Functional requirements** as well. For instance, if NFR-1 is about performance, you might have a test case like `TEST-NFR-1.1` for a load test scenario.
  * Each test case description should outline the test steps if necessary, or at least the condition being tested and the expected outcome. Additional fields can be added if desired (like `steps` or `priority`), but the above fields ensure traceability.
* **Traceability Matrix:** *(Optional section or Appendix)* A table or list that cross-references each requirement (PRD/FRD/NFR ID) to the test case IDs that validate it, and notes the test status or result. This is often derived from the above data and kept updated during test execution.
* **UAT Criteria:** *(If applicable)* Define which tests or scenarios will be repeated in User Acceptance Testing and any additional acceptance criteria from stakeholders.

**LLM Prompt Template (Test Plan & Cases):** Use this prompt to generate the test documentation:

```text
You are a QA lead creating a **Test Plan and Test Cases document** for "[PROJECT NAME]". Ensure the document is in **Markdown** and covers both the overall plan and the specific test cases, with a focus on traceability to requirements.

Include in the document:
- **Test Plan Overview**: Describe the testing strategy (scope, types of testing, environments, roles, schedule, etc. as needed for this project).
- **Test Cases**: For each functional requirement (and key non-functional requirements), list at least one test case. Use YAML blocks to structure each test case with fields:
  `id` (TEST-X.Y.Z format, mapping to the requirement ID), `title` (short description of test scenario), `description` (what the test will do), `requirement` (the FRD or NFR ID this test validates), `expected_result` (the outcome for the test to pass), `status` (e.g., Planned).
  - Cover normal cases and edge cases (including error conditions) for each requirement.
  - Ensure that every requirement from the FRD/NFR has at least one corresponding test case.
- If appropriate, add a **Traceability Matrix** section that shows requirement IDs vs. test IDs (or ensure the mapping is clear from each test case's `requirement` field).

The style should be clear and methodical, suitable for use by QA engineers and for review by the team. Each test case must directly tie back to a requirement to maintain full traceability.
```

## Onboarding Guide *(Optional)*

* **Purpose:** Provides a structured introduction for new team members (developers, testers, etc.) joining the project. It accelerates onboarding by explaining the project context, team practices, and environment setup. This guide ensures new contributors can quickly become productive by having all essential information in one place.
* **Inputs:** Existing project documentation (like the PRD for product context, TRD for architecture overview), internal team practices, development environment details, and any relevant links (repository, project management boards, CI/CD pipelines). Essentially, it's a distillation of "things you need to know on day 1."
* **Outputs:** A comprehensive **onboarding manual** or checklist. It typically covers project background, how to set up a development environment, coding standards, key contacts, and where to find further documentation. It may also include pointers to the requirements and design docs as references.
* **Intended Audience:** New developers, testers, or other team members who need to understand and integrate with the project. It can also be a reference for external collaborators or auditors to grasp project structure quickly.

**Traceability:** The onboarding guide is not a requirements document, so it doesn't contain requirement IDs or need traceability in the same way. However, it should reference the key documents in the project (e.g., "see PRD for overall product vision" or "the architecture is described in TRD section X"). In that sense, it serves as a navigation tool to the documentation library. There’s no upstream document feeding into the onboarding guide except the general project info, and no downstream except a fully onboarded team member.

**Structure:** A useful onboarding guide might include:

* **Project Overview and Goals:** A summary of the project’s purpose, vision, and current status. This orients the newcomer about what the team is building and why (often derived from the PRD’s intro).
* **Team Contacts:** Who is on the team (product manager, tech lead, QA lead, etc.) and their contact info. Could be a list or table.
* **Team Processes and Practices:** Development process (Agile/Scrum rituals, code review process, ticket workflow), communication channels (Slack, email), and any coding standards or guidelines adopted by the team.
* **Development Environment Setup:** Step-by-step instructions to get the project running on a new machine. This includes prerequisites (software, access keys), how to obtain source code (repo URLs, branch conventions), configuration steps, and how to run tests. Essentially, everything needed to set up a working dev/test environment.
* **Project Architecture Summary:** A high-level summary of the system architecture (perhaps a simplified version of what's in the TRD). This helps the newcomer understand how the pieces fit together. Diagrams or links to the TRD can be included.
* **Key Resources and Documentation:** Pointers to important documents (link to PRD, FRD, TRD, test plans), code repositories, CI/CD pipelines, issue tracker, etc. The onboarding guide often serves as an index to project-specific content, linking out to deeper information so the guide itself stays concise.
* **First Tasks / Training:** *(Optional)* A list of suggested first issues or tutorials to work through, to practice the setup and get familiar with the codebase.
* **FAQs/Troubleshooting:** Common setup problems and their solutions, or FAQs new team members often have.

**LLM Prompt Template (Onboarding Guide):** Use this prompt to generate a tailored onboarding guide:

```text
You are a tech lead preparing an **Onboarding Guide** for new team members joining the "[PROJECT NAME]" development team. The guide should be in **Markdown** and cover all essential information to get started.

Include sections for:
- **Overview and Goals**: Briefly describe the project's purpose, scope, and what the team is building (in simple terms, for context).
- **Team Contacts**: List key team members and their roles/contact info.
- **Team Processes**: Summarize how the team works (development methodology, meetings, code reviews, branch strategy, etc.).
- **Development Environment Setup**: Provide step-by-step instructions to set up the project on a new developer's machine (required software, environment variables, database seeding, how to run the application and tests).
- **Architecture Summary**: Outline the system architecture or components (so the newcomer knows the high-level design). Refer to the Technical Design doc if available for details.
- **Key Resources**: Bullet list important links (documentation like PRD/FRD, code repository link, issue tracker, continuous integration pipeline, etc.).
- **Troubleshooting/FAQs**: (if applicable) mention solutions to common setup issues or answer frequent questions.

The tone should be welcoming, clear, and concise. Assume the reader has general technical knowledge but is new to this project. Use bullet points or steps where appropriate (especially for setup).
```

## Analytics Tracking Requirements (Analytics Spec) *(Optional)*

* **Purpose:** Specifies **what data the application needs to collect** for analytics, monitoring, and decision-making. This document, sometimes called an Analytics Requirements Document or tracking plan, ensures that every important user action and system event is measured. By defining these requirements up front, the team can instrument the product to capture metrics that align with business goals (so that *“every launch can be measured”* and insights can be derived).
* **Inputs:** Product goals and KPIs (from the PRD or business stakeholders), marketing and growth requirements (e.g., funnel metrics), compliance requirements (privacy considerations), and the functional design (FRD) to identify where in the user flow events can be logged. Also input from analytics tools capabilities (e.g., what events can be tracked, any naming conventions).
* **Outputs:** A clear **analytics tracking plan** detailing each event or metric to track, including context and criteria. For example, it will output a list of events like "User Signed Up", "Item Purchased", each with definitions of when it triggers and what data is recorded. It also covers page view tracking, error logging, and any derived metrics needed. This spec guides developers in adding analytics instrumentation and serves as a contract for analysts to know what data will be available.
* **Intended Audience:** Product managers and data analysts (who define the metrics), developers (who implement the tracking), QA (who verify data is collected), and possibly compliance officers (to ensure privacy considerations are met).

**Traceability:** Analytics requirements trace **back to product/business requirements** – each metric or event should relate to a PRD objective or FRD feature. For instance, if PRD-4 is "Increase user engagement", an event like "Video Played" might trace to that objective to measure engagement. In the spec, we can use the `source` field to reference the relevant PRD/FRD that justifies the tracking. Downstream, these requirements trace to **implementation in code** (e.g., tagging plans) and to dashboards or reports that use the data (though those aren’t usually in the requirements docs). There isn't typically an “Analytics Test” document, but QA should verify that events fire correctly, possibly referencing these IDs.

**Structure:** An Analytics Requirements document can be structured as:

* **Introduction:** Goals of analytics for this product (e.g., *"understand user behavior in onboarding"* or *"track conversion funnel from signup to purchase"*). Mention the tools or platforms (e.g., Google Analytics, Mixpanel, etc.) if known, and any constraints (like GDPR compliance).
* **Key Metrics and KPIs:** List the high-level questions or KPIs the business wants to measure (e.g., *"Daily Active Users"*, *"Conversion Rate from trial to paid"*). This provides context for the events specified later.
* **Tracking Requirements (Event Specification):** A list of events or user interactions to track. Each can be listed with a structured format, for example:

  ```yaml
  id: AN-1
  title: "Signup Completed event"
  description: "Triggered when a user successfully completes the registration. Captures user_id, signup_method (email or social), and timestamp."
  verif_method: "Verify event in analytics dashboard and database logs"
  source: "FRD-1.1"
  status: "Planned"
  ```

  Here **AN-1** is an analytics event ID. The `source` indicates this event is tied to FRD-1.1 (the user registration functionality) and indirectly to PRD-1 (if PRD-1 was "User can register"). Continue enumerating events: page views (e.g., AN-2: "Home Page Viewed"), clicks or significant actions (AN-3: "Item Added to Cart"), errors (if tracking error rates), etc. For each, specify what data will be collected (could be included in description or a separate field listing parameters) and why it's needed (implicitly via source or an additional note).
* **Data Governance & Privacy:** Specify how user data is handled – e.g., "Do not log personal identifiable information (PII) in analytics" or mapping of our events to comply with privacy rules. Include if users can opt-out, etc.
* **Analytics Tools/Integration Notes:** *(Optional)* If using specific analytics platforms, note any technical requirements like event naming conventions, API keys, or integration steps. This can reference the TRD if the integration is part of the design.
* **Reporting & Dashboards:** *(Optional)* Describe how the data will be used, such as what dashboards or reports will be created. This gives context but might be beyond strict requirements; include if helpful for completeness.

**LLM Prompt Template (Analytics Spec):** To generate an analytics requirements document, use:

```text
You are a product analyst defining an **Analytics Tracking Requirements** document for "[PROJECT NAME]". The goal is to outline what events and metrics must be tracked to measure the product’s success. Provide the output in **Markdown**.

Include:
- **Introduction**: Explain the analytics goals for the project (what we want to learn or measure) and any tools or constraints (e.g., privacy laws).
- **Key Metrics**: List the main KPIs or questions (e.g., user engagement, conversion) that drive the tracking plan.
- **Events to Track**: For each important user action or system event, specify a tracking requirement. Use YAML blocks for each event with:
  `id` (AN-#), `title` (name of the event or metric), `description` (when it should be triggered and what data to capture), `verif_method` (how to verify the event is correctly tracked, e.g. "Check in analytics tool or logs"), `source` (reference to the requirement or goal that makes this event important, such as a PRD or FRD ID), `status`.
  - Cover events corresponding to each key feature (sign-ups, logins, feature usage) and any required performance or error tracking.
  - Ensure the description of each event is specific (include trigger conditions and data captured).
- **Privacy and Compliance**: Note any guidelines for handling the data (e.g., anonymize user IDs, respect user consent).
- **Usage of Data**: Optionally mention how this data will be used (dashboards, etc.) for clarity.

Make sure each event ties back to a product requirement or goal, ensuring we're only tracking things that matter. The tone should be clear and instructive, as this will guide developers implementing the analytics.
```

## Requirements Traceability Matrix (RTM) Summary

*(The RTM is typically a compiled artifact rather than a manually written doc, but we include it for completeness.)*

* **Purpose:** The **Requirements Traceability Matrix** is a structured summary that maps each requirement to its related artifacts (design elements, test cases, etc.), ensuring full coverage and traceability. It provides a one-stop view to verify that every requirement has been implemented and tested, and that no test exists without a linked requirement.
* **Format:** Often a table (in Markdown, CSV, or spreadsheet) where each row is a requirement and columns show the linked document references. For example: Requirement ID, Requirement Description, Source (upstream) ID, Design ID, Test Case ID(s), Status. This can be produced by extracting the information from the documents above (which is why consistent IDs and references are critical).
* **Upstream/Downstream:** The RTM consolidates all traceability links. Upstream, it might include a column for PRD source for each FRD, and downstream a column for test cases for each FRD/NFR. It ensures backward traceability (e.g., can trace from a test case to the original requirement) and forward traceability (from requirement to testing).
* **Maintenance:** Typically updated as requirements evolve and as tests are executed (adding test results).

**Using the Library for RTM:** Because each document uses a consistent ID scheme and references:

* We can parse the PRD, FRD, TRD, etc., and build a matrix. For example, PRD-1 is linked to FRD-1.1, 1.2, etc. Those in turn link to design items (TRD IDs) and test cases (TEST-1.1.x).
* The RTM can be generated by listing each PRD and nesting its FRDs, or by listing each FRD with columns for “Source PRD” and “Test case”. **Example (in Markdown table form):**

| **FRD ID** | **FRD Description**              | **Source (PRD)** | **Design Ref (TRD)** | **Test Cases**    | **Status**    |
| ---------- | -------------------------------- | ---------------- | -------------------- | ----------------- | ------------- |
| FRD-1.1    | User can register an account     | PRD-1            | TRD-1, TRD-3         | TEST-1.1.1, 1.1.2 | Implemented ✅ |
| FRD-1.2    | User receives confirmation email | PRD-1            | TRD-5                | TEST-1.2.1        | In QA 🔶      |

*(The above is an illustrative snippet: FRD-1.1 and FRD-1.2 both trace to PRD-1, have some TRD items fulfilling them, and corresponding test cases. Status indicates implementation/testing progress.)*

* **LLM Prompt Template:** While an RTM is often generated via tools or spreadsheets, you could ask an LLM to create one if provided with the content of the documents. For example:

```text
Using the PRD, FRD, and Test Case documents, compile a **Requirements Traceability Matrix** in Markdown. List each functional requirement (FRD) with its ID, description, upstream PRD ID, related design (TRD) IDs, and related test case IDs and status. Ensure all IDs link correctly. Summarize non-functional requirements similarly.
```

However, typically it's more reliable to produce the RTM by processing the structured YAML data from the docs.

---

By following this prompt library, teams can generate **consistent, traceable, production-grade requirements documentation** for any project. Each document is interlinked via a coherent ID system, supporting easy navigation and verification. This not only improves clarity for the current team but also lays a foundation for maintenance and audits, as all requirements and their implementations can be traced in one unified framework. Adhering to these templates helps ensure every project requirement is accounted for from conception through to testing and delivery, resulting in higher-quality software and smoother project execution.

**Sources:**

* Nicholas Rubright, *"9 Types Of Requirements Documents..."* – Definitions of PRD, FRD, TRD and their contents.
* Konstantin Hatvan, *Project Tracey* – Best practice of assigning unique IDs in Markdown to each requirement for traceability.
* Perforce, *"What is a Requirements Traceability Matrix?"* – Traceability matrix maps requirements to test cases and results.
* Piwik PRO, *"Web analytics requirements"* – Importance of including an analytics tracking plan in the project.
* Sarah's Newsletter, *"The Analytics Requirements Document"* – Every product launch should have measurable data to inform decisions.
* Microsoft Engineering Playbook, *"Onboarding Guide Template"* – Recommended contents of a team onboarding document (scope, processes, codebase, setup, etc.).
