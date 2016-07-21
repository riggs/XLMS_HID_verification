from construct import (
    Construct, GreedyRange, Struct, Byte, BitStruct, Padding, Flag, PascalString, Array, BitField,
    Enum,
)

__author__ = "riggs"


class Print_Context(Construct):
    def _parse(self, stream, context):
        print context


def hex_parser(bytes):
    return " ".join('0x' + '%02x'.upper() % ord(b) for b in bytes)


class Report(object):
    class Types(object):
        def __init__(self, set_feature=False, get_feature=False, output=False, input=False):
            self.set_feature = set_feature
            self.get_feature = get_feature
            self.output = output
            self.input = input

        def __str__(self):
            return ", ".join([name for (name, value) in
                     [('Set Feature', self.set_feature), ('Get Feature', self.get_feature),
                      ('Output', self.output), ('Input', self.input)] if value])

    class Serialization(object):
        def __init__(self, type, length):
            assert type in ("utf_8", "Uint", "Int", "Float")
            self.type = type
            if type == "utf_8":
                self.length = length
            else:
                assert length % 8 == 0
                self.length = length / 8

        def __repr__(self):
            return ''.join([self.type, '*'+str(self.length) if self.type is "utf_8" else str(self.length * 8)])

    def __init__(self, ID, types, name, serialization, length=None):
        self.ID = ID
        self.types = types
        self.name = name
        self.serialization = serialization
        self.length = length if length else 4 + len(name) + len(serialization)

    def __str__(self):
        return "Report<ID: {ID}, {types}, '{name}', {serialization}>".format(**self.__dict__)


data_structure = GreedyRange(
    Struct(
        "report",
        Byte("length"),
        Byte("ID"),
        BitStruct("types",
            Padding(4),
            Flag("set_feature"),
            Flag("get_feature"),
            Flag("output"),
            Flag("input")
        ),
        PascalString("name", length_field=Byte("length"), encoding="utf8"),
        Array(lambda ctx: ctx.length - (len(ctx.name) + 1) - 3,
              BitStruct("serialization",
                        BitField("length", 6),
                        Enum(BitField("type", 2),
                             utf_8=0,
                             Uint=1,
                             Int=2,
                             Float=3,
                             )
                        )
              ),
    )
)


def hexstring_to_bytearray(string):
    return bytearray([int(pair, 16) for pair in string.split(" ")])


def serialize(data):
    return data_structure.build(data)


def deserialize(_bytes):
    if isinstance(_bytes, str):
        _bytes = hexstring_to_bytearray(_bytes)

    return data_structure.parse(_bytes)


def magic_numbers(*reports):
    return ', '.join(hex_parser(serialize(reports)).split())
