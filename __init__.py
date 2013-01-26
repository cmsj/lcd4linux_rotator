#!/usr/bin/python
"""
lcd4linux_rotator

This is a module for use with lcd4linux. It lets you rotate a label/widget pair
between several sets of values.

by Chris Jones <cmsj@tenshu.net>
Released under the GNU GPL v2 only.
All Rights Reserved.
"""
try:
    from lcd4linux_rotator import borg
except ImportError:
    import borg

class Rotator(borg.Borg):
    """
    This is a class for use with lcd4linux. Its task is simple.
    You want a Bar Widget to alternate between multiple sources
    of information (e.g. cycle through 5 disks to show their usage).

    To achieve this, you should call this plugin roughly in this
    fashion in your lcd4linux.conf:

        Widget LabelAllDisks {
            class 'Text'
            update 1000
            width 4
            expression python::exec('lcd4linux_rotator', 'main', 'AllDisks key root=/,md0=/data,home=/home)
        }
        Widget BarAllDisks {
            class 'Bar'
            update 1000
            length 16
            direction 'E'
            min 0
            max 100
            expression path=python::exec('lcd4linux_rotator', 'main', 'AllDisks value') ; ((statfs(path, 'blocks') - statfs(path, 'bavail')) / statfs(path, 'blocks'))*100
        }

    Now let's explain what that all meant.

    The first widget is a label that updates every 1000msec and gets its value
    from a python expression. That expression calls the "main" methid in this
    module ("lcd4linux_rotator") and passes in a string of data.

    The format of that string is: "NAME TYPE [KEY=VALUE,,,,]"

    NAME - The name of this instance of lcd4linux_rotator. You can have as many as
    you want, just use the same name in the label and bar, so the module knows
    which one you want.

    TYPE - This indicates to the module which type of widget you are. There are
    currently two types, 'key' and 'value'. If you're the 'key' kind, you
    will get the keys, if you are the 'value' kind you will get the values.

    KEY=VALUE - These are the keys and values mentioned previously. The key is
    the string to the left of the = and the value is the string to the right.


    So what will happen in this example is that each second, lcd4linux will
    update both of these widgets and the label will show "root" first, then
    "md0" a second later, then "home" a second later.
    Meanwhile the bar widget will represent the percentage of disk space used
    on "/" at first, then "/data" a second later, then "/home" a second later.
    """
    name = None
    keys = None
    values = None
    current_key = None
    
    def __init__(self):
        """Assimilate ourselves into the borg"""
        borg.Borg.__init__(self, self.__class__.__name__)

    def prepare_attributes(self, args):
        """As required by the Borg, we must initialise our instance variables
        on the first run. All subsequent runs will find this method does
        nothing"""
        if not self.name:
            self.name = args['name']

        if not self.keys and args['keys']:
            self.keys = args['keys']

        if not self.values and args['values']:
            self.values = args['values']

    def string(self, req):
        """Return the next required string, with the req argument indicating
        whether we are being asked for a key or a value"""
        if not self.current_key:
            self.current_key = self.get_key()
        if req == 'key':
            return self.current_key

        if req == 'value':
            val = self.get_value(self.current_key)
            self.current_key = None
            return val

    def get_key(self):
        """Get the next key. This will return the first value from self.keys
        and then move that value to the end of self.keys"""
        key = self.keys.pop(0)
        self.keys.append(key)
        return key

    def get_value(self, key):
        """Get a value for a key"""
        return self.values[key]

def process_args(args):
    """Receive the string passed from lcd4linux and break it into actual
    arguments we care about and can process.
    Reminder, the format for the args string is:
        NAME TYPE [KEY=VALUE,,,]
    """
    bits = {}
    sections = args.split(' ')
    bits['name'] = sections[0]
    bits['type'] = sections[1].lower()

    if len(sections) > 2:
        bits['keys'] = []
        bits['values'] = {}
        kvbits = sections[2].split(',')
        for keyval in kvbits:
            key, val = keyval.split('=')
            bits['keys'].append(key)
            bits['values'][key] = val
    else:
        bits['keys'] = None
        bits['values'] = None

    return bits

def main(textarg):
    """Simple function to process incoming args, instantiate the Rotator and
    fetch/return the appropriate string from it"""
    args = process_args(textarg) 
    rotator = Rotator()
    rotator.prepare_attributes(args)
    return rotator.string(args['type'])

if __name__ == "__main__":
    i = 0
    while i < 20:
        LABEL = main("Test key foo=bar,baz=bong,lol=omg")
        if i % 5 == 0:
            LABEL2 = main("Test key")
            print "Getting extra label: %s" % LABEL2
        VALUE = main("Test value")
        print "%s=%s" % (LABEL, VALUE)
        i += 1

