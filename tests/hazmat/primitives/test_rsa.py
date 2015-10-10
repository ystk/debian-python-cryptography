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
import itertools
import math
import os

import pytest

from cryptography import utils
from cryptography.exceptions import (
    AlreadyFinalized, InvalidSignature, _Reasons
)
from cryptography.hazmat.primitives import hashes, interfaces
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers

from .fixtures_rsa import (
    RSA_KEY_1024, RSA_KEY_1025, RSA_KEY_1026, RSA_KEY_1027, RSA_KEY_1028,
    RSA_KEY_1029, RSA_KEY_1030, RSA_KEY_1031, RSA_KEY_1536, RSA_KEY_2048,
    RSA_KEY_512, RSA_KEY_512_ALT, RSA_KEY_522, RSA_KEY_599, RSA_KEY_745,
    RSA_KEY_768,
)
from .utils import (
    _check_rsa_private_numbers, generate_rsa_verification_test
)
from ...utils import (
    load_pkcs1_vectors, load_rsa_nist_vectors, load_vectors_from_file,
    raises_unsupported_algorithm
)


@utils.register_interface(interfaces.AsymmetricPadding)
class DummyPadding(object):
    name = "UNSUPPORTED-PADDING"


class DummyMGF(object):
    _salt_length = 0


def _flatten_pkcs1_examples(vectors):
    flattened_vectors = []
    for vector in vectors:
        examples = vector[0].pop("examples")
        for example in examples:
            merged_vector = (vector[0], vector[1], example)
            flattened_vectors.append(merged_vector)

    return flattened_vectors


def test_modular_inverse():
    p = int(
        "d1f9f6c09fd3d38987f7970247b85a6da84907753d42ec52bc23b745093f4fff5cff3"
        "617ce43d00121a9accc0051f519c76e08cf02fc18acfe4c9e6aea18da470a2b611d2e"
        "56a7b35caa2c0239bc041a53cc5875ca0b668ae6377d4b23e932d8c995fd1e58ecfd8"
        "c4b73259c0d8a54d691cca3f6fb85c8a5c1baf588e898d481", 16
    )
    q = int(
        "d1519255eb8f678c86cfd06802d1fbef8b664441ac46b73d33d13a8404580a33a8e74"
        "cb2ea2e2963125b3d454d7a922cef24dd13e55f989cbabf64255a736671f4629a47b5"
        "b2347cfcd669133088d1c159518531025297c2d67c9da856a12e80222cd03b4c6ec0f"
        "86c957cb7bb8de7a127b645ec9e820aa94581e4762e209f01", 16
    )
    assert rsa._modinv(q, p) == int(
        "0275e06afa722999315f8f322275483e15e2fb46d827b17800f99110b269a6732748f"
        "624a382fa2ed1ec68c99f7fc56fb60e76eea51614881f497ba7034c17dde955f92f15"
        "772f8b2b41f3e56d88b1e096cdd293eba4eae1e82db815e0fadea0c4ec971bc6fd875"
        "c20e67e48c31a611e98d32c6213ae4c4d7b53023b2f80c538", 16
    )


