---
title: AMS Grad Student Chapter
layout: static_page_no_right_menu
permalink: /ams_chapter/
nav_parent: Graduate
nav_nesting: true
nav_weight: 970
nav_id: AMS Grad Student Chapter
---

###  AMS Graduate Student Chapter

The mission of the University of Virginia graduate student chapter of the AMS is informed by the objectives of the <a href="https://www.ams.org/home/page">American Mathematical Society (AMS)</a>, whose mission statement is attached below. Our chapter seeks to nurture intellectual, professional, and community development among our members. We host events in service of this goal, such as panel discussions, talks, and social gatherings, including collaborations with fellow AMS graduate student chapters!

To become a member and enjoy extra perks, such as being added to the chapter mailing list, please fill out <a href="https://forms.gle/WRxuXZMt9JvpvvqAA">this form</a>. Membership is free!

###  Executive committee

The University of Virginia AMS graduate student chapter executive committee consists of:
<ul>
  <li>President: <a href="https://eleanormcspirit.com/">Eleanor McSpirit</a></li>
  <li>Vice President: <a href="https://alejandrodlpc.github.io/">Alejandro de las Peñas Castaño</a></li>
  <li>Secretary: <a href="https://sites.google.com/view/eleftherios-chatzitheodoridis/home">Eleftherios Chatzitheodoridis</a></li>
  <li>Treasurer: <a href="https://math.virginia.edu/people/guc8ns/">Petch Chueluecha</a></li>
  <li>Member At Large: <a href="https://sites.google.com/view/maxsg">Maximiliano Sánchez Garza</a></li>
</ul>
Fellow AMS graduate student chapters are most welcome and encouraged to get in touch with us for joint social events!

### Calendar

<table class="table table-striped">
    <caption style="caption-side: top;"><a href="https://calendar.google.com/calendar/u/0/r?cid=c_60f1de561954223e1933f83f3bfb2520fd742ca85cbd6a02dade97379ec7fad3@group.calendar.google.com" rel="external noopener" target="_blank">Add to your calendar</a></caption>
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
    const CALENDAR_ID = 'c_60f1de561954223e1933f83f3bfb2520fd742ca85cbd6a02dade97379ec7fad3@group.calendar.google.com';


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
          'maxResults': 5,
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
                  ${event.description ? `<details style="white-space: pre-wrap;"><summary style="display: list-item">Details</summary>${event.description}</details>` : ''}
                </td>
            </tr>
          `).join('');
      document.getElementById('event-content').innerHTML = output;
    }

  </script>

<script async defer src="https://apis.google.com/js/api.js" onload="gapiLoaded()"></script>

###  AMS mission statement

The AMS, founded in 1888 to further the interests of mathematical research and scholarship, serves the national and international community through its publications, meetings, advocacy and other programs, which
<ul>
  <li>promote mathematical research, its communication and uses,</li>
  <li>encourage and promote the transmission of mathematical understanding and skills,</li>
  <li>support mathematical education at all levels,</li>
  <li>advance the status of the profession of mathematics, encouraging and facilitating full participation of all individuals, and</li>
  <li>foster an awareness and appreciation of mathematics and its connections to other disciplines and everyday life.</li>
</ul>

Our purpose is to foster a greater understanding of mathematics, encourage student activity in research and related mathematical experiences, and provide a social and intellectual forum for all students interested in mathematics.

Our goal is to invest in both the scholarly and social lives of our members. We host events to achieve this goal: organizing speakers, research and work retreats, and social gatherings, among others.

We seek to inform and educate graduate students on all aspects of mathematics, both as a subject and a profession. We also publicize opportunities and raise awareness of issues related to mathematics and professional development.
