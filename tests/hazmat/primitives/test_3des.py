# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test using the NIST Test Vectors
"""

from __future__ import absolute_import, division, print_function

import binascii
import os

import pytest

from cryptography.hazmat.primitives.ciphers import algorithms, modes

from .utils import generate_encrypt_test
from ...utils import load_nist_vectors


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.TripleDES("\x00" * 8), modes.CBC("\x00" * 8)
    ),
    skip_message="Does not support TripleDES CBC",
)
@pytest.mark.cipher
class TestTripleDESModeCBC(object):
    test_KAT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "CBC"),
        [
            "TCBCinvperm.rsp",
            "TCBCpermop.rsp",
            "TCBCsubtab.rsp",
            "TCBCvarkey.rsp",
            "TCBCvartext.rsp",
        ],
        lambda keys, **kwargs: algorithms.TripleDES(binascii.unhexlify(keys)),
        lambda iv, **kwargs: modes.CBC(binascii.unhexlify(iv)),
    )

    test_MMT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "CBC"),
        [
            "TCBCMMT1.rsp",
            "TCBCMMT2.rsp",
            "TCBCMMT3.rsp",
        ],
        lambda key1, key2, key3, **kwargs: algorithms.TripleDES(
            binascii.unhexlify(key1 + key2 + key3)
        ),
        lambda iv, **kwargs: modes.CBC(binascii.unhexlify(iv)),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.TripleDES("\x00" * 8), modes.OFB("\x00" * 8)
    ),
    skip_message="Does not support TripleDES OFB",
)
@pytest.mark.cipher
class TestTripleDESModeOFB(object):
    test_KAT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "OFB"),
        [
            "TOFBpermop.rsp",
            "TOFBsubtab.rsp",
            "TOFBvarkey.rsp",
            "TOFBvartext.rsp",
            "TOFBinvperm.rsp",
        ],
        lambda keys, **kwargs: algorithms.TripleDES(binascii.unhexlify(keys)),
        lambda iv, **kwargs: modes.OFB(binascii.unhexlify(iv)),
    )

    test_MMT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "OFB"),
        [
            "TOFBMMT1.rsp",
            "TOFBMMT2.rsp",
            "TOFBMMT3.rsp",
        ],
        lambda key1, key2, key3, **kwargs: algorithms.TripleDES(
            binascii.unhexlify(key1 + key2 + key3)
        ),
        lambda iv, **kwargs: modes.OFB(binascii.unhexlify(iv)),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.TripleDES("\x00" * 8), modes.CFB("\x00" * 8)
    ),
    skip_message="Does not support TripleDES CFB",
)
@pytest.mark.cipher
class TestTripleDESModeCFB(object):
    test_KAT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "CFB"),
        [
            "TCFB64invperm.rsp",
            "TCFB64permop.rsp",
            "TCFB64subtab.rsp",
            "TCFB64varkey.rsp",
            "TCFB64vartext.rsp",
        ],
        lambda keys, **kwargs: algorithms.TripleDES(binascii.unhexlify(keys)),
        lambda iv, **kwargs: modes.CFB(binascii.unhexlify(iv)),
    )

    test_MMT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "CFB"),
        [
            "TCFB64MMT1.rsp",
            "TCFB64MMT2.rsp",
            "TCFB64MMT3.rsp",
        ],
        lambda key1, key2, key3, **kwargs: algorithms.TripleDES(
            binascii.unhexlify(key1 + key2 + key3)
        ),
        lambda iv, **kwargs: modes.CFB(binascii.unhexlify(iv)),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.TripleDES("\x00" * 8), modes.CFB8("\x00" * 8)
    ),
    skip_message="Does not support TripleDES CFB8",
)
@pytest.mark.cipher
class TestTripleDESModeCFB8(object):
    test_KAT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "CFB"),
        [
            "TCFB8invperm.rsp",
            "TCFB8permop.rsp",
            "TCFB8subtab.rsp",
            "TCFB8varkey.rsp",
            "TCFB8vartext.rsp",
        ],
        lambda keys, **kwargs: algorithms.TripleDES(binascii.unhexlify(keys)),
        lambda iv, **kwargs: modes.CFB8(binascii.unhexlify(iv)),
    )

    test_MMT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "CFB"),
        [
            "TCFB8MMT1.rsp",
            "TCFB8MMT2.rsp",
            "TCFB8MMT3.rsp",
        ],
        lambda key1, key2, key3, **kwargs: algorithms.TripleDES(
            binascii.unhexlify(key1 + key2 + key3)
        ),
        lambda iv, **kwargs: modes.CFB8(binascii.unhexlify(iv)),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.TripleDES("\x00" * 8), modes.ECB()
    ),
    skip_message="Does not support TripleDES ECB",
)
@pytest.mark.cipher
class TestTripleDESModeECB(object):
    test_KAT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "ECB"),
        [
            "TECBinvperm.rsp",
            "TECBpermop.rsp",
            "TECBsubtab.rsp",
            "TECBvarkey.rsp",
            "TECBvartext.rsp",
        ],
        lambda keys, **kwargs: algorithms.TripleDES(binascii.unhexlify(keys)),
        lambda **kwargs: modes.ECB(),
    )

    test_MMT = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "3DES", "ECB"),
        [
            "TECBMMT1.rsp",
            "TECBMMT2.rsp",
            "TECBMMT3.rsp",
        ],
        lambda key1, key2, key3, **kwargs: algorithms.TripleDES(
            binascii.unhexlify(key1 + key2 + key3)
        ),
        lambda **kwargs: modes.ECB(),
    )
