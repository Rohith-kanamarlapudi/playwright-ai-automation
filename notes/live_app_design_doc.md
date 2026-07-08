# IoTWebApp — Live Demo Dashboard

**URL:** https://live.ideabytesiot.com/demolive

---

## Application Description

The application is a live IoT Remote Monitoring System built as a Single Page Application (SPA) using Angular.

It provides real-time monitoring of IoT devices, sensor readings, alarms, alerts, reports, and user management. The dashboard updates dynamically and displays live operational data collected from connected devices.

Authentication is required before accessing the application.

---

## Technology

- Framework: Angular 18
- Application Type: Single Page Application (SPA)
- Authentication: Login Required
- Client-side Rendering
- Dynamic UI Updates
- Responsive Dashboard

---

## Key Pages / Modules

1. Dashboard
   - Device summary cards
   - Temperature widget
   - Humidity widget
   - Device status overview
   - Last updated timestamps

2. Reports
   - Scheduled Reports
   - On-Demand Reports
   - Report creation
   - Report download

3. Alerts
   - Live alerts table
   - Alert filters
   - Search functionality

4. Devices
   - Device inventory
   - Assigned devices
   - Device status
   - Hardware warranty
   - Software subscription

5. Alarms
   - Alarm rules
   - Threshold conditions
   - Alarm state
   - Trigger status

6. Users
   - User Management
   - Role Management
   - User search
   - User creation

---

## Navigation

Sidebar Navigation

- Dashboard
- Reports
- Alerts
- Devices
- Alarms
- Users

Top Navigation

- Notifications
- User Profile

---

## Key Widgets

Dashboard Summary Cards

- Total Devices
- Reporting Devices
- Good Status
- Warning Status
- Critical Status
- Not Reporting

Widgets

- Temperature display
- Humidity display
- Device information table
- Device status indicators
- Last Updated timestamps

Reports

- Reports table
- Search box
- Download buttons
- Create Report button

Alerts

- Filter panel
- Search box
- Alert table

Devices

- Device table
- Search
- Assign Device button

Alarms

- Rules table
- Edit/Delete actions

Users

- User table
- Search
- Add User button

---

## Test Constraints

Because this is a live IoT application:

- Never assert exact sensor values.
- Never assert exact temperatures or humidity values.
- Verify widgets are rendered.
- Verify values are displayed.
- Verify charts/tables load successfully.
- Verify navigation works correctly.
- Verify pages load without errors.
- Wait for SPA hydration before locating elements.
- Use stable selectors whenever possible.

---

## Dynamic Behaviour

The application contains live data.

Examples include:

- Temperature changes
- Humidity changes
- Device status updates
- Last Updated timestamps
- Alert information
- Dashboard statistics

Tests should verify element presence rather than exact values.

---

## Test Priorities

### Priority 1

- Login
- Dashboard loading
- Sidebar navigation

### Priority 2

- Reports module
- Alerts module
- Devices module
- Alarms module
- Users module

### Priority 3

- Dashboard widgets
- Search functionality
- Tables
- Filters
- Buttons

### Priority 4

- Responsive layout
- Empty states
- Error handling
- Session handling
- Authentication redirects

---

## Known Constraints

- Authentication required.
- Angular SPA hydration required.
- Live data changes continuously.
- Dynamic content should not use fixed-value assertions.
- Navigation occurs without full page reloads.
- Application uses client-side rendering.

---

## Automation Guidelines

Preferred assertions

- Element exists
- Element visible
- Widget rendered
- Table contains rows
- Navigation successful
- Buttons clickable
- Inputs editable

Avoid assertions

- Exact temperatures
- Exact humidity
- Exact timestamps
- Exact device counts
- Exact alert counts
- Exact dashboard statistics