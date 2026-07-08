# Day 11 Discovery Notes – live.ideabytesiot.com/demolive

## Auth

- [x] Is login required?

Answer:
Yes. Authentication using a valid username and password is required before accessing the application dashboard.

- [x] If yes, what are the test credentials?

Answer:
Internal project credentials were provided by the organization. Credentials are not included in this document.

- [x] Is there a public demo mode?

Answer:
No. A public demo mode was not observed. Authentication is required to access the application.

- [x] Which routes are public?

Answer:
Only the login page appears to be publicly accessible. Dashboard modules such as Dashboard, Reports, Alerts, Devices, Alarms, and Users require authentication.

---

# DOM Structure

- [x] Page title / main heading

Answer:

**Remote Monitoring System**

- [x] Main sections/widgets visible

Answer:

### Navigation
- Dashboard
- Reports
- Alerts
- Devices
- Alarms
- Users

### Dashboard Widgets
- Total Devices
- Reporting Devices
- Good Status
- Warning Status
- Critical Status
- Not Reporting

### Dashboard Components
- Device Information Table
- Temperature
- Humidity
- Last Updated Timestamp
- Sort Toggle
- Search Bar
- Notification Icon
- User Profile Menu

### Reports Module
- Scheduled Reports
- On-Demand Reports
- New Report Button
- Search Reports
- Reports Table

### Alerts Module
- Live Alerts
- Location Filter
- Device Filter
- Sensor Filter
- Status Filter
- Period Filter
- Fetch Button
- Search Alerts

### Devices Module
- Assign Devices Button
- Device Table
- Search Devices

### Alarms Module
- Rules Dropdown
- Location Filter
- Search Rules
- Alarm Rules Table
- Edit Button
- Delete Button

### Users Module
- User Management
- Role Management
- Add User Button
- Search Users

---

- [x] Framework used

Answer:

**Angular 18.2.13**

Verification:

Chrome DevTools Console

```javascript
document.querySelector("[ng-version]")
```

Output

```html
<ib-iot-root ng-version="18.2.13"></ib-iot-root>
```

This confirms that the application is built using **Angular version 18.2.13**.

---

- [x] WebSocket connections?

Answer:

No WebSocket (WS) connections were detected during manual inspection.

Verification:

Chrome DevTools

```
Network → Socket (WS)
```

After refreshing the page, no WebSocket requests were observed.

---

- [x] What updates automatically?

Answer:

The dashboard displays live monitoring information including:

- Temperature
- Humidity
- Device Status
- Last Updated timestamp

The values appear to be refreshed dynamically as part of the monitoring dashboard. During manual inspection, no WebSocket traffic was detected, indicating updates may occur through periodic HTTP requests or polling.

---

# Selectors (Manual)

## Main navigation selectors

Observed navigation items

- Dashboard
- Reports
- Alerts
- Devices
- Alarms
- Users

Expected selector examples for automation

```css
nav
aside
.sidebar
.menu
```

Angular root element

```html
<ib-iot-root>
```

---

## Key buttons

- New Report
- Live Alerts
- Assign Devices
- Fetch
- Search
- Download
- Edit
- Delete
- Rules

---

## Input fields

- Search Reports
- Search Alerts
- Search Devices
- Search Users
- Location Dropdown
- Device Dropdown
- Sensor Dropdown
- Status Dropdown
- Period Dropdown
- Sort Toggle

---

# Risks

## Rate limiting

Answer:

No rate limiting was observed during manual testing.

---

## Redirects

Answer:

Unauthenticated users are redirected to the login page. Authenticated navigation occurs within the application dashboard.

---

## Authentication walls

Answer:

Yes.

Dashboard functionality and all management modules require authentication before access.

---

# Notes

Additional observations:

- The application is an Angular-based Single Page Application (SPA).
- Navigation is performed using a persistent left sidebar.
- Dashboard displays IoT device health and monitoring metrics.
- Reports, Alerts, Devices, Alarms, and Users are separate functional modules.
- Multiple pages include search bars, filters, dropdowns, and data tables.
- The application uses authenticated session-based access.
- No WebSocket communication was detected during inspection.
- The application appears to update monitoring data dynamically, likely using periodic HTTP polling instead of WebSockets.
- Stable selectors should be preferred during Playwright automation. Angular-generated attributes such as `_ngcontent-*` and `_nghost-*` should be avoided because they are dynamically generated.


---

# Conclusion

The Week 3 live IoT pipeline is operational and able to crawl, analyze, and generate Playwright automation for the live Angular application.

The major infrastructure required for the live application has been completed successfully, including authentication support, SPA hydration handling, authenticated crawling, route discovery, selector extraction, selector prioritization, and prompt tuning for live IoT dashboards.

