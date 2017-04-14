<script>
var apiKey = 'AIzaSyA7Uka7Cbx7SPTWqDn52Nw9XPAe1kdQZxs';
var userEmail = [
  "starrie@virginia.edu",
  "lhnqsj4qdhf8e7hn692c7to8ao@group.calendar.google.com",
  "5rjqjb9rg8t3ent7bo5kp4fka0@group.calendar.google.com",
  "k613quo3pribde7jrm5e12ft1c@group.calendar.google.com",
  "d2u7r4bb07jlh8v71pp61nrs3s@group.calendar.google.com",
  "j3a6i93k8m7ulpp9n5bg8vbb4g@group.calendar.google.com",
  "dd0lvqfa6j2vtbocbhnsp3u380@group.calendar.google.com",
  "6njs6bnklu56g6lhi5ojl2pha8@group.calendar.google.com",
  "f0un05c36pdv08n0m90bi99jmk@group.calendar.google.com",
  "pce8r0mnja2do20vkku2gslamk@group.calendar.google.com"
]; //your calendar Ids
var userTimeZone = "New_York"; //example "Rome" "Los_Angeles" ecc...
var maxRows = 10; //events to shown


var scopes = 'https://www.googleapis.com/auth/calendar';

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
    if (num <= 12) { return num; }
    return padNum(num - 12);
}
function AmPm1(num) {
    if (num <= 12) { return " am"; }
    return " pm";
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
    gapi.auth.authorize({scope: scopes, immediate: true}, handleAuthResult);
}
//--------------------- end

//--------------------- handle result and make CALL
function handleAuthResult(authResult) {
    if (authResult) {
        makeApiCall();
    }
}
//--------------------- end

//--------------------- API CALL itself
function makeApiCall() {
    var today = new Date(); //today date
    today.setDate(today.getDate() - 1); //today date minus one day
    gapi.client.load('calendar', 'v3', function () {
        var request = gapi.client.calendar.events.list({
            'calendarId' : userEmail[4],
            'timeZone' : userTimeZone,
            'singleEvents': true,
            'timeMin': today.toISOString(),  //collecting events from today minus one day
            'maxResults': maxRows,
            'orderBy': 'startTime'});
    request.execute(function (resp) {
            for (var i = 0; i < resp.items.length; i++) {
                var li = document.createElement('li');
                var item = resp.items[i];
                var classes = [];
                var allDay = item.start.date? true : false;
                var startDT = allDay ? item.start.date : item.start.dateTime;
                var dateTime = startDT.split("T"); //split date from time
                var date = dateTime[0].split("-"); //split yyyy mm dd
                var startYear = date[0];
                var startMonth = monthString(date[1]);
                var startDay = date[2];
                var startDateISO = new Date(startMonth + " " + startDay + ", " + startYear + " 00:00:00");
                var startDayWeek = dayString(startDateISO.getDay());

                if( allDay == true){ //change this to match your needs
                  var str = [
                  '<b><a href="', item.htmlLink, '">',
                  startDayWeek, ' ',
                  startMonth, ' ',
                  startDay, ', ',
                  startYear, '</a></b> - ', item.summary, ' in <b>', item.location, '</b><br><br>'
                  ];
                }
                else{
                    var time = dateTime[1].split(":"); //split hh ss etc...
                    var AmPmInd = AmPm1(time[0])
                    var startHour = AmPm(time[0]);
                    var startMin = time[1];
                    var str = [ //change this to match your needs
                        '<b><a href="', item.htmlLink, '">',
                        startDayWeek, ' ',
                        startMonth, ' ',
                        startDay, ', ',
                        startYear, ' @ ',
                        startHour, ':', startMin, AmPmInd, '</a></b> - ', item.summary, ' in <b>', item.location, '</b><br><br>'
                        ];
                }

                li.innerHTML = str.join('');
                li.setAttribute('class', classes.join(' '));
                document.getElementById('events').appendChild(li);

            }
        document.getElementById('calendar').innerHTML = calName;
        });
    });
}
//--------------------- end
</script>

<script src='https://apis.google.com/js/client.js?onload=handleClientLoad'></script>

<div id='content'>
  <ul id='events'></ul>
</div>