@pytest.mark.rsa
class TestRSA(object):
    @pytest.mark.parametrize(
        ("public_exponent", "key_size"),
        itertools.product(
            (3, 5, 65537),
            (1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1536, 2048)
        )
    )
    def test_generate_rsa_keys(self, backend, public_exponent, key_size):
        skey = rsa.generate_private_key(public_exponent, key_size, backend)
        assert skey.key_size == key_size

        if isinstance(skey, interfaces.RSAPrivateKeyWithNumbers):
            _check_rsa_private_numbers(skey.private_numbers())
            pkey = skey.public_key()
            assert isinstance(pkey.public_numbers(), rsa.RSAPublicNumbers)

    def test_generate_rsa_key_class_method(self, backend):
        skey = pytest.deprecated_call(
            rsa.RSAPrivateKey.generate,
            65537,
            512,
            backend
        )
        assert skey.key_size == 512
        assert skey.public_exponent == 65537

    def test_generate_bad_public_exponent(self, backend):
        with pytest.raises(ValueError):
            rsa.generate_private_key(public_exponent=1,
                                     key_size=2048,
                                     backend=backend)

        with pytest.raises(ValueError):
            rsa.generate_private_key(public_exponent=4,
                                     key_size=2048,
                                     backend=backend)

    def test_cant_generate_insecure_tiny_key(self, backend):
        with pytest.raises(ValueError):
            rsa.generate_private_key(public_exponent=65537,
                                     key_size=511,
                                     backend=backend)

        with pytest.raises(ValueError):
            rsa.generate_private_key(public_exponent=65537,
                                     key_size=256,
                                     backend=backend)

    @pytest.mark.parametrize(
        "pkcs1_example",
        load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs-1v2-1d2-vec", "pss-vect.txt"),
            load_pkcs1_vectors
        )
    )
    def test_load_pss_vect_example_keys(self, pkcs1_example):
        secret, public = pkcs1_example

        private_num = rsa.RSAPrivateNumbers(
            p=secret["p"],
            q=secret["q"],
            d=secret["private_exponent"],
            dmp1=secret["dmp1"],
            dmq1=secret["dmq1"],
            iqmp=secret["iqmp"],
            public_numbers=rsa.RSAPublicNumbers(
                e=secret["public_exponent"],
                n=secret["modulus"]
            )
        )
        _check_rsa_private_numbers(private_num)

        public_num = rsa.RSAPublicNumbers(
            e=public["public_exponent"],
            n=public["modulus"]
        )
        assert public_num

        public_num2 = private_num.public_numbers
        assert public_num2

        assert public_num.n == public_num2.n
        assert public_num.e == public_num2.e

    def test_invalid_private_key_argument_types(self):
        with pytest.raises(TypeError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None
            )

    def test_invalid_public_key_argument_types(self):
        with pytest.raises(TypeError):
            pytest.deprecated_call(rsa.RSAPublicKey, None, None)

    def test_invalid_private_key_argument_values(self):
        # Start with p=3, q=11, private_exponent=3, public_exponent=7,
        # modulus=33, dmp1=1, dmq1=3, iqmp=2. Then change one value at
        # a time to test the bounds.

        # Test a modulus < 3.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=2
            )

        # Test a modulus != p * q.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=35
            )

        # Test a p > modulus.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=37,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

        # Test a q > modulus.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=37,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

        # Test a dmp1 > modulus.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=35,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

        # Test a dmq1 > modulus.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=35,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

        # Test an iqmp > modulus.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=35,
                public_exponent=7,
                modulus=33
            )

        # Test a private_exponent > modulus
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=37,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

        # Test a public_exponent < 3
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=1,
                modulus=33
            )

        # Test a public_exponent > modulus
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=65537,
                modulus=33
            )

        # Test a public_exponent that is not odd.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_exponent=6,
                modulus=33
            )

        # Test a dmp1 that is not odd.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=2,
                dmq1=3,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

        # Test a dmq1 that is not odd.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPrivateKey,
                p=3,
                q=11,
                private_exponent=3,
                dmp1=1,
                dmq1=4,
                iqmp=2,
                public_exponent=7,
                modulus=33
            )

    def test_invalid_public_key_argument_values(self):
        # Start with public_exponent=7, modulus=15. Then change one value at a
        # time to test the bounds.

        # Test a modulus < 3.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPublicKey, public_exponent=7, modulus=2
            )

        # Test a public_exponent < 3
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPublicKey, public_exponent=1, modulus=15
            )

        # Test a public_exponent > modulus
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPublicKey, public_exponent=17, modulus=15
            )

        # Test a public_exponent that is not odd.
        with pytest.raises(ValueError):
            pytest.deprecated_call(
                rsa.RSAPublicKey, public_exponent=6, modulus=15
            )


def test_rsa_generate_invalid_backend():
    pretend_backend = object()

    with raises_unsupported_algorithm(_Reasons.BACKEND_MISSING_INTERFACE):
        rsa.generate_private_key(65537, 2048, pretend_backend)

    with raises_unsupported_algorithm(_Reasons.BACKEND_MISSING_INTERFACE):
        pytest.deprecated_call(
            rsa.RSAPrivateKey.generate, 65537, 2048, pretend_backend
        )