The remaining issues are concentrated in the Playwright code generation and conversion stages rather than the crawler itself.

---

# Successfully Completed

## Live Application Discovery

- Live application analyzed successfully.
- Angular framework identified (Angular 18.2.13).
- Authentication requirements documented.
- Live application design document created.
- Navigation structure documented.
- Dashboard widgets documented.

---

## Scraper

- Playwright-based crawler implemented.
- Authenticated crawling enabled using `auth.json`.
- SPA hydration waits implemented.
- Dynamic route discovery implemented.
- Duplicate route filtering implemented.
- Multi-page crawling verified.
- Route queue handling improved.

---

## Authentication

- Automated login implemented.
- Authentication state persisted using `auth.json`.
- Authenticated browser contexts reused during crawling.
- Protected routes successfully accessed.

---

## Selector Discovery

- Selector prioritization improved for Angular SPA.
- Stable selector extraction verified.
- Duplicate selectors filtered.
- Dynamic selectors ignored where possible.

---

## Selector Stability

Three consecutive crawler executions produced identical results.

| Run | Pages | Selectors |
|------|-------|-----------|
| 1 | 3 | 43 |
| 2 | 3 | 43 |
| 3 | 3 | 43 |

Variation:

```
0 selectors
```

Result:

✅ Selector Stability PASS

---

## Prompt Improvements

Completed prompt updates for:

- Strategy Agent
- YAML Generation
- Edge Cases Agent

Prompt tuning now considers:

- Live IoT dashboards
- Dynamic data
- SPA behaviour
- Widget visibility
- Presence-based assertions
- Navigation validation
- Live-data constraints

---

## Performance

Performance baseline module added.

Capabilities include:

- Live route response measurements
- TTFB measurement
- Average response time calculation
- JSON performance reports

---

# Remaining Issues

Although the pipeline executes successfully, several code generation issues remain.

## Review Agent Findings

- Incorrect `expect_page()` generation.
- Invalid Playwright locators.
- Unsupported Playwright conversion steps.
- Hardcoded URLs in generated tests.
- Weak assertions generated for dynamic widgets.
- Authentication not automatically injected into generated tests.
- Duplicate waits generated in some scenarios.

---

## Pipeline Limitations

- Review agent required two regeneration attempts.
- Maximum regeneration limit reached.
- One generated Playwright test still failed.
- Unsupported conversion rules remain.

---

# Root Cause Analysis

The crawler and discovery pipeline are functioning correctly.

Most remaining failures originate from the Playwright code generation pipeline rather than the crawler.

Primary causes include:

- YAML-to-Playwright conversion limitations.
- Weak locator generation.
- Unsupported automation actions.
- Missing authenticated fixture injection.
- Incomplete review feedback incorporation.

---

# Day 14 Action Items

## High Priority

- Fix `expect_page()` generation.
- Improve Playwright locator generation.
- Automatically inject authenticated session (`auth.json`) into generated tests.
- Replace hardcoded URLs with `base_url`.
- Improve widget-specific assertions.
- Remove redundant waits.
- Improve regeneration quality.

---

## Medium Priority

- Improve YAML conversion rules.
- Reduce unsupported Playwright actions.
- Improve review feedback incorporation.
- Strengthen assertion generation.
- Improve selector ranking.

---

## Low Priority

- Expand route discovery depth.
- Improve crawler performance.
- Add additional live dashboard widgets.
- Expand edge-case generation.

---

# Overall Project Status

| Component | Status |
|-----------|--------|
| Live App Discovery | ✅ Complete |
| Authentication | ✅ Complete |
| Angular Detection | ✅ Complete |
| SPA Hydration | ✅ Complete |
| Authenticated Crawling | ✅ Complete |
| Route Discovery | ✅ Complete |
| Selector Discovery | ✅ Complete |
| Selector Stability | ✅ Complete |
| Performance Baseline | ✅ Complete |
| Strategy Prompt | ✅ Complete |
| YAML Prompt | ✅ Complete |
| Edge Cases Prompt | ✅ Complete |
| Live Design Document | ✅ Complete |
| Pipeline Execution | ✅ Complete |
| Review Agent | ⚠ Needs Improvement |
| Playwright Code Generation | ⚠ Needs Improvement |
| YAML → Playwright Converter | ⚠ Needs Improvement |

---

# Final Assessment

The Week 3 migration from the sample application to the live IoT dashboard has been successfully completed.

The crawler, discovery pipeline, authentication flow, prompt engineering, and selector extraction are stable and suitable for continued development.

The remaining work is focused on improving the Playwright code generation and review pipeline to produce fully executable, production-quality automated tests.

**Overall Status:** ⚠️ **Pipeline Functional — Requires Playwright Code Generation Improvements Before Production Deployment.**