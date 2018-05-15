"""
@author Simon Wu <swprojects@runbox.com>
Copyright (c) 2018 by Simon Wu <Zippy Ip Scanner>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>
"""


def decimal_to_byte_list(d, retbytes):
    if not isinstance(d, int):
        raise ValueError("arg d must be an integer")
    d = bin(d)[2:]
    value = [0] * retbytes
    n = -1
    while (d):
        v = d[-8:]
        v = int(v, 2)
        d = d[:-8]
        value[n] = v
        n -= 1
    return value


def byte_list_to_decimal(array):
    pwr = 0
    value = 0
    for byte in reversed(array):
        value += byte * (2**pwr)
        pwr += 8

    return value


if __name__ == "__main__":
    a = byte_list_to_decimal([255, 255])
    b = byte_list_to_decimal([0, 0])
    print(a - b)

    temp = decimal_to_byte_list(65535, retbytes=4)
    print(temp)

    temp = decimal_to_byte_list(255, retbytes=4)
    print(temp)
