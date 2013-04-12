#!/usr/bin/env python
"""This script posts a timesheet to FogBugz.

The program takes no arguments or options. It takes it's configuration from
~/.timetoughrc, which is in INI format with one section and four keys:

    [main]
    url=https://example.fogbugz.com/api.asp
    username=your name
    password=secr3t
    timesheet=~/.timesheet
    timezone=US/Eastern


It needs pytz:

    http://pytz.sourceforge.net/


Timetough accounts for:

    o estimates (it prompts you to add/update estimates for relevant cases)
    o closed cases (it reopens, posts, and resolves/closes them again)
    o conflicting time intervals (you must resolve these manually)


The timesheet format that timetough is designed to work with is as follows:

    ---===START===---

    03/17/2009
    09:33   101 12:00
    12:00   42  13:30

    ---===END===---
    
    03/18/2009
    08:30  101  11:13
    11:13   42  11:58
    13:00   42  15:33


Only the lines between the START and END markers are processed. Allowable lines
between these markers are of three types:

    o blank lines
    o dates in MM/DD/YYYY format
    o entries in <start-time> <case-number> <end-time> format; 24 hour clock,
      and must be preceded by a date line


TODO:

    - test!
    - document!
    - how about the rest of a time line is posted as a comment on the case?
    ===done===
    - account for timezone
    - account for overlapping entries
        - figure out minute boundary overlaps for sure (ok in FB ui?)
        - parse overlaps on client rather than hitting server N times
    - clear out old data in FB


The name comes from:

    http://songza.com/z/mgj2hg


Legal (MIT License; http://www.opensource.org/licenses/mit-license.php):

    Copyright (c) 2009 Zeta Design & Development, LLC

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.


"""
import ConfigParser
import datetime
import os
import re
import stat
import sys
import time
import urllib
import urllib2
from xml.etree import ElementTree


CONF = '~/.timetoughrc'
START = '---===START===---'
END = '---===END===---'


# Helpers
# =======

def die(msg):
    print >> sys.stderr, msg
    raise SystemExit(1)

