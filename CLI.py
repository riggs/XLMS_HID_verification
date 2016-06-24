from __future__ import absolute_import

import sys

from XLMS_HID import *

admin = Report(ID=1, types=Report.Types(get_feature=True), name=u'admin',
               serialization=[Report.Serialization(type='Int', length=1) for _ in range(4)] +
                             [Report.Serialization(type='utf_8', length=5)])

timestamp = Report(ID=4, types=Report.Types(get_feature=True, set_feature=True), name=u'timestamp',
                   serialization=[Report.Serialization(type='Uint', length=64 / 8)])

timeout = Report(ID=5, types=Report.Types(get_feature=True, set_feature=True), name=u'timeout',
                 serialization=[Report.Serialization(type='Uint', length=32 / 8)])

events = Report(ID=6, types=Report.Types(input=True), name=u'events',
                serialization=[Report.Serialization(type='Uint', length=64 / 8),
                               Report.Serialization(type='Int', length=1)])

errors = Report(ID=7, types=Report.Types(input=True), name=u'errors',
                serialization=[Report.Serialization(type='Uint', length=64 / 8),
                               Report.Serialization(type='Int', length=1)])


if __name__ == "__main__":
    from XLMS_HID.tests import passed
    print("Tests passed: " + str(passed))

    print(hex_parser(serialize([admin, timestamp, timeout, events, errors])))

    sys.exit()
