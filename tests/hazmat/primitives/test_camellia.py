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

from __future__ import absolute_import, division, print_function

import binascii
import os

import pytest

from cryptography.hazmat.primitives.ciphers import algorithms, modes

from .utils import generate_encrypt_test
from ...utils import (
    load_cryptrec_vectors, load_nist_vectors
)


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.Camellia("\x00" * 16), modes.ECB()
    ),
    skip_message="Does not support Camellia ECB",
)
@pytest.mark.cipher
class TestCamelliaModeECB(object):
    test_ECB = generate_encrypt_test(
        load_cryptrec_vectors,
        os.path.join("ciphers", "Camellia"),
        [
            "camellia-128-ecb.txt",
            "camellia-192-ecb.txt",
            "camellia-256-ecb.txt"
        ],
        lambda key, **kwargs: algorithms.Camellia(binascii.unhexlify(key)),
        lambda **kwargs: modes.ECB(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.Camellia("\x00" * 16), modes.CBC("\x00" * 16)
    ),
    skip_message="Does not support Camellia CBC",
)
@pytest.mark.cipher
class TestCamelliaModeCBC(object):
    test_CBC = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "Camellia"),
        ["camellia-cbc.txt"],
        lambda key, **kwargs: algorithms.Camellia(binascii.unhexlify(key)),
        lambda iv, **kwargs: modes.CBC(binascii.unhexlify(iv)),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.Camellia("\x00" * 16), modes.OFB("\x00" * 16)
    ),
    skip_message="Does not support Camellia OFB",
)
@pytest.mark.cipher
class TestCamelliaModeOFB(object):
    test_OFB = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "Camellia"),
        ["camellia-ofb.txt"],
        lambda key, **kwargs: algorithms.Camellia(binascii.unhexlify(key)),
        lambda iv, **kwargs: modes.OFB(binascii.unhexlify(iv)),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.cipher_supported(
        algorithms.Camellia("\x00" * 16), modes.CFB("\x00" * 16)
    ),
    skip_message="Does not support Camellia CFB",
)
@pytest.mark.cipher
class TestCamelliaModeCFB(object):
    test_CFB = generate_encrypt_test(
        load_nist_vectors,
        os.path.join("ciphers", "Camellia"),
        ["camellia-cfb.txt"],
        lambda key, **kwargs: algorithms.Camellia(binascii.unhexlify(key)),
        lambda iv, **kwargs: modes.CFB(binascii.unhexlify(iv)),
    )