@pytest.mark.rsa
class TestRSASignature(object):
    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    @pytest.mark.parametrize(
        "pkcs1_example",
        _flatten_pkcs1_examples(load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs1v15sign-vectors.txt"),
            load_pkcs1_vectors
        ))
    )
    def test_pkcs1v15_signing(self, pkcs1_example, backend):
        private, public, example = pkcs1_example
        private_key = pytest.deprecated_call(
            rsa.RSAPrivateKey,
            p=private["p"],
            q=private["q"],
            private_exponent=private["private_exponent"],
            dmp1=private["dmp1"],
            dmq1=private["dmq1"],
            iqmp=private["iqmp"],
            public_exponent=private["public_exponent"],
            modulus=private["modulus"]
        )
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1(), backend)
        signer.update(binascii.unhexlify(example["message"]))
        signature = signer.finalize()
        assert binascii.hexlify(signature) == example["signature"]

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    @pytest.mark.parametrize(
        "pkcs1_example",
        _flatten_pkcs1_examples(load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs-1v2-1d2-vec", "pss-vect.txt"),
            load_pkcs1_vectors
        ))
    )
    def test_pss_signing(self, pkcs1_example, backend):
        private, public, example = pkcs1_example
        private_key = pytest.deprecated_call(
            rsa.RSAPrivateKey,
            p=private["p"],
            q=private["q"],
            private_exponent=private["private_exponent"],
            dmp1=private["dmp1"],
            dmq1=private["dmq1"],
            iqmp=private["iqmp"],
            public_exponent=private["public_exponent"],
            modulus=private["modulus"]
        )
        public_key = rsa.RSAPublicKey(
            public_exponent=public["public_exponent"],
            modulus=public["modulus"]
        )
        signer = private_key.signer(
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA1(),
            backend
        )
        signer.update(binascii.unhexlify(example["message"]))
        signature = signer.finalize()
        assert len(signature) == math.ceil(private_key.key_size / 8.0)
        # PSS signatures contain randomness so we can't do an exact
        # signature check. Instead we'll verify that the signature created
        # successfully verifies.
        verifier = public_key.verifier(
            signature,
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA1(),
            backend
        )
        verifier.update(binascii.unhexlify(example["message"]))
        verifier.verify()

    @pytest.mark.parametrize(
        "hash_alg",
        [hashes.SHA224(), hashes.SHA256(), hashes.SHA384(), hashes.SHA512()]
    )
    def test_pss_signing_sha2(self, hash_alg, backend):
        if not backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hash_alg),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ):
            pytest.skip(
                "Does not support {0} in MGF1 using PSS.".format(hash_alg.name)
            )
        private_key = RSA_KEY_768.private_key(backend)
        public_key = private_key.public_key()
        pss = padding.PSS(
            mgf=padding.MGF1(hash_alg),
            salt_length=padding.PSS.MAX_LENGTH
        )
        signer = private_key.signer(pss, hash_alg)
        signer.update(b"testing signature")
        signature = signer.finalize()
        verifier = public_key.verifier(signature, pss, hash_alg)
        verifier.update(b"testing signature")
        verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: (
            backend.hash_supported(hashes.SHA512()) and
            backend.rsa_padding_supported(
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA1()),
                    salt_length=padding.PSS.MAX_LENGTH
                )
            )
        ),
        skip_message="Does not support SHA512."
    )
    def test_pss_minimum_key_size_for_digest(self, backend):
        private_key = RSA_KEY_522.private_key(backend)
        signer = private_key.signer(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )
        signer.update(b"no failure")
        signer.finalize()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    @pytest.mark.supported(
        only_if=lambda backend: backend.hash_supported(hashes.SHA512()),
        skip_message="Does not support SHA512."
    )
    def test_pss_signing_digest_too_large_for_key_size(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with pytest.raises(ValueError):
            private_key.signer(
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA1()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    def test_pss_signing_salt_length_too_long(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        signer = private_key.signer(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=1000000
            ),
            hashes.SHA1()
        )
        signer.update(b"failure coming")
        with pytest.raises(ValueError):
            signer.finalize()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_use_after_finalize(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        signer.update(b"sign me")
        signer.finalize()
        with pytest.raises(AlreadyFinalized):
            signer.finalize()
        with pytest.raises(AlreadyFinalized):
            signer.update(b"more data")

    def test_unsupported_padding(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_PADDING):
            private_key.signer(DummyPadding(), hashes.SHA1())

    def test_padding_incorrect_type(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with pytest.raises(TypeError):
            private_key.signer("notpadding", hashes.SHA1())

    def test_rsa_signer_invalid_backend(self, backend):
        pretend_backend = object()
        private_key = pytest.deprecated_call(
            rsa.RSAPrivateKey,
            p=RSA_KEY_512.p,
            q=RSA_KEY_512.q,
            private_exponent=RSA_KEY_512.d,
            dmp1=RSA_KEY_512.dmp1,
            dmq1=RSA_KEY_512.dmq1,
            iqmp=RSA_KEY_512.iqmp,
            public_exponent=RSA_KEY_512.public_numbers.e,
            modulus=RSA_KEY_512.public_numbers.n
        )

        with raises_unsupported_algorithm(_Reasons.BACKEND_MISSING_INTERFACE):
            private_key.signer(
                padding.PKCS1v15(), hashes.SHA256, pretend_backend)

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(mgf=padding.MGF1(hashes.SHA1()), salt_length=0)
        ),
        skip_message="Does not support PSS."
    )
    def test_unsupported_pss_mgf(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_MGF):
            private_key.signer(
                padding.PSS(
                    mgf=DummyMGF(),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA1()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_pkcs1_digest_too_large_for_key_size(self, backend):
        private_key = RSA_KEY_599.private_key(backend)
        signer = private_key.signer(
            padding.PKCS1v15(),
            hashes.SHA512()
        )
        signer.update(b"failure coming")
        with pytest.raises(ValueError):
            signer.finalize()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_pkcs1_minimum_key_size(self, backend):
        private_key = RSA_KEY_745.private_key(backend)
        signer = private_key.signer(
            padding.PKCS1v15(),
            hashes.SHA512()
        )
        signer.update(b"no failure")
        signer.finalize()


@pytest.mark.rsa
class TestRSAVerification(object):
    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    @pytest.mark.parametrize(
        "pkcs1_example",
        _flatten_pkcs1_examples(load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs1v15sign-vectors.txt"),
            load_pkcs1_vectors
        ))
    )
    def test_pkcs1v15_verification(self, pkcs1_example, backend):
        private, public, example = pkcs1_example
        public_key = rsa.RSAPublicKey(
            public_exponent=public["public_exponent"],
            modulus=public["modulus"]
        )
        verifier = public_key.verifier(
            binascii.unhexlify(example["signature"]),
            padding.PKCS1v15(),
            hashes.SHA1(),
            backend
        )
        verifier.update(binascii.unhexlify(example["message"]))
        verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_invalid_pkcs1v15_signature_wrong_data(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        signer.update(b"sign me")
        signature = signer.finalize()
        verifier = public_key.verifier(
            signature,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        verifier.update(b"incorrect data")
        with pytest.raises(InvalidSignature):
            verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_invalid_pkcs1v15_signature_wrong_key(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        private_key2 = RSA_KEY_512_ALT.private_key(backend)
        public_key = private_key2.public_key()
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        signer.update(b"sign me")
        signature = signer.finalize()
        verifier = public_key.verifier(
            signature,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        verifier.update(b"sign me")
        with pytest.raises(InvalidSignature):
            verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=20
            )
        ),
        skip_message="Does not support PSS."
    )
    @pytest.mark.parametrize(
        "pkcs1_example",
        _flatten_pkcs1_examples(load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs-1v2-1d2-vec", "pss-vect.txt"),
            load_pkcs1_vectors
        ))
    )
    def test_pss_verification(self, pkcs1_example, backend):
        private, public, example = pkcs1_example
        public_key = rsa.RSAPublicKey(
            public_exponent=public["public_exponent"],
            modulus=public["modulus"]
        )
        verifier = public_key.verifier(
            binascii.unhexlify(example["signature"]),
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                salt_length=20
            ),
            hashes.SHA1(),
            backend
        )
        verifier.update(binascii.unhexlify(example["message"]))
        verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    def test_invalid_pss_signature_wrong_data(self, backend):
        public_key = rsa.RSAPublicKey(
            modulus=int(
                b"dffc2137d5e810cde9e4b4612f5796447218bab913b3fa98bdf7982e4fa6"
                b"ec4d6653ef2b29fb1642b095befcbea6decc178fb4bed243d3c3592c6854"
                b"6af2d3f3", 16
            ),
            public_exponent=65537
        )
        signature = binascii.unhexlify(
            b"0e68c3649df91c5bc3665f96e157efa75b71934aaa514d91e94ca8418d100f45"
            b"6f05288e58525f99666bab052adcffdf7186eb40f583bd38d98c97d3d524808b"
        )
        verifier = public_key.verifier(
            signature,
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA1(),
            backend
        )
        verifier.update(b"incorrect data")
        with pytest.raises(InvalidSignature):
            verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    def test_invalid_pss_signature_wrong_key(self, backend):
        signature = binascii.unhexlify(
            b"3a1880165014ba6eb53cc1449d13e5132ebcc0cfd9ade6d7a2494a0503bd0826"
            b"f8a46c431e0d7be0ca3e453f8b2b009e2733764da7927cc6dbe7a021437a242e"
        )
        public_key = rsa.RSAPublicKey(
            modulus=int(
                b"381201f4905d67dfeb3dec131a0fbea773489227ec7a1448c3109189ac68"
                b"5a95441be90866a14c4d2e139cd16db540ec6c7abab13ffff91443fd46a8"
                b"960cbb7658ded26a5c95c86f6e40384e1c1239c63e541ba221191c4dd303"
                b"231b42e33c6dbddf5ec9a746f09bf0c25d0f8d27f93ee0ae5c0d723348f4"
                b"030d3581e13522e1", 16
            ),
            public_exponent=65537
        )
        verifier = public_key.verifier(
            signature,
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA1(),
            backend
        )
        verifier.update(b"sign me")
        with pytest.raises(InvalidSignature):
            verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    def test_invalid_pss_signature_data_too_large_for_modulus(self, backend):
        signature = binascii.unhexlify(
            b"cb43bde4f7ab89eb4a79c6e8dd67e0d1af60715da64429d90c716a490b799c29"
            b"194cf8046509c6ed851052367a74e2e92d9b38947ed74332acb115a03fcc0222"
        )
        public_key = rsa.RSAPublicKey(
            modulus=int(
                b"381201f4905d67dfeb3dec131a0fbea773489227ec7a1448c3109189ac68"
                b"5a95441be90866a14c4d2e139cd16db540ec6c7abab13ffff91443fd46a8"
                b"960cbb7658ded26a5c95c86f6e40384e1c1239c63e541ba221191c4dd303"
                b"231b42e33c6dbddf5ec9a746f09bf0c25d0f8d27f93ee0ae5c0d723348f4"
                b"030d3581e13522", 16
            ),
            public_exponent=65537
        )
        verifier = public_key.verifier(
            signature,
            padding.PSS(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA1(),
            backend
        )
        verifier.update(b"sign me")
        with pytest.raises(InvalidSignature):
            verifier.verify()

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_use_after_finalize(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        signer.update(b"sign me")
        signature = signer.finalize()

        verifier = public_key.verifier(
            signature,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        verifier.update(b"sign me")
        verifier.verify()
        with pytest.raises(AlreadyFinalized):
            verifier.verify()
        with pytest.raises(AlreadyFinalized):
            verifier.update(b"more data")

    def test_unsupported_padding(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_PADDING):
            public_key.verifier(b"sig", DummyPadding(), hashes.SHA1())

    def test_padding_incorrect_type(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()
        with pytest.raises(TypeError):
            public_key.verifier(b"sig", "notpadding", hashes.SHA1())

    def test_rsa_verifier_invalid_backend(self, backend):
        pretend_backend = object()
        private_key = pytest.deprecated_call(
            rsa.RSAPrivateKey.generate,
            65537,
            2048,
            backend
        )
        public_key = private_key.public_key()

        with raises_unsupported_algorithm(_Reasons.BACKEND_MISSING_INTERFACE):
            public_key.verifier(
                b"foo", padding.PKCS1v15(), hashes.SHA256(), pretend_backend)

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(mgf=padding.MGF1(hashes.SHA1()), salt_length=0)
        ),
        skip_message="Does not support PSS."
    )
    def test_unsupported_pss_mgf(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_MGF):
            public_key.verifier(
                b"sig",
                padding.PSS(
                    mgf=DummyMGF(),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA1()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    @pytest.mark.supported(
        only_if=lambda backend: backend.hash_supported(hashes.SHA512()),
        skip_message="Does not support SHA512."
    )
    def test_pss_verify_digest_too_large_for_key_size(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        signature = binascii.unhexlify(
            b"8b9a3ae9fb3b64158f3476dd8d8a1f1425444e98940e0926378baa9944d219d8"
            b"534c050ef6b19b1bdc6eb4da422e89161106a6f5b5cc16135b11eb6439b646bd"
        )
        public_key = private_key.public_key()
        with pytest.raises(ValueError):
            public_key.verifier(
                signature,
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS."
    )
    def test_pss_verify_salt_length_too_long(self, backend):
        signature = binascii.unhexlify(
            b"8b9a3ae9fb3b64158f3476dd8d8a1f1425444e98940e0926378baa9944d219d8"
            b"534c050ef6b19b1bdc6eb4da422e89161106a6f5b5cc16135b11eb6439b646bd"
        )
        public_key = rsa.RSAPublicKey(
            modulus=int(
                b"d309e4612809437548b747d7f9eb9cd3340f54fe42bb3f84a36933b0839c"
                b"11b0c8b7f67e11f7252370161e31159c49c784d4bc41c42a78ce0f0b40a3"
                b"ca8ffb91", 16
            ),
            public_exponent=65537
        )
        verifier = public_key.verifier(
            signature,
            padding.PSS(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA1(),
                ),
                salt_length=1000000
            ),
            hashes.SHA1(),
            backend
        )
        verifier.update(b"sign me")
        with pytest.raises(InvalidSignature):
            verifier.verify()


@pytest.mark.rsa
class TestRSAPSSMGF1Verification(object):
    test_rsa_pss_mgf1_sha1 = pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA1()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS using MGF1 with SHA1."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGenPSS_186-2.rsp",
            "SigGenPSS_186-3.rsp",
            "SigVerPSS_186-3.rsp",
        ],
        hashes.SHA1(),
        lambda params, hash_alg: padding.PSS(
            mgf=padding.MGF1(
                algorithm=hash_alg,
            ),
            salt_length=params["salt_length"]
        )
    ))

    test_rsa_pss_mgf1_sha224 = pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA224()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS using MGF1 with SHA224."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGenPSS_186-2.rsp",
            "SigGenPSS_186-3.rsp",
            "SigVerPSS_186-3.rsp",
        ],
        hashes.SHA224(),
        lambda params, hash_alg: padding.PSS(
            mgf=padding.MGF1(
                algorithm=hash_alg,
            ),
            salt_length=params["salt_length"]
        )
    ))

    test_rsa_pss_mgf1_sha256 = pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS using MGF1 with SHA256."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGenPSS_186-2.rsp",
            "SigGenPSS_186-3.rsp",
            "SigVerPSS_186-3.rsp",
        ],
        hashes.SHA256(),
        lambda params, hash_alg: padding.PSS(
            mgf=padding.MGF1(
                algorithm=hash_alg,
            ),
            salt_length=params["salt_length"]
        )
    ))

    test_rsa_pss_mgf1_sha384 = pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA384()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS using MGF1 with SHA384."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGenPSS_186-2.rsp",
            "SigGenPSS_186-3.rsp",
            "SigVerPSS_186-3.rsp",
        ],
        hashes.SHA384(),
        lambda params, hash_alg: padding.PSS(
            mgf=padding.MGF1(
                algorithm=hash_alg,
            ),
            salt_length=params["salt_length"]
        )
    ))

    test_rsa_pss_mgf1_sha512 = pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            )
        ),
        skip_message="Does not support PSS using MGF1 with SHA512."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGenPSS_186-2.rsp",
            "SigGenPSS_186-3.rsp",
            "SigVerPSS_186-3.rsp",
        ],
        hashes.SHA512(),
        lambda params, hash_alg: padding.PSS(
            mgf=padding.MGF1(
                algorithm=hash_alg,
            ),
            salt_length=params["salt_length"]
        )
    ))


