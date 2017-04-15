<script>
// javascript to access all seminar google calendars which puts them onto main page;
// its modifications can be used for seminar pages
  var userEmail = [
    "dd0lvqfa6j2vtbocbhnsp3u380@group.calendar.google.com",
    "6njs6bnklu56g6lhi5ojl2pha8@group.calendar.google.com",
    "lhnqsj4qdhf8e7hn692c7to8ao@group.calendar.google.com",
    "5rjqjb9rg8t3ent7bo5kp4fka0@group.calendar.google.com",
    "k613quo3pribde7jrm5e12ft1c@group.calendar.google.com",
    "d2u7r4bb07jlh8v71pp61nrs3s@group.calendar.google.com",
    "j3a6i93k8m7ulpp9n5bg8vbb4g@group.calendar.google.com",
    "f0un05c36pdv08n0m90bi99jmk@group.calendar.google.com",
    "pce8r0mnja2do20vkku2gslamk@group.calendar.google.com",
    "starrie@virginia.edu"
  ]; //list of all calendars, new seminar google calendars can be added here
  var apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
  var clientId = '924411057957-0d9mrr6c8uvgsbdq1v1he5ha0je1om3d.apps.googleusercontent.com';
  var scopes = 'https://www.googleapis.com/auth/calendar.readonly';
  // google API keys
  var userTimeZone = "New_York"; // Charlottesville is in this timezone so we keep it like this
  var maxRows = 7;

  var propSep = "__sep__";

  var eventsArray = [];
  var calsArray = [];

  function padNum(num) {
      if (num <= 9) {
          return "0" + num;
      }
      return num;
  }
  function AmPm(num) {
      if (num <= 12) { return "am " + num; }
      return "pm " + padNum(num - 12);
  }
  function monthString(num) {
           if (num === "01") { return "Jan"; }
      else if (num === "02") { return "Feb"; }
      else if (num === "03") { return "Mar"; }
      else if (num === "04") { return "Apr"; }
      else if (num === "05") { return "May"; }
      else if (num === "06") { return "Jun"; }
      else if (num === "07") { return "Jul"; }
      else if (num === "08") { return "Aug"; }
      else if (num === "09") { return "Sep"; }
      else if (num === "10") { return "Oct"; }
      else if (num === "11") { return "Nov"; }
      else if (num === "12") { return "Dec"; }
  }
  function dayString(num){
           if (num == "1") { return "Mon" }
      else if (num == "2") { return "Tue" }
      else if (num == "3") { return "Wed" }
      else if (num == "4") { return "Thu" }
      else if (num == "5") { return "Fri" }
      else if (num == "6") { return "Sat" }
      else if (num == "0") { return "Sun" }
  }
  function handleClientLoad() {
      gapi.client.setApiKey(apiKey);
      checkAuth();
  }
  function checkAuth() {
      gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
  }
  function handleAuthResult(authResult) {
      if (authResult) {
          makeApiCall();
      }
  }
  function appendPre(message) {
    //prints in a bare way
    var pre = document.getElementById('content');
    var textContent = document.createTextNode(message + '\n');
    pre.appendChild(textContent);
  }

  //--------------------- main function makes API calls and displays results
  function makeApiCall(callback) {
    var executeOnce = 0;
    var today = new Date();
    var request = [];
    today.setDate(today.getDate() - 1);
    gapi.client.load('calendar', 'v3', function () {
      for(var cal_i = 0; cal_i < userEmail.length; cal_i++ )
      {
        request[cal_i] = gapi.client.calendar.events.list({
          'calendarId' : userEmail[cal_i],
          'timeZone' : userTimeZone,
          'singleEvents': true,
          'timeMin': today.toISOString(),
          'maxResults': maxRows,
          'orderBy': 'startTime'});
      }
      for(var cal_j = 0; cal_j < userEmail.length; cal_j++ )
      {
        request[cal_j].execute(function (resp)
        {
          calsArray.push('');
          for (var i = 0; i < resp.items.length; i++) {
            var item = resp.items[i];
            var allDay = item.start.date? true : false;
            var startDT = allDay ? item.start.date : item.start.dateTime;

            eventsArray.push(startDT + propSep + calsArray.length + propSep + item.summary);
            // formatted google calendar events are put into array as strings

          }
          if(calsArray.length == userEmail.length && !executeOnce)
          {
            eventsArray.sort();
            // the array is sorted after all calendars are processes
            for (var j = 0; j < eventsArray.length; j++)
            {
              //this is where the events' representation happens
              el = eventsArray[j];
              // appendPre(el.split(propSep)[0]);
              appendPre(el);
            }
            executeOnce = 1;
          };
        });
      };
    });
  }
</script>
<script src='https://apis.google.com/js/client.js?onload=handleClientLoad'></script>

<pre id="content"></pre>
