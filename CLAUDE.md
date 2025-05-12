# UVA Math Website Guidelines

## File Naming Conventions

### Announcements

When creating a new announcement, the file name should include **today's date** (the creation date) rather than the date of the event being announced.

#### Examples:

**Correct:**
- `2023-11-15-announcing-upcoming-holiday-party.md` (where 2023-11-15 is today's date when the announcement is created)
- `2025-03-12-james-teaching.md` (file created on March 12, 2025, even though it announces a future event)
- `2025-04-08-AWM-mathclub-colloq.md` (file created on April 8, 2025, even though the colloquium might be on a different date)

**Incorrect:**
- `2023-12-20-announcing-upcoming-holiday-party.md` (where 2023-12-20 is the date of the holiday party itself)
- `2025-05-17-final-exercises.md` (if created before May 17, should use the creation date instead)

### Categories

Make sure to include the appropriate categories in the front matter of announcement files:

```yaml
categories: news events conferences
```

- Use `conferences` for all workshop, symposium, and conference announcements
- Use `major-news` for important department announcements
- Always include `news` and `events` for event announcements