@pytest.mark.rsa
class TestRSAPKCS1Verification(object):
    test_rsa_pkcs1v15_verify_sha1 = pytest.mark.supported(
        only_if=lambda backend: (
            backend.hash_supported(hashes.SHA1()) and
            backend.rsa_padding_supported(padding.PKCS1v15())
        ),
        skip_message="Does not support SHA1 and PKCS1v1.5."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGen15_186-2.rsp",
            "SigGen15_186-3.rsp",
            "SigVer15_186-3.rsp",
        ],
        hashes.SHA1(),
        lambda params, hash_alg: padding.PKCS1v15()
    ))

    test_rsa_pkcs1v15_verify_sha224 = pytest.mark.supported(
        only_if=lambda backend: (
            backend.hash_supported(hashes.SHA224()) and
            backend.rsa_padding_supported(padding.PKCS1v15())
        ),
        skip_message="Does not support SHA224 and PKCS1v1.5."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGen15_186-2.rsp",
            "SigGen15_186-3.rsp",
            "SigVer15_186-3.rsp",
        ],
        hashes.SHA224(),
        lambda params, hash_alg: padding.PKCS1v15()
    ))

    test_rsa_pkcs1v15_verify_sha256 = pytest.mark.supported(
        only_if=lambda backend: (
            backend.hash_supported(hashes.SHA256()) and
            backend.rsa_padding_supported(padding.PKCS1v15())
        ),
        skip_message="Does not support SHA256 and PKCS1v1.5."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGen15_186-2.rsp",
            "SigGen15_186-3.rsp",
            "SigVer15_186-3.rsp",
        ],
        hashes.SHA256(),
        lambda params, hash_alg: padding.PKCS1v15()
    ))

    test_rsa_pkcs1v15_verify_sha384 = pytest.mark.supported(
        only_if=lambda backend: (
            backend.hash_supported(hashes.SHA384()) and
            backend.rsa_padding_supported(padding.PKCS1v15())
        ),
        skip_message="Does not support SHA384 and PKCS1v1.5."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGen15_186-2.rsp",
            "SigGen15_186-3.rsp",
            "SigVer15_186-3.rsp",
        ],
        hashes.SHA384(),
        lambda params, hash_alg: padding.PKCS1v15()
    ))

    test_rsa_pkcs1v15_verify_sha512 = pytest.mark.supported(
        only_if=lambda backend: (
            backend.hash_supported(hashes.SHA512()) and
            backend.rsa_padding_supported(padding.PKCS1v15())
        ),
        skip_message="Does not support SHA512 and PKCS1v1.5."
    )(generate_rsa_verification_test(
        load_rsa_nist_vectors,
        os.path.join("asymmetric", "RSA", "FIPS_186-2"),
        [
            "SigGen15_186-2.rsp",
            "SigGen15_186-3.rsp",
            "SigVer15_186-3.rsp",
        ],
        hashes.SHA512(),
        lambda params, hash_alg: padding.PKCS1v15()
    ))


