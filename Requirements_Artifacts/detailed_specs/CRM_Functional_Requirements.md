# CRM Functional Requirements (Pipedrive-Inspired)

## Source
Based on Pipedrive analysis and requirements provided by user.
Reference: https://www.pipedrive.com/

## Functional Requirements

| ID    | Title                  | Description                                                                                                | Broker View             | Manager View              | Priority |
| ----- | ---------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------- | -------- |
| FR-01 | **Pipeline Board**     | Kanban board with min. 5 configurable stages; drag-drop cards; inline edit of deal value & expected close. | ✓ view & edit own deals | ✓ view all; stage filters | P0       |
| FR-02 | **Deal Card**          | Shows: title, org/contact, value, aging badge, next activity. Clicking opens side panel with full details. | ✓                       | ✓                         | P0       |
| FR-03 | **Lead Inbox**         | Separate list view for un-qualified leads with bulk "Convert to Deal" action.                              | ✓                       | optional bulk ops         | P1       |
| FR-04 | **Activity Scheduler** | Log calls, emails, tasks; calendar sync (GCal). Overdue activities badge on cards.                         | ✓                       | team-wide calendar        | P0       |
| FR-05 | **Basic Automation**   | Rule builder: *IF* deal enters stage X *THEN* (a) assign task, (b) send templated email, (c) fire webhook. | limited to own deals    | create/edit all rules     | P1       |
| FR-06 | **AI Deal Score**      | Lightweight ML model (or rules-based starter) assigns 0-100 probability; score visible on card.            | ✓ filter by score       | ✓ pipeline health chart   | P2       |
| FR-07 | **AI Email Helper**    | GPT-powered "Draft Reply" & "Thread Summary" inside email panel.                                           | ✓                       | —                         | P2       |
| FR-08 | **Email Integration**  | OAuth Gmail sync; send, receive, track opens; templating & merge tags.                                     | ✓                       | team template library     | P1       |
| FR-09 | **SMS Integration**    | Twilio connect; one-to-one SMS from deal/contact & stage-based SMS workflow.                               | ✓                       | configure sender IDs      | P2       |
| FR-10 | **Insights Dashboard** | Charts: funnel conversion, time-in-stage, forecast (sum(value × probability)). Export CSV/JSON.            | —                       | ✓                         | P1       |

## Stage Configuration

### Default Pipeline Stages
1. **Qualified** - Initial qualified leads
2. **Contact Made** - First contact established  
3. **Demo Scheduled** - Product demonstration scheduled
4. **Negotiation** - Terms and pricing discussion
5. **Won** - Deal closed successfully
6. **Lost** - Deal closed unsuccessfully

### Stage Customization Requirements
- Minimum 3 stages, maximum 10 stages
- Custom stage names and colors
- Stage-specific automation rules
- Stage progression tracking and analytics

## Deal Card Specifications

### Required Fields
- Deal title (editable inline)
- Organization/Contact name
- Deal value (currency, editable inline)
- Expected close date (date picker)
- Deal stage (dropdown)
- Next activity (calendar icon + text)
- AI score (0-100, color-coded badge)

### Optional Fields
- Deal source (dropdown)
- Assigned broker (user selector)
- Tags (multi-select)
- Custom fields (configurable)

### Visual Indicators
- Aging badge (days in current stage)
- Overdue activity indicator (red badge)
- High-value deal indicator (gold star)
- Hot lead indicator (flame icon)

## API Requirements

### Core Endpoints
- `GET /api/crm/pipeline` - Get deals by stage
- `POST /api/crm/deals` - Create new deal
- `PUT /api/crm/deals/{id}` - Update deal
- `DELETE /api/crm/deals/{id}` - Delete deal
- `POST /api/crm/deals/{id}/move` - Move deal between stages
- `GET /api/crm/leads` - Get leads inbox
- `POST /api/crm/leads/{id}/convert` - Convert lead to deal
- `GET /api/crm/activities` - Get activities
- `POST /api/crm/activities` - Create activity
- `GET /api/crm/insights` - Get dashboard metrics

### Real-time Updates
- WebSocket support for live pipeline updates
- Optimistic UI updates for drag-and-drop
- Conflict resolution for concurrent edits

## Performance Requirements
- Pipeline board load time: <500ms for 100 deals
- Drag-and-drop response time: <100ms
- Real-time updates: <200ms latency
- Search results: <300ms for 1000+ deals

## Security Requirements
- Role-based access control (Broker vs Manager)
- Tenant isolation (multi-tenant SaaS)
- Data encryption at rest and in transit
- Audit logging for all CRM actions