# vi: ts=8 sts=4 sw=4 et
#
# support.py: test support for draco2.util
#
# This file is part of Draco2. Draco2 is free software and is made available
# under the MIT license. Consult the file "LICENSE" that is distributed
# together with this file for the exact licensing terms.
#
# Draco2 is copyright (c) 1999-2007 by the Draco2 authors. See the file
# "AUTHORS" for a complete overview.
#
# $Revision: 1187 $

import random


def inverse(s):
    inv = []
    for i in range(256):
        ch = chr(i)
        if ch not in s:
            inv.append(ch)
    return ''.join(inv)


class EncoderTest(object):

    RANDOM_TESTS = 10
    RANDOM_SIZE = 1024

    def setup_class(cls):
        random.seed()

    def random_data(self, size):
        d = []
        for i in range(size):
            d.append(chr(random.randrange(128)))
        return ''.join(d)

    def test_encode(self):
        for data,encoded in self.encode_vectors:
            assert self.quote(data) == encoded

    def test_decode(self):
        for data,decoded in self.decode_vectors:
            assert self.unquote(data) == decoded

    def test_random(self):
        for i in range(self.RANDOM_TESTS):
            size = random.randrange(self.RANDOM_SIZE)
            data = self.random_data(size)
            encoded = self.quote(data)
            decoded = self.unquote(encoded)
            assert data == decoded
            assert size <= len(encoded)
            for ch in self.unsafe:
                if ch in self.quotechars:
                    continue  # don't test for quoting character
                assert ch not in encoded
