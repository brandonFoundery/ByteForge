# Carrier Management Interface Design

This document defines the carrier management view specifications following the UXDMD format.

## View Catalogue

| View-ID | Title | Route | Upstream FRD | Primary API Endpoint(s) | User Roles |
|---------|-------|-------|--------------|-------------------------|------------|
| `view-carrier-register` | Carrier Registration | `/carriers/register` | FRD-3.4.1 | `POST /carrier/register` | public, admin |
| `view-carrier-portal` | Carrier Portal | `/carrier/portal` | FRD-3.4.2 | `GET /carrier/portal` | carrier, admin |

## Data Map

| Data Key | API Contract | Store Slice | Caching TTL | Loaded By (View-IDs) | Security |
|----------|--------------|-------------|-------------|---------------------|----------|
| `carrierPortal` | `GET /carrier/portal` | `state.carrier.portal` | 30s | carrier-portal | carrier auth |
| `registration` | `POST /carrier/register` | `state.carrier.registration` | 0s | carrier-register | public access |

## Per-View Specification

### view-carrier-portal (UXDMD-7)

| Section | Detail |
|---------|--------|
| **Purpose** | Self-service portal for carriers to manage loads and payments |
| **Layout** | Dashboard layout with widgets for key metrics and actions |
| **Displayed Fields** | Active Loads • Payment History • Performance Metrics • Notifications |
| **Primary Actions** | View Load Details, Update Status, Submit Documents |
| **Secondary Actions** | Download reports, contact support, update profile |
| **State Behavior** | Real-time updates, notification badges |
| **API Mapping** | `GET /carrier/portal` (200/401/500) |
| **Error UX** | Session timeout warnings, offline mode indicators |
| **Security Notes** | Carrier-specific data isolation, secure document upload |
| **Analytics** | Track `carrier.portal.viewed`, `load.status.updated` events |
| **Accessibility** | Dashboard navigation, status announcements |
| **Design Tokens** | `--surface-carrier`, `--space-md` |
| **Traceability Links** | FRD-3.4.2 • API-CARRIERS-2 • NFRD-SEC-3 |

## Security Requirements

| Topic | Requirement |
|-------|-------------|
| Data Isolation | Carriers only see their own data |
| Document Security | Encrypted file uploads with virus scanning |
| Session Management | Auto-logout after 30 minutes of inactivity |
| Access Control | Role-based permissions for portal features |

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Invoice Processing](./uiux_spec_invoice_proc.md)
- [Information Architecture →](./uiux_spec_architecture.md)