def w(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def retry(m):
    for i in range(3,0,-1):
        if i == 1:
            w('\r%s Retry in 1 second.     ' % m)
        else:
            w('\r%s Retry in %d seconds.   ' % (m, i))
        time.sleep(1)
    w('\r')

class step(object):
    _step = 0
    def __call__(self, name):
        self._step += 1
        line = " STEP %d: %s " % (self._step, name)
        line = line.center(45, '=')
        line = line.center(60, '-')
        line = line.center(79, ' ')
        print
        print
        print
        print line
        print
step = step()


# Import pytz
# ===========
# This is here so we have die().

try:
    import pytz
except ImportError:
    die("This program depends on pytz: http://pytz.sourceforge.net/")


# XML API
# =======

class XMElement(object):
    """Wrap the ElementTree API.
    """

    def __init__(self, etree):
        if isinstance(etree, basestring):
            etree = ElementTree.fromstring(etree)
        self.__etree = etree
        self._tag = self.__etree.tag
        self.__encoding = 'UTF-8' # @@: this could be smarter

    def __getitem__(self, name):
        """Dictionary access for element attributes.
        """
        return self.__etree.attrib[name]

    def keys(self):
        return self.__etree.keys()
    
    def __getattr__(self, name):
        """Attribute access for subelements.
        """
        val = self.__etree.find(name)
        if val is None:
            raise AttributeError( "'%s' object has no attribute '%s'" 
                                % (self.__class__.__name__, name)
                                 )
        else:
            return XMElement(val) # recurse

    def __hasattr__(self, name):
        try:
            val = getattr(self, name)
            return True
        except AttributeError:
            return False

    def __iter__(self):
        """Iterator access for children.
        """
        for child in self.__etree.getchildren():
            yield XMElement(child)

    def __str__(self):
        """String access for text.
        """
        str = self.__etree.text
        if str is None:
            str = ''
        return str.decode(self.__encoding)

    def __repr__(self):
        return '<XMElement: %s>' % self.__etree.tag

    def _raw(self):
        return ElementTree.tostring(self.__etree, self.__encoding)


# FogBugz API
# ===========
# See Also:
# 
#   - http://our.fogbugz.com/default.asp?W1048
#   - http://paltman.com/2009/jan/09/wrapping-fogbugz-with-python/
#   - http://code.google.com/p/fogbugz-python/

class FogBugzError(StandardError):
    
    def __init__(self, error):
        StandardError.__init__(self)
        self.xml = error
        self.code = int(error['code'])
        self.text = unicode(error)

    def __str__(self):
        return "%s [%s]" % (self.text, self.code)


class FogBugzResponse(XMElement):

    def __init__(self, url, kw):
        # AttributeError here triggers infinite loop in XMElement.__getattr__
        self.__data = urllib.urlencode(kw)              # POST body
        self.__fp = urllib.urlopen(url, self.__data)    # file-like object
        self.__body = self.__fp.read()                  # response body
        XMElement.__init__(self, self.__body)           # XML API
         # bad URL will (probably) trigger failure to parse XML here
        if hasattr(self, 'error'):
            raise FogBugzError(self.error)


class FogBugz(object):
    """Model a FogBugz instance.
    """

    def __init__(self, url, username, password):
        """Logon.
        """
        self.url = url                      # needed for logon
        response = self.logon(email=username, password=password)
        self.token = str(response.token)    # needed for later calls


    # Make the FogBugz API Pythonic
    # =============================
    # Calling any function on this object will translate into a call to the 
    # underlying FogBugz API, using the name of the method called as the cmd
    # attribute to pass to FogBugz. Keyword arguments to the method become the
    # remaining parameters passed.

    def __call__(self, **kw):
        if kw['cmd'] != 'logon':
            kw['token'] = self.token
        return FogBugzResponse(self.url, kw) # may raise FogBugzError

    def __getattr__(self, name):
        def func(**kw): # FogBugz's version caches these
            kw['cmd'] = name
            return self(**kw)
        return func


# The Thing Itself
# ================

utc = pytz.timezone('UTC')

class Interval(object):

    def __init__(self, case, start, end, date=None):
        """Takes three strings and a datetime.datetime object.

        Or take an int and two datetime objects.

        """
        self.case = int(case)

        if isinstance(start, basestring):
            parse_time = lambda t: [int(x) for x in t.split(':')]
            def make_time(h, m):
                dt = datetime.datetime(date.year, date.month, date.day, h, m)
                dt = timezone.localize(dt)
                dt = dt.astimezone(utc)
                return dt
    
            start_h, start_m = parse_time(start)
            end_h, end_m = parse_time(end)
    
            start = make_time(start_h, start_m)
            if end_h < start_h: # somebody's working late ;^)
                date += datetime.timedelta(days=1)
            end = make_time(end_h, end_m)

        self.start = start
        self.end = end

    def __cmp__(self, other):
        return cmp(self.start, other.start)
    
    def __repr__(self):
        return "<%2.2f hrs on %d>" % (self.to_hours(), self.case)

    def to_hours(self):
        return (self.end - self.start).seconds / 60.0 / 60.0


def process(fogbugz, timesheet):
    """Given a FogBugz object, process a timesheet.

    We want to be careful not to duplicate intervals. So first we batch all
    intervals by day, and ask the user for confirmation if they already have 
    any intervals posted for that day. Then check each interval for an interval
    matching the exact start and end times, and skip-and-warn those.

    """

    # Read in the timesheet.
    # ======================

    step('Read Timesheet')
    w("Reading timesheet ")

    timesheet = open(timesheet)
    for line in timesheet:  # skip down to start marker
        if line.strip() == START:
            break
    
    date = earliest = latest = None
    date_pattern = re.compile(r'^\d\d/\d\d/\d\d\d\d$')
    all = list()
    intervals = dict()
    elapsed = dict()
    
    for line in timesheet:
        line = line.strip()
        if not line:
            continue
    
        if line == END:     # break at end marker
            break
   

        # Process a date line.
        # ====================

        m = date_pattern.match(line)
        if m is not None:
            month, day, year = [int(x) for x in m.group(0).split('/')]
            date = datetime.date(year, month, day)
            continue
    

        # Process an interval line.
        # =========================

        if date is None:
            die("no date set")

        start, case_id, end = line.split()
        interval = Interval(case_id, start, end, date)
        all.append(interval)

        if (earliest is None) or (interval.start < earliest):
            earliest = interval.start
        if (latest is None) or (interval.end > latest):
            latest = interval.end
     

        # File for later.
        # ===============
        
        if interval.case in intervals:
            intervals[interval.case].append(interval)
        else:
            intervals[interval.case] = [interval]

        _elapsed = interval.to_hours()
        if interval.case in elapsed:
            elapsed[interval.case] += _elapsed
        else:
            elapsed[interval.case] = _elapsed

        w('.')

    all.sort() # start, ascending
    print " done"


    # Resolve conflicts.
    # ==================

    conflicts = list()
  
    step("Resolve Conflicts")
    w("Checking for conflicts ")

    response = fogbugz.listIntervals(dtStart=earliest, dtEnd=latest)
    existing = list()
    for interval in response.intervals:
        m = lambda d: datetime.datetime.strptime(str(d), "%Y-%m-%dT%H:%M:%SZ")
        s = utc.localize(m(interval.dtStart))
        e = utc.localize(m(interval.dtEnd))
        existing.append(Interval(str(interval.ixBug), s, e))


    class Conflict(Exception):
        pass

    def has_conflict(first):
        """Given an Interval return a boolean.
        
        Two temporal parts can relate in 13 ways; 9 are conflicts, so for 
        readability we structure our tests for non-conflict.

        """
        for second in existing:
            conflict = True
            if first.start < second.start:
                if first.end <= second.start:
                    conflict = False
            elif first.start > second.start:
                if first.start >= second.end:
                    conflict = False
            else:
                assert first.start == second.start # sanity check
                pass
            if conflict:
                return True
        return False


    for interval in all:
        if has_conflict(interval):
            w('x')
            conflicts.append(interval)
            intervals[interval.case].remove(interval)
            if not intervals[interval.case]:
                del intervals[interval.case]
            continue
        else:
            w('.')

    print " done"


    if conflicts:

        nconflicts = len(conflicts)
        nall = len(all)
        if nconflicts == nall:
            print
            print ("Your entire timesheet conflicts with already-posted work "
                   "intervals. Please\nresolve manually before re-running.")
            print
            sys.exit()

        print
        print ("Some of your timesheet entries conflict with already-posted "
               "work intervals:")
        print

        for interval in sorted(conflicts):
            w(interval.start.strftime("  %Y-%m-%d  %H:%M - "))
            w(interval.end.strftime("%H:%M "))
            w("% 4d" % interval.case)
            print

        print
        # We can't delete intervals using the API (version 5), so users have 
        # to manually resolve conflicts.
        nnon = nall - nconflicts
        if nnon == 1:
            prompt = ("Would you like to proceed with posting the 1 non-"
                      "conflicting entry? [Y/n] ")
        else:
            prompt = ("Would you like to proceed with posting the %d non-"
                      "conflicting entries? [Y/n] " % nnon)
        while 1:
            val = raw_input(prompt).lower()
            if val == 'n':
                print
                print "Exiting ..."
                print
                sys.exit()
            elif val in ('', 'y'):
                break


    # Update estimates for all cases in this timesheet.
    # =================================================
    # An estimate of 0.01 hours is used to signal that a case is perpetually
    # open for time to be billed against. FogBugz assumes that all cases are
    # part of a software ship schedule, so we have to hack this a bit.

    step("Update Estimates")
    cases = [str(i) for i in sorted(intervals.keys())]
    response = fogbugz.search( q=','.join(cases)
                             , cols=('ixBug,sProject,sTitle,hrsCurrEst,'
                                     'hrsElapsed,fOpen')
                              )
    ncases = response.cases['count']
    assert int(ncases) == len(cases) # sanity check

    if int(ncases) == 1:
        msg = "Please review and update the estimate for the following case."
    else:
        msg = "Please review and update estimates for the following %s cases."
        msg %= ncases

    print "+%s+" % ('-'*77)
    print '|%s|' % msg.center(77)
    print "+%s+" % ('-'*77)
    print ( "| case | estim |  new  | elaps |  new  | title [project] %s|" 
          % (" "*21)
           )
    print "+%s+" % ('-'*77)

    closed = list()

    for case in response.cases:
        if str(case.fOpen) == 'false':
            closed.append(case)

        curest = float(str(case.hrsCurrEst))
        while 1:
            prompt = '| % 4s |' % case.ixBug
            if curest == 0.01:
                prompt += '   -   | '
            else:
                prompt += ' %#5.2f | ' % curest


            # Output a line with info on this case.
            # =====================================

            w(prompt) # overwritten by raw_input below
            w('      |') # entry field
            w(' %#5.2f |' % float(str(case.hrsElapsed)))
            w(' %#5.2f |' % float(elapsed[int(str(case.ixBug))]))
            w(' %-36.36s |' % ('%s [%s]' % (case.sTitle, case.sProject)))
            w('\r')


            # Get and validate an estimate for this case.
            # ===========================================

            estimate = raw_input(prompt)
            if curest > 0 and not estimate:
                break # keep current estimate
            if estimate.strip() == '-':
                estimate = 0.01 # special case; means perpetual task

            try:
                estimate = float(estimate)
                assert estimate > 0
            except (ValueError, AssertionError):
                retry('Estimate must be a float greater than zero.')
            else:
                response = fogbugz.edit(ixBug=case.ixBug, hrsCurrEst=estimate)
                break
    
    print "+%s+" % ('-'*77)


    # Confirm posting for all closed cases.
    # =====================================
    # This block converts closed from a list of XMElements to a list of ints.

    if closed:
    
        step("Confirm Closed Cases")

        nclosed = len(closed)
        if nclosed == 1:
            msg = "Please confirm posting for the following closed case."
        else:
            msg = "Please confirm posting for the following %d closed cases."
            msg %= nclosed

        print "Thank you. %s" % msg
        print 

        _closed = list()
        for case in closed:
            case_id = int(str(case.ixBug))
            prompt = "%s [%s]" % (case.sTitle, case.sProject)
            prompt = "  % 4s | %-60.60s [Y/n] " % (case.ixBug, prompt)
            while 1:
                confirm = raw_input(prompt).lower()
                if confirm not in ('', 'y', 'n'):
                    retry("Please enter Y or N (default: Y)")
                elif confirm in ('', 'y'):
                    _closed.append(case_id)
                    break
                else:
                    del intervals[case_id]
                    break
        closed = _closed

        print


    # Post timesheet.
    # ===============

    step("Post Timesheet")
    print "Thank you. Proceeding to post timesheet ..."
    print

    to_post = sorted(intervals.items())
    if not to_post:
        print "  Nothing to post ..."
    else:
        for case_id, intervals in to_post:
            if case_id in closed:
                fogbugz.reopen(ixBug=case_id)
            w("  % 4d | " % case_id)
            for interval in intervals:
                assert case_id == interval.case # sanity check
                fogbugz.newInterval( ixBug=interval.case
                                   , dtStart=interval.start
                                   , dtEnd=interval.end
                                    )
                w(".")
            print
            if case_id in closed:
                fogbugz.resolve(ixBug=case_id)
                fogbugz.close(ixBug=case_id)
    print
    print "All done!"
    print


def main():
    global timezone


    # Find a secure conf file
    # =======================
    
    conf_path = os.path.expanduser(CONF)
    if not os.path.isfile(conf_path):
        die("you need a configuration file at %s" % CONF)
    
    perms = stat.S_IMODE(os.stat(conf_path)[stat.ST_MODE])
    if (perms ^ 0600) > 0:
        die("permissions on %s must be 0600, not 0%o" % (CONF, perms))
    
    
    # Load configuration
    # ==================
    
    conf = ConfigParser.RawConfigParser()
    conf.read([conf_path])
    url = conf.get('main', 'url')
    username = conf.get('main', 'username')
    password = conf.get('main', 'password')
    timesheet = os.path.expanduser(conf.get('main', 'timesheet'))
    try:
        _timezone = conf.get('main', 'timezone')
        timezone = pytz.timezone(_timezone)
    except pytz.UnknownTimeZoneError:
        die("unknown timezone: %s" % _timezone)
    
    
    # Log on and hand off
    # ===================
    
    try:
        fogbugz = FogBugz(url, username, password)
        process(fogbugz, timesheet)
    except FogBugzError, err:
        die(unicode(err))
    except KeyboardInterrupt:
        print


if __name__ == '__main__':
    main()

