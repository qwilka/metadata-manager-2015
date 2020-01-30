"""
Copyright © 2020 Stephen McEntee
Licensed under the MIT license. 
See LICENSE file for details https://github.com/qwilka/metadata-manager-2015/blob/master/LICENSE
"""
import calendar
import datetime
import time


def make_timestamp(timestring=None, formatstring='%Y-%m-%dT%H:%M:%SZ', truncate=True):
    """Return a POSIX timestamp. (Default, return timestamp for current time).
    
    :param timestring: string specifying date and time in UTC
    :param formatstring: string specifying format for timestring (default ISO 8601)
    :param truncate: if True, truncate timestamp to second
    :returns: POSIX timestamp as int (truncate=True), or float (truncate=False)
    
    Examples:
    >>> make_timestamp('2013-06-05T15:19:10Z')
    1370445550
    >>> make_timestamp('04/01/2008 08:29:55', '%d/%m/%Y %H:%M:%S')
    1199435395
    >>> make_timestamp()
    144...
    """
    # http://www.avilpage.com/2014/11/python-unix-timestamp-utc-and-their.html
    if timestring:
        timestamp = calendar.timegm( time.strptime(timestring, formatstring) )
    else:
        try:
            timestamp = datetime.datetime.utcnow().timestamp()
        except AttributeError:
            timestamp = time.time()  # WARNING: time.time() is UTC+1 (Ireland, 2015-09-03)
    if truncate:
        timestamp = int( timestamp )
    return timestamp


def timestamp_to_timestring(timestamp, formatstring='%Y-%m-%dT%H:%M:%SZ'):
    """Return a date and time string from a POSIX timestamp.
    
    :param timestamp: POSIX timestamp
    :param formatstring: string specifying format for timestring (default ISO 8601)
    :returns: date and time string in UTC

    Examples:
    >>> timestamp_to_timestring(1009931465, '%d/%m/%Y %H:%M:%S')
    '02/01/2002 00:31:05'
    >>> timestamp_to_timestring(810637651)
    '1995-09-09T09:07:31Z'
    """
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return dt.strftime(formatstring)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True, optionflags=doctest.ELLIPSIS) # optionflags=(doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    print("time.time() - datetime.datetime.utcnow().timestamp()=\n", time.time() - datetime.datetime.utcnow().timestamp())