class TestPSS(object):
    def test_invalid_salt_length_not_integer(self):
        with pytest.raises(TypeError):
            padding.PSS(
                mgf=padding.MGF1(
                    hashes.SHA1()
                ),
                salt_length=b"not_a_length"
            )

    def test_invalid_salt_length_negative_integer(self):
        with pytest.raises(ValueError):
            padding.PSS(
                mgf=padding.MGF1(
                    hashes.SHA1()
                ),
                salt_length=-1
            )

    def test_valid_pss_parameters(self):
        algorithm = hashes.SHA1()
        salt_length = algorithm.digest_size
        mgf = padding.MGF1(algorithm)
        pss = padding.PSS(mgf=mgf, salt_length=salt_length)
        assert pss._mgf == mgf
        assert pss._salt_length == salt_length

    def test_valid_pss_parameters_maximum(self):
        algorithm = hashes.SHA1()
        mgf = padding.MGF1(algorithm)
        pss = padding.PSS(mgf=mgf, salt_length=padding.PSS.MAX_LENGTH)
        assert pss._mgf == mgf
        assert pss._salt_length == padding.PSS.MAX_LENGTH


class TestMGF1(object):
    def test_invalid_hash_algorithm(self):
        with pytest.raises(TypeError):
            padding.MGF1(b"not_a_hash")

    def test_valid_mgf1_parameters(self):
        algorithm = hashes.SHA1()
        mgf = padding.MGF1(algorithm)
        assert mgf._algorithm == algorithm


