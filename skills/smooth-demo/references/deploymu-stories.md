# DeployMu Demo Stories

## Sales Demo Request

Objective:

Show how a sales user creates or reviews a demo request, then moves toward approval and scheduling.

Useful routes:

- `/sales-demo/dashboard`
- `/sales-demo/requests`
- `/sales-demo/approvals`
- `/sales-demo/scheduler`
- `/sales-demo/vehicles`

Suggested shot list:

| Time | Shot | Action | Visible result |
|------|------|--------|----------------|
| 0-6s | Command center | Open `/sales-demo/dashboard` | Calendar, map, activity are visible |
| 6-18s | Request context | Open an existing request or create one from a date | Account, hospital, dates, unit, attachments visible |
| 18-30s | Approval | Move to approvals or show request status | Approval lanes/details are visible |
| 30-45s | Scheduling | Open scheduler and assign staff/logistics | Demo card shows assigned staff/vehicle |

Use this story when landing-page visitors choose "Sales demo".

## Planning Demo

Objective:

Show how service planning combines scheduler capacity, warranty/PMS forecast, and backlog triage.

Useful routes:

- `/service-scheduler`
- `/service-items`
- `/service-backlog`
- `/service-dashboard`

Suggested shot list:

| Time | Shot | Action | Visible result |
|------|------|--------|----------------|
| 0-8s | Scheduler | Open `/service-scheduler` | Monthly plan and engineer grid are visible |
| 8-20s | Warranty forecast | Open service item warranty/calendar view | Due months and forecasted work are visible |
| 20-34s | Backlog | Open `/service-backlog` and filter/group | Overdue/unassigned work by location is visible |
| 34-50s | Outcome | Return to scheduler or dashboard | Planned workload/utilization is visible |

Use this story when landing-page visitors choose "Planning demo".

## Seed And Reset Notes

- Prefer demo orgs that are already seeded with medical data.
- If a flow creates records, either record against disposable seeded data or reset with the repo seed command after capture.
- Do not record personal browser profile data, tokens, Convex dashboard contents, or unrelated tabs.
