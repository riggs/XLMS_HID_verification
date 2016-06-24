from __future__ import absolute_import

from .XLMS_HID import Report, hex_parser, serialize, deserialize

__author__ = "riggs"

__exports__ = ("passed",)


admin = Report(ID=1, types=Report.Types(get_feature=True), name=u'admin',
               serialization=[Report.Serialization(type='Int', length=1) for _ in range(4)] +
                             [Report.Serialization(type='utf_8', length=5)])
admin_hex = "0x0E 0x01 0x04 0x05 0x61 0x64 0x6D 0x69 0x6E 0x05 0x05 0x05 0x05 0x14"

set_time = Report(ID=1, types=Report.Types(output=True), name=u'set_time',
                  serialization=[Report.Serialization(type='Uint', length=64/8)])
set_time_hex = "0x0D 0x01 0x02 0x08 0x73 0x65 0x74 0x5F 0x74 0x69 0x6D 0x65 0x22"

module_name = Report(ID=2, name=u'module_name', types=Report.Types(get_feature=True),
                     serialization=[Report.Serialization(type='utf_8', length=len('rugged_arm'))])
module_name_hex = "0x10 0x02 0x04 0x0B 0x6D 0x6F 0x64 0x75 0x6C 0x65 0x5F 0x6E 0x61 0x6D 0x65 0x28"

heart_rate = Report(ID=13, name="HEART_RATE", types=Report.Types(output=True),
                    serialization=[Report.Serialization(type="Float", length=32/8)])
heart_rate_hex = "0x0F 0x0D 0x02 0x0A 0x48 0x45 0x41 0x52 0x54 0x5F 0x52 0x41 0x54 0x45 0x13"

cases = {
    admin_hex: admin,
    set_time_hex: set_time,
    module_name_hex: module_name,
    heart_rate_hex: heart_rate
}

for hex, obj in cases.items():
    assert hex_parser(serialize([obj])) == hex
    assert hex_parser(serialize(deserialize(hex))) == hex

assert hex_parser(serialize([admin, set_time, module_name, heart_rate])) == \
    " ".join([admin_hex, set_time_hex, module_name_hex, heart_rate_hex])

passed = True