class TestOAEP(object):
    def test_invalid_algorithm(self):
        mgf = padding.MGF1(hashes.SHA1())
        with pytest.raises(TypeError):
            padding.OAEP(
                mgf=mgf,
                algorithm=b"",
                label=None
            )


@pytest.mark.rsa
class TestRSADecryption(object):
    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    @pytest.mark.parametrize(
        "vector",
        _flatten_pkcs1_examples(load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs1v15crypt-vectors.txt"),
            load_pkcs1_vectors
        ))
    )
    def test_decrypt_pkcs1v15_vectors(self, vector, backend):
        private, public, example = vector
        skey = rsa.RSAPrivateKey(
            p=private["p"],
            q=private["q"],
            private_exponent=private["private_exponent"],
            dmp1=private["dmp1"],
            dmq1=private["dmq1"],
            iqmp=private["iqmp"],
            public_exponent=private["public_exponent"],
            modulus=private["modulus"]
        )
        ciphertext = binascii.unhexlify(example["encryption"])
        assert len(ciphertext) == math.ceil(skey.key_size / 8.0)
        message = skey.decrypt(
            ciphertext,
            padding.PKCS1v15(),
            backend
        )
        assert message == binascii.unhexlify(example["message"])

    def test_unsupported_padding(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_PADDING):
            private_key.decrypt(b"0" * 64, DummyPadding())

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_decrypt_invalid_decrypt(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with pytest.raises(ValueError):
            private_key.decrypt(
                b"\x00" * 64,
                padding.PKCS1v15()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_decrypt_ciphertext_too_large(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with pytest.raises(ValueError):
            private_key.decrypt(
                b"\x00" * 65,
                padding.PKCS1v15()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    def test_decrypt_ciphertext_too_small(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        ct = binascii.unhexlify(
            b"50b4c14136bd198c2f3c3ed243fce036e168d56517984a263cd66492b80804f1"
            b"69d210f2b9bdfb48b12f9ea05009c77da257cc600ccefe3a6283789d8ea0"
        )
        with pytest.raises(ValueError):
            private_key.decrypt(
                ct,
                padding.PKCS1v15()
            )

    def test_rsa_decrypt_invalid_backend(self, backend):
        pretend_backend = object()
        private_key = pytest.deprecated_call(
            rsa.RSAPrivateKey.generate, 65537, 2048, backend
        )

        with raises_unsupported_algorithm(_Reasons.BACKEND_MISSING_INTERFACE):
            private_key.decrypt(
                b"irrelevant",
                padding.PKCS1v15(),
                pretend_backend
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        ),
        skip_message="Does not support OAEP."
    )
    @pytest.mark.parametrize(
        "vector",
        _flatten_pkcs1_examples(load_vectors_from_file(
            os.path.join(
                "asymmetric", "RSA", "pkcs-1v2-1d2-vec", "oaep-vect.txt"),
            load_pkcs1_vectors
        ))
    )
    def test_decrypt_oaep_vectors(self, vector, backend):
        private, public, example = vector
        skey = pytest.deprecated_call(
            rsa.RSAPrivateKey,
            p=private["p"],
            q=private["q"],
            private_exponent=private["private_exponent"],
            dmp1=private["dmp1"],
            dmq1=private["dmq1"],
            iqmp=private["iqmp"],
            public_exponent=private["public_exponent"],
            modulus=private["modulus"]
        )
        message = skey.decrypt(
            binascii.unhexlify(example["encryption"]),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            ),
            backend
        )
        assert message == binascii.unhexlify(example["message"])

    def test_unsupported_oaep_mgf(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_MGF):
            private_key.decrypt(
                b"0" * 64,
                padding.OAEP(
                    mgf=DummyMGF(),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )


@pytest.mark.rsa
class TestRSAEncryption(object):
    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        ),
        skip_message="Does not support OAEP."
    )
    @pytest.mark.parametrize(
        ("key_data", "pad"),
        itertools.product(
            (RSA_KEY_1024, RSA_KEY_1025, RSA_KEY_1026, RSA_KEY_1027,
             RSA_KEY_1028, RSA_KEY_1029, RSA_KEY_1030, RSA_KEY_1031,
             RSA_KEY_1536, RSA_KEY_2048),
            [
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            ]
        )
    )
    def test_rsa_encrypt_oaep(self, key_data, pad, backend):
        private_key = rsa.RSAPrivateKey(
            p=key_data.p,
            q=key_data.q,
            private_exponent=key_data.d,
            dmp1=key_data.dmp1,
            dmq1=key_data.dmq1,
            iqmp=key_data.iqmp,
            public_exponent=key_data.public_numbers.e,
            modulus=key_data.public_numbers.n
        )
        pt = b"encrypt me!"
        public_key = private_key.public_key()
        ct = public_key.encrypt(pt, pad, backend)
        assert ct != pt
        assert len(ct) == math.ceil(public_key.key_size / 8.0)
        recovered_pt = private_key.decrypt(ct, pad, backend)
        assert recovered_pt == pt

    @pytest.mark.supported(
        only_if=lambda backend: backend.rsa_padding_supported(
            padding.PKCS1v15()
        ),
        skip_message="Does not support PKCS1v1.5."
    )
    @pytest.mark.parametrize(
        ("key_data", "pad"),
        itertools.product(
            (RSA_KEY_1024, RSA_KEY_1025, RSA_KEY_1026, RSA_KEY_1027,
             RSA_KEY_1028, RSA_KEY_1029, RSA_KEY_1030, RSA_KEY_1031,
             RSA_KEY_1536, RSA_KEY_2048),
            [padding.PKCS1v15()]
        )
    )
    def test_rsa_encrypt_pkcs1v15(self, key_data, pad, backend):
        private_key = key_data.private_key(backend)
        pt = b"encrypt me!"
        public_key = private_key.public_key()
        ct = public_key.encrypt(pt, pad)
        assert ct != pt
        assert len(ct) == math.ceil(public_key.key_size / 8.0)
        recovered_pt = private_key.decrypt(ct, pad)
        assert recovered_pt == pt

    @pytest.mark.parametrize(
        ("key_data", "pad"),
        itertools.product(
            (RSA_KEY_1024, RSA_KEY_1025, RSA_KEY_1026, RSA_KEY_1027,
             RSA_KEY_1028, RSA_KEY_1029, RSA_KEY_1030, RSA_KEY_1031,
             RSA_KEY_1536, RSA_KEY_2048),
            (
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                ),
                padding.PKCS1v15()
            )
        )
    )
    def test_rsa_encrypt_key_too_small(self, key_data, pad, backend):
        private_key = key_data.private_key(backend)
        public_key = private_key.public_key()
        # Slightly smaller than the key size but not enough for padding.
        with pytest.raises(ValueError):
            public_key.encrypt(
                b"\x00" * (private_key.key_size // 8 - 1),
                pad
            )

        # Larger than the key size.
        with pytest.raises(ValueError):
            public_key.encrypt(
                b"\x00" * (private_key.key_size // 8 + 5),
                pad
            )

    def test_rsa_encrypt_invalid_backend(self, backend):
        pretend_backend = object()
        private_key = pytest.deprecated_call(
            rsa.RSAPrivateKey.generate, 65537, 512, backend
        )
        public_key = private_key.public_key()

        with raises_unsupported_algorithm(_Reasons.BACKEND_MISSING_INTERFACE):
            public_key.encrypt(
                b"irrelevant",
                padding.PKCS1v15(),
                pretend_backend
            )

    def test_unsupported_padding(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()

        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_PADDING):
            public_key.encrypt(b"somedata", DummyPadding())
        with pytest.raises(TypeError):
            public_key.encrypt(b"somedata", padding=object())

    def test_unsupported_oaep_mgf(self, backend):
        private_key = RSA_KEY_512.private_key(backend)
        public_key = private_key.public_key()

        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_MGF):
            public_key.encrypt(
                b"ciphertext",
                padding.OAEP(
                    mgf=DummyMGF(),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )


@pytest.mark.rsa
class TestRSANumbers(object):
    def test_rsa_public_numbers(self):
        public_numbers = rsa.RSAPublicNumbers(e=1, n=15)
        assert public_numbers.e == 1
        assert public_numbers.n == 15

    def test_rsa_private_numbers(self):
        public_numbers = rsa.RSAPublicNumbers(e=1, n=15)
        private_numbers = rsa.RSAPrivateNumbers(
            p=3,
            q=5,
            d=1,
            dmp1=1,
            dmq1=1,
            iqmp=2,
            public_numbers=public_numbers
        )

        assert private_numbers.p == 3
        assert private_numbers.q == 5
        assert private_numbers.d == 1
        assert private_numbers.dmp1 == 1
        assert private_numbers.dmq1 == 1
        assert private_numbers.iqmp == 2
        assert private_numbers.public_numbers == public_numbers

    def test_rsa_private_numbers_create_key(self, backend):
        private_key = RSA_KEY_1024.private_key(backend)
        assert private_key

    def test_rsa_public_numbers_create_key(self, backend):
        public_key = RSA_KEY_1024.public_numbers.public_key(backend)
        assert public_key

    def test_public_numbers_invalid_types(self):
        with pytest.raises(TypeError):
            rsa.RSAPublicNumbers(e=None, n=15)

        with pytest.raises(TypeError):
            rsa.RSAPublicNumbers(e=1, n=None)

    def test_private_numbers_invalid_types(self):
        public_numbers = rsa.RSAPublicNumbers(e=1, n=15)

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=None,
                q=5,
                d=1,
                dmp1=1,
                dmq1=1,
                iqmp=2,
                public_numbers=public_numbers
            )

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=None,
                d=1,
                dmp1=1,
                dmq1=1,
                iqmp=2,
                public_numbers=public_numbers
            )

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=5,
                d=None,
                dmp1=1,
                dmq1=1,
                iqmp=2,
                public_numbers=public_numbers
            )

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=5,
                d=1,
                dmp1=None,
                dmq1=1,
                iqmp=2,
                public_numbers=public_numbers
            )

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=5,
                d=1,
                dmp1=1,
                dmq1=None,
                iqmp=2,
                public_numbers=public_numbers
            )

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=5,
                d=1,
                dmp1=1,
                dmq1=1,
                iqmp=None,
                public_numbers=public_numbers
            )

        with pytest.raises(TypeError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=5,
                d=1,
                dmp1=1,
                dmq1=1,
                iqmp=2,
                public_numbers=None
            )

    def test_invalid_public_numbers_argument_values(self, backend):
        # Start with public_exponent=7, modulus=15. Then change one value at a
        # time to test the bounds.

        # Test a modulus < 3.

        with pytest.raises(ValueError):
            rsa.RSAPublicNumbers(e=7, n=2).public_key(backend)

        # Test a public_exponent < 3
        with pytest.raises(ValueError):
            rsa.RSAPublicNumbers(e=1, n=15).public_key(backend)

        # Test a public_exponent > modulus
        with pytest.raises(ValueError):
            rsa.RSAPublicNumbers(e=17, n=15).public_key(backend)

        # Test a public_exponent that is not odd.
        with pytest.raises(ValueError):
            rsa.RSAPublicNumbers(e=16, n=15).public_key(backend)

    def test_invalid_private_numbers_argument_values(self, backend):
        # Start with p=3, q=11, private_exponent=3, public_exponent=7,
        # modulus=33, dmp1=1, dmq1=3, iqmp=2. Then change one value at
        # a time to test the bounds.

        # Test a modulus < 3.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=2
                )
            ).private_key(backend)

        # Test a modulus != p * q.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=35
                )
            ).private_key(backend)

        # Test a p > modulus.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=37,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test a q > modulus.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=37,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test a dmp1 > modulus.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=35,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test a dmq1 > modulus.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=35,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test an iqmp > modulus.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=35,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test a private_exponent > modulus
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=37,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test a public_exponent < 3
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=1,
                    n=33
                )
            ).private_key(backend)

        # Test a public_exponent > modulus
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=35,
                public_numbers=rsa.RSAPublicNumbers(
                    e=65537,
                    n=33
                )
            ).private_key(backend)

        # Test a public_exponent that is not odd.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=6,
                    n=33
                )
            ).private_key(backend)

        # Test a dmp1 that is not odd.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=2,
                dmq1=3,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

        # Test a dmq1 that is not odd.
        with pytest.raises(ValueError):
            rsa.RSAPrivateNumbers(
                p=3,
                q=11,
                d=3,
                dmp1=1,
                dmq1=4,
                iqmp=2,
                public_numbers=rsa.RSAPublicNumbers(
                    e=7,
                    n=33
                )
            ).private_key(backend)

    def test_public_number_repr(self):
        num = RSAPublicNumbers(1, 1)
        assert repr(num) == "<RSAPublicNumbers(e=1, n=1)>"
