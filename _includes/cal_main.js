<script src="https://apis.google.com/js/api.js"></script>
<script>
// javascript to access all seminar google calendars which puts them onto main page;
// its modifications can be used for seminar pages
  var userEmail = [ //do not reorder as seminar links depend on this. This also has to match _data/seminars.yml
    "dd0lvqfa6j2vtbocbhnsp3u380@group.calendar.google.com",   //0 - hmm? empty old defunct
    "6njs6bnklu56g6lhi5ojl2pha8@group.calendar.google.com",   //1 - geometry
    "lhnqsj4qdhf8e7hn692c7to8ao@group.calendar.google.com",   //2 - math club
    "5rjqjb9rg8t3ent7bo5kp4fka0@group.calendar.google.com",   //3 - harmonic seminar
    "k613quo3pribde7jrm5e12ft1c@group.calendar.google.com",   //4 - math physics
    "d2u7r4bb07jlh8v71pp61nrs3s@group.calendar.google.com",   //5 - algebra
    "j3a6i93k8m7ulpp9n5bg8vbb4g@group.calendar.google.com",   //6 - colloquium
    "f0un05c36pdv08n0m90bi99jmk@group.calendar.google.com",   //7 - probability
    "pce8r0mnja2do20vkku2gslamk@group.calendar.google.com",   //8 - topology
    "empty@virginia.edu", //was starrie???
		//9 - hmm? seems like the old calendar for many events, and now seems defunct
    //add new seminar calendars here and modify the function giving the link as well as _data/seminars.yml
    "n6dhh35l2td9i73ii6dbkpqtro@group.calendar.google.com",   //10 - gradsem
    "8qr0g4b576nd86cvbaogamclj8@group.calendar.google.com",   //11 - galois
    "ftc1mbjbp95irpj6t9e2tfl020@group.calendar.google.com",   //12 - operator
    "fj2uv2u9ea74h8b0gihm3iu73c@group.calendar.google.com",   //13 - analysis commons
    "3ehl1jte3jnlftm6h5m28b96jo@group.calendar.google.com",   //14 - AWM
    "56un1k179o7d8mtj85o12qsg7c@group.calendar.google.com",   //15 - Number Theory
    // (REMOVE AMS CHAPTER) "c_60f1de561954223e1933f83f3bfb2520fd742ca85cbd6a02dade97379ec7fad3@group.calendar.google.com",  // 16 - AMS chapter
    //do not touch the last seminar (it is empty and it is needed for IE compatibility)
    "c7vr381laveomub6abc4vh3qos@group.calendar.google.com"
    // this last one is the empty calendar with no seminar link (also for compatibility with IE)
  ]; //list of all calendars, new seminar google calendars can be added here
  var apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
  // google API keys
  var userTimeZone = "New_York"; // Charlottesville is in this timezone so we keep it like this
  var maxSeminars = {{include.max_sem}}; //This is the number of seminars to display
  var maxRows = {{include.max_from_cal}}; //This is the number of events to pull from each of the calendars


  var propSep = "__sep__";

  var eventsArray = [];
  var calsArray = [];

//various seminar things
  function getSeminar(num)
  {
    if(num == 1) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "1" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 2) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "2" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 3) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "3" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 4) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "4" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 5) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "5" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 6) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "6" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 7) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "7" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 8) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "8" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 9) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "9" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 10) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "10" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 11) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "11" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 12) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "12" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 13) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "13" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    if(num == 14) { return '<a href="{{site.url}}/awm/calendar/">AWM at UVA</a>'; }
    if(num == 15) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "15" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
    //if(num == 16) { return '<a href="{{site.url}}/ams_chapter/">AMS Student Chapter</a>'; }
    if(num == 17) { return '{% for sem in site.data.seminars %}{% if sem.cal_number == "16" %}<a href="{{site.url}}/seminars/{{ sem.shortname }}/">{{sem.name}}</a>{% endif %}{% endfor %}'; }
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
      var retStr = ['<details><summary>Description</summary>' , abst.replace(/(?:\r\n|\r|\n)/g, '<br />'), '<br><a href="' ,  htlink, '"  target="_blank">Google Calendar link</a><br>', '</details>'];
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

  //--------------------- main function makes API calls and displays results
  function start() {
    gapi.client.init({
      'apiKey': apiKey,
      'discoveryDocs': ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
    }).then(function() {
    var executeOnce = 0;
    {%if include.current %}
      var today = new Date();
      var future_day = new Date();
      future_day.setDate( future_day.getDate() + 180 ); //display only events 180 days into the future
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
            'timeMax': future_day.toISOString(),
          {%else%}
            'timeMin': ffr.toISOString(),
            'timeMax': tto.toISOString(),
          {%endif%}
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
                '<b><a href="' + item.htmlLink + '"  target="_blank">' +
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
                '<b><a href="' + item.htmlLink + '"  target="_blank">' +
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
              li.className = "mt-3";
              var elem = (eventsArray[j]+'').split(propSep)[1];
              li.innerHTML = elem + '';
              document.getElementById('events').appendChild(li);
            }
            executeOnce = 1;
          };
          document.getElementById('preloader').innerHTML = "";
        });
      };
    });
  });
};

  gapi.load('client', start);
</script>

<div id='preloader' class="h5" style="color:grey">Loading seminars...</div>
<div id='content' class="my-div-zebra">
  <div id='events'></div>
</div>
