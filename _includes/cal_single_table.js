<script>
// javascript to access all seminar google calendars which puts them onto main page;
// its modifications can be used for seminar pages
  var userEmail = ["{{include.google_cal_id}}"];
  var apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
  var clientId = '924411057957-0d9mrr6c8uvgsbdq1v1he5ha0je1om3d.apps.googleusercontent.com';
  var scopes = 'https://www.googleapis.com/auth/calendar.readonly';
  // google API keys
  var userTimeZone = "New_York"; // Charlottesville is in this timezone so we keep it like this
  var maxSeminars = {{include.max_sem}}; //This is the number of seminars to display

  var propSep = "__sep__";

  var eventsArray = [];
  var calsArray = [];

  function getLocation(loc)
  {
    if (loc)
    {
      return loc + '<br>';
    }
    return '';
  }
  function getAbstract(abst, htlink)
  {
    if (abst)
    {
      var retStr = ['<details><summary>Abstract</summary>' , abst.replace(/(?:\r\n|\r|\n)/g, '<br />'), '<br><a href="' ,  htlink, '">Google Calendar link</a><br>', '</details>'];
      // appendPre(retStr);
      return retStr.join('');
    }
    return '';
  }

// ------------

  function padNum(num) {
      if (num <= 9) {
          return "0" + num;
      }
      return num;
  }
  function AmPm(num) {
      if (num <= 12) { return num; }
      return padNum(num - 12);
  }
  function AmPm1(num) {
      if (num < 12) { return "am"; }
      return "pm";
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

  //--------------------- main function makes API calls and displays results
  function makeApiCall(callback) {
    var executeOnce = 0;
    {%if include.current %}
      var today = new Date();
      today.setDate(today.getDate() {%if include.days_back != null%}- {{include.days_back}}{%endif%}); //access current data from some days ago
    {%else%}
      var ffr = new Date('{{include.show_from}}'); //access historical data
      var tto = new Date('{{include.show_to}}');
    {%endif%}
    var request = [];

    //this part calls the API
    gapi.client.load('calendar', 'v3', function () {
      for(var cal_i = 0; cal_i < userEmail.length; cal_i++ )
      {
        request[cal_i] =
        [
          gapi.client.calendar.events.list({
          'calendarId' : userEmail[cal_i],
          'timeZone' : userTimeZone,
          'singleEvents': true,
          {%if include.current %}
            'timeMin': today.toISOString(),
          {%else%}
            'timeMin': ffr.toISOString(),
            'timeMax': tto.toISOString(),
          {%endif%}
          'maxResults': maxSeminars,
          'orderBy': 'startTime'}),
          cal_i
        ];
      }
      //this part packs the results into a single array
      for(let cal_j = 0; cal_j < userEmail.length; cal_j++ )
      {
        request[cal_j][0].execute(function (resp)
        {
          calsArray.push(cal_j);
          for (var i = 0; i < resp.items.length; i++)
          {
            // formatted google calendar events are packed into array of strings here
            var item = resp.items[i];
            var allDay = item.start.date? true : false;
            var startDT = allDay ? item.start.date : item.start.dateTime;
            var dateTime = startDT.split("T"); //split date from time
            var date = dateTime[0].split("-"); //split yyyy mm dd
            var startYear = date[0];
            var startMonth = monthString(date[1]);
            var startDay = date[2];
            var startDateISO = new Date(startMonth + " " + startDay + ", " + startYear + " 00:00:00");
            var startDayWeek = dayString(startDateISO.getDay());
            if( allDay == true)
            {
              var strBegin = startDT +
                propSep +
                '<b><a href="' + item.htmlLink + '" class="h6 mt-6">' +
                  startDayWeek + ' ' +
                  startMonth + ' ' +
                  startDay + ', ' +
                startYear + '</a></b>';
            }
            else
            {
              var time = dateTime[1].split(":"); //split hh ss etc...
              var startHour = AmPm(time[0]);
              var startMin = time[1];
              var strBegin = startDT +
                propSep +
                '<b><a href="' + item.htmlLink + '" class="h6 mt-6">' +
                startDayWeek + ' ' +
                startMonth + ' ' +
                startDay + ', ' +
                startYear + ' @ ' +
                startHour + ':' +
                startMin + ' ' +
                AmPm1(time[0]) + '</a></b>';
            }
            var str = '<h5 class="mt-1" style="text-transform:none !important">' +
            item.summary + '</h5>' +
            getLocation(item.location) +
            getAbstract(item.description, item.htmlLink);
            // formatted google calendar events are packed into array of strings here
            eventsArray.push(str);

          }
          if(calsArray.length == userEmail.length && !executeOnce)
          {
            eventsArray.sort();
            // the array is sorted after all calendars are processes
            var eventsToDisplay = eventsArray.length > maxSeminars ? maxSeminars : eventsArray.length;
            {%if include.current %}
              for (var j = 0; j < eventsToDisplay; j++)
              {
                //this is where the events' representation happens
                var li = document.createElement('p');
                li.className = "mb-3";
                var elem = (eventsArray[j]+'');
                li.innerHTML = elem;
                document.getElementById('events').appendChild(li);
              }
            {% else %}
              for (var j = eventsToDisplay - 1; j>=0; j--)
              {
                //this is where the events' representation happens
                var tr = document.createElement('tr');
                var tdd = document.createElement('td');
                var tdb = document.createElement('td');
                tr.className = "mb-3";
                var elem = (eventsArray[j]+'');
                var dateTimeOfSem = (strBegin+'').split(propSep)[1];
                tdd.innerHTML = dateTimeOfSem;
                tdb.innerHTML = elem
                tr.appendChild(tdd);
                tr.appendChild(tdb);
                document.getElementById('events').appendChild(tr);
              }
            {% endif %}

            executeOnce = 1;
          };
        });
      };
    });
  }
</script>
<script src='https://apis.google.com/js/client.js?onload=handleClientLoad'></script>

<div id='content'>
  <table >
  <h3>Fall Semester</h3>
  <thead>
      <tr>
          <th width="12%">Date</th>
          <th>Speaker and Title</th>
      </tr>
  </thead>
  <tbody class="my-tr-zebra" id='events'>

  </tbody>
  </table>
</div>
