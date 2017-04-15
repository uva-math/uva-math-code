<script>
  var apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
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
  ]; //your calendar Ids
  var clientId = '924411057957-0d9mrr6c8uvgsbdq1v1he5ha0je1om3d.apps.googleusercontent.com';
  var userTimeZone = "New_York"; //example "Rome" "Los_Angeles" ecc...
  var maxRows = 3; //events to shown
  var scopes = 'https://www.googleapis.com/auth/calendar.readonly';

  var eventsArray = [];

  //--------------------- Add a 0 to numbers
  function padNum(num) {
      if (num <= 9) {
          return "0" + num;
      }
      return num;
  }
  //--------------------- end

  //--------------------- From 24h to Am/Pm
  function AmPm(num) {
      if (num <= 12) { return "am " + num; }
      return "pm " + padNum(num - 12);
  }
  //--------------------- end

  //--------------------- num Month to String
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
  //--------------------- end

  //--------------------- from num to day of week
  function dayString(num){
           if (num == "1") { return "Mon" }
      else if (num == "2") { return "Tue" }
      else if (num == "3") { return "Wed" }
      else if (num == "4") { return "Thu" }
      else if (num == "5") { return "Fri" }
      else if (num == "6") { return "Sat" }
      else if (num == "0") { return "Sun" }
  }
  //--------------------- end

  //--------------------- client CALL
  function handleClientLoad() {
      gapi.client.setApiKey(apiKey);
      checkAuth();
  }
  //--------------------- end

  //--------------------- check Auth
  function checkAuth() {
      gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
  }
  //--------------------- end

  //--------------------- handle result and make CALL
  function handleAuthResult(authResult) {
      if (authResult) {
          makeApiCall();
      }
  }
  //--------------------- end

  function appendPre(message) {
    var pre = document.getElementById('content');
    var textContent = document.createTextNode(message + '\n');
    pre.appendChild(textContent);
  }

  //--------------------- API CALL itself

  function makeApiCall(callback) {
    var executeOnce = 0;
    var today = new Date();
    today.setDate(today.getDate());
    gapi.client.load('calendar', 'v3', function () {
      for(var cal_i = 0; cal_i < userEmail.length; cal_i++ )
      {
        var request = gapi.client.calendar.events.list({
          'calendarId' : userEmail[cal_i],
          'timeZone' : userTimeZone,
          'singleEvents': true,
          'timeMin': today.toISOString(),
          'maxResults': maxRows,
          'orderBy': 'startTime'});
        request.execute(function (resp) {
          for (var i = 0; i < resp.items.length; i++) {
            var item = resp.items[i];
            var allDay = item.start.date? true : false;
            var startDT = allDay ? item.start.date : item.start.dateTime;
            eventsArray.push(startDT + ' ' + item.summary);
            // appendPre(startDT + ' ' + item.summary);
            }
            if(eventsArray.length == 19 && !executeOnce)
            {
              eventsArray.sort();
              for (var j = 0; j < eventsArray.length; j++)
              {
                appendPre(j + '  ' + eventsArray[j]);
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
