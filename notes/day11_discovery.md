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

The Day 11 discovery successfully identified the architecture and behaviour of the live IoT application.

Key findings include:

- Authentication is required before accessing dashboard modules.
- The application is built using Angular 18.2.13.
- The application is a Single Page Application (SPA).
- Dashboard data updates dynamically.
- Stable selectors were identified for automation.
- Authenticated crawling and selector extraction were successfully validated.

The discovery phase provides a solid foundation for building reliable Playwright automation against the live application.