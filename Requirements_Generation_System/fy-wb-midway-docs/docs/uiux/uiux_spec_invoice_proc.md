# Invoice Processing Interface Design

This document defines the invoice processing view specifications following the UXDMD format.

## View Catalogue

| View-ID | Title | Route | Upstream FRD | Primary API Endpoint(s) | User Roles |
|---------|-------|-------|--------------|-------------------------|------------|
| `view-invoice-list` | Invoice List | `/invoices` | FRD-3.3.1 | `GET /invoices` | admin, finance |
| `view-invoice-detail` | Invoice Detail | `/invoices/:id` | FRD-3.3.1 | `GET /invoices/{id}` | admin, finance |
| `view-invoice-generate` | Invoice Generation | `/invoices/generate` | FRD-3.3.1 | `POST /invoices` | admin, finance |

## Data Map

| Data Key | API Contract | Store Slice | Caching TTL | Loaded By (View-IDs) | Security |
|----------|--------------|-------------|-------------|---------------------|----------|
| `invoices` | `GET /invoices` | `state.invoices.list` | 60s | invoice-list | auth required |
| `invoice` | `GET /invoices/{id}` | `state.invoices.byId[id]` | 30s | invoice-detail | auth required |

## Per-View Specification

### view-invoice-generate (UXDMD-6)

| Section | Detail |
|---------|--------|
| **Purpose** | Automated invoice generation from completed loads |
| **Layout** | Multi-step wizard with preview and confirmation |
| **Displayed Fields** | Load Details • Line Items • Tax Calculations • Total Amount |
| **Primary Actions** | Generate Invoice, Save Draft, Send to Customer |
| **Secondary Actions** | Apply discounts, add custom line items |
| **State Behavior** | Auto-calculation, preview updates, generation progress |
| **API Mapping** | `POST /invoices` (201/400/500) |
| **Error UX** | Validation errors with field highlighting |
| **Security Notes** | Financial data access controls, audit logging |
| **Analytics** | Track `invoice.generated`, `invoice.sent` events |
| **Accessibility** | Form progression announcements, calculation summaries |
| **Design Tokens** | `--surface-elevated-3`, `--space-xl` |
| **Traceability Links** | FRD-3.3.1 • API-INVOICES-1 • NFRD-AUDIT-1 |

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Load Management](./uiux_spec_load_mgt.md)
- [Carrier Management →](./uiux_spec_carrier_mgt.md)