# MRBS accessibility follow-up — September 2026

Source: `UVA Math Website Accessibility Review September 2026.docx` in LP's Downloads. The 24 embedded screenshots were inspected; image 20 shows the MRBS calendar and date-picker focus problem. This note records the review's findings, not a fresh audit of the running MRBS application.

LP requested on September 13, 2026 that MRBS remediation and its more complicated deployment be handled separately from the Jekyll website. This checkout contains links to MRBS, not the application source. Do not assume the website's S3 deployment updates MRBS.

## Assessment

Significant, with high-priority barriers in the core calendar and login workflows. Keyboard and screen-reader users may have difficulty determining their current calendar position, choosing a room, understanding booking types, and recovering from login errors. These are more consequential than the smaller typography and page-title defects. The report does not establish that every booking task is impossible.

The reviewer had no account and could not evaluate authenticated event details or creation of new bookings. That is an important coverage gap; it must be tested before claiming the application is accessible.

## Fix first: calendar and login

- Date picker: ensure keyboard focus is visible on the actual focused date, distinct from today and the selected date, in every state. Test Tab and arrow keys. The screenshot shows today September 9, selected September 16, and invisible keyboard focus on September 21.
- Week calendar: draw the complete focus outline on the active cell; move the visual indicator with arrow-key focus, not only after the next Tab press. Check clipping by scroll containers.
- Room selector: add a persistent visible `<label>` associated with the control. Keep focus on the selector after changing rooms; do not reset it to the page banner. If selection currently causes navigation, provide an explicit submit action or restore focus reliably after navigation.
- Booking types: include readable type names (Class, Seminar, Meeting, Office Hours, Exam) with each event. Color and the color legend alone are insufficient. Check compact cells and the agenda view too.
- Login: announce validation errors via an alert or a focused error summary; associate field-specific errors with inputs and preserve entered nonsecret data. Test missing and incorrect credentials without exposing them in logs.
- Authenticated workflows: test creating, editing and deleting a test booking, recurrence where authorized, conflict/error handling, confirmation, and return-focus behavior. Use a test environment/account and avoid changing real reservations.

## Shared page structure

Applies to Calendar, Log In, Help, and About MRBS:

- Give each page a distinct descriptive title, such as “Calendar | Math Room Booking” and “Log in | Math Room Booking.”
- Add a first-focusable skip link and a unique main-content target.
- Provide consistent department navigation. Avoid copying Jekyll output manually without a documented update mechanism.
- Remove redundant nested navigation landmarks around Calendar/Log In; label genuinely different navigation regions.
- Use strong, complete keyboard focus indicators on links, buttons, calendar cells, and date-picker controls.
- Use at least 16px body/supporting text (including Help and About) and verify zoom/reflow.
- Add the missing h1 on About MRBS and check the heading hierarchy on all pages.
- Combine duplicate week-view day/date links into a single descriptively named link.
- Check Back to Calendar and Technical Help button focus contrast on Help.

## Source and deployment discovery

1. Locate the actual running source and any GitHub/local repository; compare it with the deployed version before editing.
2. Identify upstream MRBS version, local UVA theme/customizations, PHP runtime, authentication integration, database/schema version, web-server paths, and asset build/cache behavior.
3. Document deployment and rollback. Preserve local configuration and secrets; do not copy credentials into this repository or the audit note.
4. Make changes in a separate checkout or staging environment and review the concrete diff before production deployment.
5. Verify on the deployed build after release, including cache invalidation.

The relevant public entry points are `/mrbs/index.php`, `/mrbs/help-uva.php`, and the application's login and technical-help links. The Jekyll information page is `info/mrbs.md` and is not the application.

## Verification

Use keyboard-only testing, NVDA or JAWS with a supported browser (matching the original audit), and VoiceOver/Safari where available. Test desktop and 320px reflow, 200% and 400% zoom, each calendar view, date picker, room changes, error states, and authenticated tasks. Automated checks supplement this work; passing axe does not establish that the calendar is usable.

## Interim route

The department office can assist with room reservations. Keep its email/phone prominently available from the website's MRBS information page while remediation is pending. This is an interim assistance route, not a substitute for fixing the application's controls.

## Status

Deferred by LP for separate work. No MRBS source or deployment was modified as part of the main website accessibility remediation.
