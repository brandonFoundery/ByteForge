# Load Management Interface Design

This document defines the load management view specifications following the UXDMD format.

## View Catalogue

| View-ID | Title | Route | Upstream FRD | Primary API Endpoint(s) | User Roles |
|---------|-------|-------|--------------|-------------------------|------------|
| `view-load-list` | Load List | `/loads` | FRD-3.2.1 | `GET /loads` | admin, operations |
| `view-load-book` | Load Booking | `/loads/book` | FRD-3.2.1 | `POST /loads` | admin, operations |
| `view-load-track` | Load Tracking | `/loads/:id/track` | FRD-3.2.2 | `GET /loads/{id}/track` | admin, operations, customer |

## Data Map

| Data Key | API Contract | Store Slice | Caching TTL | Loaded By (View-IDs) | Security |
|----------|--------------|-------------|-------------|---------------------|----------|
| `loads` | `GET /loads` | `state.loads.list` | 60s | load-list | auth required |
| `tracking` | `GET /loads/{id}/track` | `state.loads.tracking[id]` | 5s | load-track | auth required |

## Per-View Specification

### view-load-track (UXDMD-5)

| Section | Detail |
|---------|--------|
| **Purpose** | Real-time load tracking with GPS location and milestone updates |
| **Layout** | Map view with timeline sidebar and status indicators |
| **Displayed Fields** | Current Location • Status • ETA • Milestones • Driver Info |
| **Primary Actions** | Refresh Location, Contact Driver, Update Status |
| **Secondary Actions** | Export tracking report, share tracking link |
| **State Behavior** | Auto-refresh every 30s, offline indicator |
| **API Mapping** | `GET /loads/{id}/track` (200/404/500) |
| **Error UX** | Connection lost indicator, manual refresh option |
| **Security Notes** | Load access permissions, customer data filtering |
| **Analytics** | Track `load.tracking.viewed`, `location.updated` events |
| **Accessibility** | Map alternative text, status announcements |
| **Design Tokens** | `--color-primary`, `--space-lg` |
| **Traceability Links** | FRD-3.2.2 • API-LOADS-2 • NFRD-PERF-2 |

## Navigation

- [← Back to Master Document](./uiux_spec.md)
- [← Payment Processing](./uiux_spec_payment_proc.md)
- [Invoice Processing →](./uiux_spec_invoice_proc.md)