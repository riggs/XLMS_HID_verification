from construct import (
    Construct, OptionalGreedyRange, Struct, Byte, BitStruct, PascalString, Array, BitField,
    Enum, UBInt16, Const, FlagsEnum
)

__author__ = "riggs"


class Print_Context(Construct):
    def _parse(self, stream, context):
        print context


def hex_parser(_bytes):
    return ", ".join('0x' + '%02x'.upper() % ord(b) for b in _bytes)


Feature = {'feature': True}
Output = {'output': True}
Input = {'input': True}


class Report(object):
    class Types(int):
        def __new__(cls, feature=False, output=False, input=False):
            value = sum([value for key, value in {feature: 4, output: 2, input: 1}.items() if key])
            obj = super(Report.Types, cls).__new__(cls, value)
            obj.value = value
            return obj

        def __init__(self, feature=False, output=False, input=False):
            super(Report.Types, self).__init__(self)
            self.feature = feature
            self.output = output
            self.input = input

        def __str__(self):
            return ", ".join([name for (name, value) in
                              [('Feature', self.feature), ('Output', self.output), ('Input', self.input)] if value])

    class Serialization(object):
        types = ("utf8", "Uint", "Int", "Float")

        def __init__(self, type, length):
            assert type in self.types
            self.type = type
            if type == "utf8":
                self.length = length
            else:
                assert length % 8 == 0
                self.length = length / 8

        def __repr__(self):
            return ''.join([self.type, ","+str(self.length) if self.type == "utf8" else str(self.length * 8)])

        def __eq__(self, other):
            return self.type == other.type and self.length == other.length

        @classmethod
        def parse(cls, string):
            results = []
            for byte in string.strip().split():
                for type in cls.types:
                    if type in byte:
                        size, count = byte.strip(type).strip(','), 1
                        if '*' in size:
                            size, count = size.split('*')
                        results.extend([cls(type, int(size))] * int(count))
            return results

    def __init__(self, ID, types, name, serialization):
        self.ID = ID
        if isinstance(types, dict):
            self.types = self.Types(**types)
        else:
            self.types = types
        self.name = name
        if isinstance(serialization, self.Serialization):
            serialization = [serialization]
        elif isinstance(serialization, str):
            serialization = self.Serialization.parse(serialization)
        self.serialization = serialization
        self.length = 5 + len(name) + len(serialization)

    def __str__(self):
        return "Report<ID: {ID}, {types}, '{name}', {serialization}>".format(**self.__dict__)

    def __eq__(self, other):
        return self.ID == other.ID and self.types == other.types and self.name == other.name and \
                self.name == other.name and self.length == other.length and \
               (self.version == other.version if hasattr(self, 'version') else True)


class Admin(Report):
    class Version(tuple):
        def __new__(cls, major, minor, patch):
            return super(Admin.Version, cls).__new__(cls, (major, minor, patch))

        def __init__(self, major, minor, patch):
            super(Admin.Version, self).__init__(self)
            self.major = major
            self.minor = minor
            self.patch = patch

    def __init__(self, *version):
        super(Admin, self).__init__(ID=1, types=Report.Types(feature=True), name='admin',
                                    serialization=[Report.Serialization(type='Uint', length=8)] * 3)
        if isinstance(version[0], self.Version):
            self.version = version
        else:
            self.version = self.Version(*version)

    def __str__(self):
        return "Admin<ID: {ID}, {types}, '{name}', Version: {version}>".format(**self.__dict__)


# These should really be combined into a single Sequence, but using Embed on a GreedyRange containing the second
# Struct, 'report', caused some type of error I wasn't able to chase down. Also, the 'types' byte must be a raw value
# (and, subsequently, Report.Types must subclass int) because of a bug between Const & FlagsEnum:
# https://github.com/construct/construct/issues/73

admin_report = Struct("admin",
                      Const(UBInt16("length"), 13),
                      Const(Byte("ID"), 1),
                      Const(Byte("types"), 4),
                      Const(PascalString("name", length_field=Byte("length"), encoding="utf8"), "admin"),
                      Struct("version",
                             Byte("major"),
                             Byte("minor"),
                             Byte("patch")
                             )
                      )

HID_report = OptionalGreedyRange(
    Struct("report",
           UBInt16("length"),
           Byte("ID"),
           FlagsEnum(Byte("types"),
                     feature=4,
                     output=2,
                     input=1
                     ),
           PascalString("name", length_field=Byte("length"), encoding="utf8"),
           Array(lambda ctx: ctx.length - (len(ctx.name) + 1) - 4,
                 BitStruct("serialization",
                           BitField("length", 6),
                           Enum(BitField("type", 2),
                                utf8=0,
                                Uint=1,
                                Int=2,
                                Float=3
                                )
                           )
                 )
           )
)


def hexstring_to_bytearray(string):
    return bytearray([int(pair.strip(','), 16) for pair in string.split(" ")])


def serialize(data):
    if hasattr(data[0], 'version'):
        return admin_report.build(data[0]) + HID_report.build(data[1:])
    return HID_report.build(data)


def deserialize(_bytes):
    if ' ' in _bytes:
        _bytes = hexstring_to_bytearray(_bytes)

    return HID_report.parse(_bytes)


def Magic_Numbers(*reports):
    return hex_parser(serialize(reports))
