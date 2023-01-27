---
title: DRP Calendar
layout: drp_page
permalink: /drp/calendar/
---
// Script contributed by Markus Tuominen
<h2 class="mb-3">Timeline</h2>

<table class="table table-striped">
    <caption style="caption-side: top;"><a href="https://calendar.google.com/calendar/u/0/r?cid=c_428da1776779765e670bf757dffa8c89156532333693ea77794fbac9b58e8b67@group.calendar.google.com" rel="external noopener" target="_blank">Add to your calendar</a></caption>
    <tbody id="event-content">
        <tr class="font-weight-bold">
            <td>
                Loading calendar...
            </td>
        </tr>
    </tbody>
</table>

<script type="text/javascript">
    const API_KEY = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
    const DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest';
    const CALENDAR_ID = 'c_428da1776779765e670bf757dffa8c89156532333693ea77794fbac9b58e8b67@group.calendar.google.com';


    function gapiLoaded() {
      gapi.load('client', initializeGapiClient);
    }

    async function initializeGapiClient() {
      try {
        await gapi.client.init({
          apiKey: API_KEY,
          discoveryDocs: [DISCOVERY_DOC],
        });
      } catch (err) {
        console.error(err.message)
        document.getElementById('event-content').innerHTML = `<tr class="font-weight-bold"><td>Failed to initialize calendar API</td></tr>`;
        return;
      }
      gapi.client.load('calendar', 'V3', listUpcomingEvents)
    }

    async function listUpcomingEvents() {
      let response;
      try {
        const request = {
          'calendarId': CALENDAR_ID,
          'timeMin': (new Date()).toISOString(),
          'showDeleted': false,
          'singleEvents': true,
          'maxResults': 20,
          'orderBy': 'startTime',
          'timeZone': 'America/New_York',
        };
        response = await gapi.client.calendar.events.list(request);
      } catch (err) {
        console.error(err.message)
        document.getElementById('event-content').innerHTML = `<tr class="font-weight-bold"><td>Failed to load calendar</td></tr>`;
        return;
      }

      const events = response.result.items;
      if (!events || events.length == 0) {
        document.getElementById('event-content').innerHTML = `<tr class="font-weight-bold"><td>No scheduled events</td></tr>`;
        return;
      }
      const dateFormatter = new Intl.DateTimeFormat("en-US", {weekday: "short", month:"short", day:"2-digit", year:"numeric"})
      const dateTimeFormatter = new Intl.DateTimeFormat("en-US", {weekday: "short", month:"short", day:"2-digit", year:"numeric", hour:"2-digit", minute:"2-digit", timeZone: 'America/New_York'})

      const output = events.map(
          (event) => `
            <tr>
                <td>
                  <a class="font-weight-bold" href=${event.htmlLink} rel="external noopener" target="_blank">
                    <time datetime=${(new Date(event.start.date ?? event.start.dateTime)).toISOString()}>${event.start.date ? dateFormatter.format(new Date(event.start.date)) : dateTimeFormatter.format(new Date(event.start.dateTime))}</time>
                  </a>
                  <h5>${event.summary}</h5>
                  ${event.location ? `${event.location}</br>` : ''}
                  ${event.description ? `<details><summary style="display: list-item">Details</summary>${event.description}</details>` : ''}
                </td>
            </tr>
          `).join('');
      document.getElementById('event-content').innerHTML = output;
    }

  </script>

<script async defer src="https://apis.google.com/js/api.js" onload="gapiLoaded()"></script>
