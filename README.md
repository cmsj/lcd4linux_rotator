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
(The bar widget is calling out to this module to get the path it should be 
checking, and then using lcd4linux's built in 'statfs' plugin to calculate the disk usage)
