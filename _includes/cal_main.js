<script>
// javascript to access all seminar google calendars which puts them onto main page;
// its modifications can be used for seminar pages
  var userEmail = [ //do not reorder as seminar links depend on this. This also has to match _data/seminars.yml
    "dd0lvqfa6j2vtbocbhnsp3u380@group.calendar.google.com",   //1 - geometry
    "6njs6bnklu56g6lhi5ojl2pha8@group.calendar.google.com",   //2 - math club
    "lhnqsj4qdhf8e7hn692c7to8ao@group.calendar.google.com",   //3 - harmonic seminar
    "5rjqjb9rg8t3ent7bo5kp4fka0@group.calendar.google.com",   //4 - math physics
    "k613quo3pribde7jrm5e12ft1c@group.calendar.google.com",   //5 - algebra
    "d2u7r4bb07jlh8v71pp61nrs3s@group.calendar.google.com",   //6 - colloquium
    "j3a6i93k8m7ulpp9n5bg8vbb4g@group.calendar.google.com",   //7 - probability
    "f0un05c36pdv08n0m90bi99jmk@group.calendar.google.com",   //8 - topology
    "pce8r0mnja2do20vkku2gslamk@group.calendar.google.com",   //9 - hmm? seems like the old calendar for many events, and now seems defunct
    "starrie@virginia.edu",                                   //10 - hmm?
    //add new seminar calendars here and modify the function giving the link as well as _data/seminars.yml
    //do not touch the last seminar (it is empty and it is needed for IE compatibility)
    "c7vr381laveomub6abc4vh3qos@group.calendar.google.com"
    // this last one is the empty calendar with no seminar link (also for compatibility with IE)
  ]; //list of all calendars, new seminar google calendars can be added here
  var apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
  var clientId = '924411057957-0d9mrr6c8uvgsbdq1v1he5ha0je1om3d.apps.googleusercontent.com';
  var scopes = 'https://www.googleapis.com/auth/calendar.readonly';
  // google API keys
  var userTimeZone = "New_York"; // Charlottesville is in this timezone so we keep it like this
  var maxSeminars = 8; //This is the number of seminars to display
  var maxRows = 7; //This is the number of events to pull from each of the calendars

  var propSep = "__sep__";

  var eventsArray = [];
  var calsArray = [];

//various seminar things
  function getSeminar(num)
  {
    if(num == 1) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "1" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 2) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "2" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 3) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "3" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 4) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "4" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 5) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "5" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 6) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "6" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 7) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "7" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 8) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "8" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 9) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "9" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 10) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "10" %}<a href="{{sem.webpage}}">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    return '';
  }
  function getLocation(loc)
  {
    if (loc)
    {
      return 'in ' + loc;
    }
    return '';
  }
  function getAbstract(abst, htlink)
  {
    if (abst)
    {
      var retStr = ['<details><summary>Description</summary>' , abst.replace(/(?:\r\n|\r|\n)/g, '<br />'), '<br><a href="' ,  htlink, '">Google Calendar link</a><br>', '</details>'];
      // appendPre(retStr);
      return retStr.join('');
    }
    return '<br>';
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
    var today = new Date();
    var request = [];
    today.setDate(today.getDate() - 1); //access data from yesterday, and display a fixed number of events
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
          'timeMin': today.toISOString(),
          'maxResults': maxRows,
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
                '<b><a href="' + item.htmlLink + '">' +
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
                '<b><a href="' + item.htmlLink + '">' +
                startDayWeek + ' ' +
                startMonth + ' ' +
                startDay + ', ' +
                startYear + ' @ ' +
                startHour + ':' +
                startMin + ' ' +
                AmPm1(time[0]) + '</a></b>';
            }
            var str = strBegin + '<br>' +
            getSeminar(cal_j) + '<br><b>' +
            item.summary + '</b> ' +
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
            for (var j = 0; j < eventsToDisplay; j++)
            {
              //this is where the events' representation happens
              var li = document.createElement('div');
              var elem = (eventsArray[j]+'').split(propSep)[1];
              li.innerHTML = elem + '<br>';
              document.getElementById('events').appendChild(li);
            }
            executeOnce = 1;
          };
        });
      };
    });
  }
</script>
<script src='https://apis.google.com/js/client.js?onload=handleClientLoad'></script>

<div id='content'>
  <div id='events'></div>
</div>
