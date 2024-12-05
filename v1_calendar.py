import re
from icalendar import Calendar, Event, vRecur
from dateutil import parser
from datetime import datetime, timedelta
import pytz

def day_of_week(day):
    if day == "monday":
        return 0
    elif day == "tuesday":
        return 1
    elif day == "wednesday":
        return 2
    elif day == "thursday":
        return 3
    elif day == "friday":
        return 4
    elif day == "saturday":
        return 5
    elif day == "sunday":
        return 6

index = 1
line_count = 1
events = {1 : {"dates" : [], "days" : [], "times" : []}}

file = open("/Users/veronikak/Documents/Side Projects/Calendar/classes.txt", "r")
for line in file:
    line = line.strip()

    if line == "Enrollment DeadlinesNo Exams Scheduled":
        index +=1
        events[index] = {"dates" : [], "days" : [], "times" : []}
        line_count = 1
    else :
        if line_count == 1:
            events[index]["class name"] = line
            line_count = 3
        elif re.search(r"\d{2}/\d{2}/\d{4}", line.split(" ")[0]):
            events[index]["dates"].append(line)
        elif line.startswith("Days: "):
            events[index]["days"].append(line)
        elif line.startswith("Times: "):
            events[index]["times"].append(line)
            line_count = 2
        elif line_count == 2 :
            events[index]["location"] = line
            line_count = 3       
file.close()

print()
print(events)
print()

c = Calendar()

for e in events:
    if len(events[e]["dates"]) == 1:
        event = Event()
        event.add('summary', events[e]["class name"] ) # event title

        start_date = ''
        end_date = ''
        d = ''

        start_date, end_date = events[e]["dates"][0].split(' - ')
        times = events[e]["times"][0].replace('Times: ', '').split(' to ')
        days = events[e]["days"][0].replace('Days: ', '').split(' ')
        first_day = day_of_week(days[0].lower())

        # Parse the start date
        parsed_start_date = datetime.strptime(start_date, "%m/%d/%Y")
        # Check the weekday: Monday=0, Sunday=6
        weekday = parsed_start_date.weekday()
        # Adjust the start date
        if weekday != first_day:
            days_to_add = (first_day - weekday) % 7
            parsed_start_date = parsed_start_date + timedelta(days=days_to_add)
        start_date = parsed_start_date.strftime("%m/%d/%Y")

        # Now use the adjusted start date for your event
        s_d = start_date +  ' ' + times[0]
        e_d = start_date +  ' ' + times[1]

        s_d = datetime.strptime(s_d, "%m/%d/%Y %I:%M%p")
        e_d = datetime.strptime(e_d, "%m/%d/%Y %I:%M%p")
        timezone = pytz.timezone("America/New_York")
        s_d = timezone.localize(s_d)
        e_d = timezone.localize(e_d)
        event.add('dtstart', s_d)
        event.add('dtend', e_d)

        for day in days:
            abbrev = day.upper()
            abbrev = abbrev[:2]
            d = d + abbrev + ','

        d = d[:-1]

        parsed_end_date = datetime.strptime(end_date, "%m/%d/%Y")
        # Add one day to the parsed date
        new_end_date = parsed_end_date + timedelta(days=1)
        # Format the new end date as required for the UNTIL field (YYYYMMDD)
        d_e = new_end_date.strftime("%Y%m%d")

        recurrence_rule_str = f'FREQ=WEEKLY;BYDAY={d};UNTIL={d_e}T000000Z'
        recurrence_rule = vRecur.from_ical(recurrence_rule_str)

        event.add('rrule', recurrence_rule)
        event.add('description', events[e]["location"])
        c.add_component(event)
    elif len(events[e]["dates"]) > 1:
        title = events[e]["class name"] # event title
        local = events[e]["location"]

        dates = events[e]["dates"]
        days = events[e]["days"]
        times = events[e]["times"]

        for index in range(len(dates)):
            event = Event()
            event.add('summary', title)

            start_date = ''
            end_date = ''

            start_date, end_date = dates[index].split(' - ')
            e_times = times[index].replace('Times: ', '').split(' to ')

            if e_times[0] == 'To be Announced': # all day event
                s_d = datetime.strptime(start_date, "%m/%d/%Y")
                e_d = datetime.strptime(end_date, "%m/%d/%Y")
            else:
                s_d = start_date +  ' ' + e_times[0]
                e_d = end_date +  ' ' + e_times[1]

                s_d = datetime.strptime(s_d, "%m/%d/%Y %I:%M%p")
                e_d = datetime.strptime(e_d, "%m/%d/%Y %I:%M%p")
                timezone = pytz.timezone("America/New_York")
                s_d = timezone.localize(s_d)
                e_d = timezone.localize(e_d)

            event.add('dtstart', s_d)
            event.add('dtend', e_d)
            event.add('description', local)

            c.add_component(event)

with open('/Users/veronikak/Documents/Side Projects/Calendar/my_cal.ics', 'wb') as f:
    f.write(c.to_ical())
