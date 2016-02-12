
from construct import *


data_structure = GreedyRange(
    Struct(
        "report",
        Byte("length"),
        Byte("ID"),
        BitStruct(
            Padding(4),
            Flag("set_feature"),
            Flag("get_feature"),
            Flag("output"),
            Flag("input")
        ),
        PascalString("name", length_field=Byte("length"), encoding="utf8"),
        Array(lambda ctx: ctx.length - (ctx.name.length + 1) - 3, BitStruct(
            BitField("length", 6),
            Enum(BitField("type", 2),
                 utf8 = 0,
                 Int = 1,
                 Uint = 2,
                 Float = 4
        )))
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
