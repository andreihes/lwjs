'''
Calculate date from the str expression (each arg concatenated as str).
Return final date as %Y-%m-%d str. Expression syntax is:
  expr = <when> <sign> <numb> <unit>
  when = %Y-%m-%d date str | "today" | "yesterday" | "tomorrow"
  sign = "+" | "-"
  numb = integer (0-...)
  unit = D: "d" | "day" | "days"
        W: "w" | "wk" | "week" | "weeks"
        M: "m" | "mon" | "month" | "months"
        Y: "y" | "yr" | "year" | "years"
All tokens can be surrounded (or not) by any number of whitespaces.
Defaults:
  when = today (local TZ)
  sign = +
  numb = 0
  unit = d
Thus, $(date) returns today's date (local TZ)
'''

import re
import datetime
import calendar

DAYS = ('d', 'day', 'days')
WEEK = ('w', 'wk', 'week', 'weeks')
MNTH = ('m', 'mon', 'month', 'months')
YEAR = ('y', 'yr', 'year', 'years')

# when: literal or %Y-%m-%d date
REXP = r'^\s*(today|yesterday|tomorrow|[0-9]{4}-[0-9]{2}-[0-9]{2})?'
# sign: + or -
REXP += r'\s*(\+|\-)?'
# numb: a sequence of digits
REXP += r'\s*([0-9]+)?'
# unit: day and week literals
REXP += r'\s*(' + '|'.join(DAYS + WEEK + MNTH + YEAR) + r')?\s*$'

def date(*args) -> str:
  args = ''.join([str(arg).lower() for arg in args])
  if not (grps := re.match(REXP, args)):
    raise ValueError(args)

  when = datetime.datetime.now()
  if grps[1]:
    if grps[1] == 'today':
      pass
    elif grps[1] == 'yesterday':
      when -= datetime.timedelta(days = 1)
    elif grps[1] == 'tomorrow':
      when += datetime.timedelta(days = 1)
    else:
      try:
        when = datetime.datetime.strptime(grps[1], '%Y-%m-%d')
      except Exception as e:
        raise ValueError(args) from e
      if when.strftime('%Y-%m-%d') != grps[1]:
        raise ValueError(args)

  sign = +1
  if grps[2] == '-':
    sign = -1

  numb = 0
  if grps[3]:
    try:
      numb = int(grps[3])
    except Exception as e:
      raise ValueError(args) from e

  unit = 'd'
  if grps[4]:
    unit = grps[4]

  if unit in DAYS:
    when = when + datetime.timedelta(days = sign * numb)
  elif unit in WEEK:
    when = when + datetime.timedelta(days = sign * numb * 7)
  elif unit in MNTH:
    y = when.year + (when.month - 1 + sign * numb) // 12
    m = (when.month - 1 + sign * numb) % 12 + 1
    d = min(when.day, calendar.monthrange(y, m)[1])
    when = datetime.datetime(y, m ,d)
  elif unit in YEAR:
    y = when.year + sign * numb
    m = when.month
    d = min(when.day, calendar.monthrange(y, m)[1])
    when = datetime.datetime(y, m ,d)

  return when.strftime('%Y-%m-%d')
