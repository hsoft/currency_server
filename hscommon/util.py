# Created By: Virgil Dupras
# Created On: 2011-01-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import os
import os.path as op
import re
from math import ceil

from . import io
from .path import Path

def nonone(value, replace_value):
    ''' Returns value if value is not None. Returns replace_value otherwise.
    '''
    if value is None:
        return replace_value
    else:
        return value

def tryint(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def minmax(value, min_value, max_value):
    """Returns `value` or one of the min/max bounds if `value` is not between them.
    """
    return min(max(value, min_value), max_value)

#--- Sequence related

def dedupe(iterable):
    '''Returns a list of elements in iterable with all dupes removed.
    '''
    result = []
    seen = {}
    for item in iterable:
        if item in seen:
            continue
        seen[item] = 1
        result.append(item)
    return result

def flatten(iterables, start_with=None):
    '''Takes a list of lists 'lists' and returns a list containing elements of every list.
    
    If start_with is not None, the result will start with start_with items, exactly as if
    start_with would be the first item of lists.
    '''
    result = []
    if start_with:
        result.extend(start_with)
    for iterable in iterables:
        result.extend(iterable)
    return result

def first(iterable):
    """Returns the first item of 'iterable'
    """
    try:
        return next(iter(iterable))
    except StopIteration:
        return None

def stripfalse(seq):
    """Returns a sequence with all false elements stripped out of seq.
    """
    return [x for x in seq if x]

def extract(predicate, iterable):
    """Separates the wheat from the shaft (`predicate` defines what's the wheat), and returns both.
    """
    wheat = []
    shaft = []
    for item in iterable:
        if predicate(item):
            wheat.append(item)
        else:
            shaft.append(item)
    return wheat, shaft

def allsame(iterable):
    """Returns whether all elements of 'iterable' are the same.
    """
    it = iter(iterable)
    try:
        first_item = next(it)
    except StopIteration:
        raise ValueError("iterable cannot be empty")
    return all(element == first_item for element in it)

#--- String related

def escape(s, to_escape, escape_with='\\'):
    return ''.join((escape_with + c if c in to_escape else c) for c in s)

def get_file_ext(filename):
    """Returns the lowercase extension part of filename, without the dot."""
    pos = filename.rfind('.')
    if pos > -1:
        return filename[pos + 1:].lower()
    else:
        return ''

def rem_file_ext(filename):
    """Returns the filename without extension."""
    pos = filename.rfind('.')
    if pos > -1:
        return filename[:pos]
    else:
        return filename

def pluralize(number, word, decimals=0, plural_word=None):
    """Returns a string with number in front of s, and adds a 's' to s if number > 1
    
    number: The number to go in front of s
    word: The word to go after number
    decimals: The number of digits after the dot
    plural_word: If the plural rule for word is more complex than adding a 's', specify a plural
    """
    number = round(number, decimals)
    format = "%%1.%df %%s" % decimals
    if number > 1:
        if plural_word is None:
            word += 's'
        else:
            word = plural_word
    return format % (number, word)

def format_time(seconds, with_hours=True):
    """Transforms seconds in a hh:mm:ss string.
    
    If `with_hours` if false, the format is mm:ss.
    """
    minus = seconds < 0
    if minus:
        seconds *= -1
    m, s = divmod(seconds, 60)
    if with_hours:
        h, m = divmod(m, 60)
        r = '%02d:%02d:%02d' % (h, m, s)
    else:
        r = '%02d:%02d' % (m,s)
    if minus:
        return '-' + r
    else:
        return r

def format_time_decimal(seconds):
    """Transforms seconds in a strings like '3.4 minutes'"""
    minus = seconds < 0
    if minus:
        seconds *= -1
    if seconds < 60:
        r = pluralize(seconds, 'second', 1)
    elif seconds < 3600:
        r = pluralize(seconds / 60.0, 'minute', 1)
    elif seconds < 86400:
        r = pluralize(seconds / 3600.0, 'hour', 1)
    else:
        r = pluralize(seconds / 86400.0, 'day', 1)
    if minus:
        return '-' + r
    else:
        return r

SIZE_DESC = ('B','KB','MB','GB','TB','PB','EB','ZB','YB')
SIZE_VALS = tuple(1024 ** i for i in range(1,9))
def format_size(size, decimal=0, forcepower=-1, showdesc=True):
    """Transform a byte count in a formatted string (KB, MB etc..).
    
    size is the number of bytes to format.
    decimal is the number digits after the dot.
    forcepower is the desired suffix. 0 is B, 1 is KB, 2 is MB etc.. if kept at -1, the suffix will
    be automatically chosen (so the resulting number is always below 1024).
    if showdesc is True, the suffix will be shown after the number.
    """
    if forcepower < 0:
        i = 0
        while size >= SIZE_VALS[i]:
            i += 1
    else:
        i = forcepower
    if i > 0:
        div = SIZE_VALS[i-1]
    else:
        div = 1
    format = '%%%d.%df' % (decimal,decimal)
    negative = size < 0
    divided_size = ((0.0 + abs(size)) / div)
    if decimal == 0:
        divided_size = ceil(divided_size)
    else:
        divided_size = ceil(divided_size * (10 ** decimal)) / (10 ** decimal)
    if negative:
        divided_size *= -1
    result = format % divided_size
    if showdesc:
        result += ' ' + SIZE_DESC[i]
    return result

_valid_xml_range = '\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD'
if sys.maxunicode > 0x10000:
    _valid_xml_range += '%s-%s' % (chr(0x10000), chr(min(sys.maxunicode, 0x10FFFF)))
RE_INVALID_XML_SUB = re.compile('[^%s]' % _valid_xml_range, re.U).sub

def remove_invalid_xml(s, replace_with=' '):
    return RE_INVALID_XML_SUB(replace_with, s)

def multi_replace(s, replace_from, replace_to=''):
    """A function like str.replace() with multiple replacements.

    replace_from is a list of things you want to replace. Ex: ['a','bc','d']
    replace_to is a list of what you want to replace to.
    If replace_to is a list and has the same length as replace_from, replace_from
    items will be translated to corresponding replace_to. A replace_to list must
    have the same length as replace_from
    If replace_to is a basestring, all replace_from occurence will be replaced
    by that string.
    replace_from can also be a str. If it is, every char in it will be translated
    as if replace_from would be a list of chars. If replace_to is a str and has
    the same length as replace_from, it will be transformed into a list.
    """
    if isinstance(replace_to, str) and (len(replace_from) != len(replace_to)):
        replace_to = [replace_to for r in replace_from]
    if len(replace_from) != len(replace_to):
        raise ValueError('len(replace_from) must be equal to len(replace_to)')
    replace = list(zip(replace_from, replace_to))
    for r_from, r_to in [r for r in replace if r[0] in s]:
        s = s.replace(r_from, r_to)
    return s

#--- Files related

def modified_after(first_path, second_path):
    """Returns True if first_path's mtime is higher than second_path's mtime."""
    try:
        first_mtime = io.stat(first_path).st_mtime
    except EnvironmentError:
        return False
    try:
        second_mtime = io.stat(second_path).st_mtime
    except EnvironmentError:
        return True
    return first_mtime > second_mtime

def find_in_path(name, paths=None):
    """Search for `name` in all directories of `paths` and return the absolute path of the first
    occurrence. If `paths` is None, $PATH is used.
    """
    if paths is None:
        paths = os.environ['PATH']
    if isinstance(paths, str): # if it's not a string, it's already a list
        paths = paths.split(os.pathsep)
    for path in paths:
        if op.exists(op.join(path, name)):
            return op.join(path, name)
    return None

@io.log_io_error
def delete_if_empty(path, files_to_delete=[]):
    ''' Deletes the directory at 'path' if it is empty or if it only contains files_to_delete.
    '''
    if not io.exists(path) or not io.isdir(path):
        return
    contents = io.listdir(path)
    if any(name for name in contents if (name not in files_to_delete) or io.isdir(path + name)):
        return False
    for name in contents:
        io.remove(path + name)
    io.rmdir(path)
    return True

def open_if_filename(infile, mode='rb'):
    """
    infile can be either a string or a file-like object.
    if it is a string, a file will be opened with mode.
    Returns a tuple (shouldbeclosed,infile) infile is a file object
    """
    if isinstance(infile, Path):
        return (io.open(infile, mode), True)
    if isinstance(infile, str):
        return (open(infile, mode), True)
    else:
        return (infile, False)

class FileOrPath:
    def __init__(self, file_or_path, mode='rb'):
        self.file_or_path = file_or_path
        self.mode = mode
        self.mustclose = False
        self.fp = None
    
    def __enter__(self):
        self.fp, self.mustclose = open_if_filename(self.file_or_path, self.mode)
        return self.fp
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.fp and self.mustclose:
            self.fp.close()
    
