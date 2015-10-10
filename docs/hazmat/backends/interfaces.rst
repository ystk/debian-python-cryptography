.. hazmat::

Backend interfaces
==================

.. currentmodule:: cryptography.hazmat.backends.interfaces


Backend implementations may provide a number of interfaces to support
operations such as :doc:`/hazmat/primitives/symmetric-encryption`,
:doc:`/hazmat/primitives/cryptographic-hashes`, and
:doc:`/hazmat/primitives/mac/hmac`.

A specific ``backend`` may provide one or more of these interfaces.


.. class:: CipherBackend

    A backend that provides methods for using ciphers for encryption
    and decryption.

    The following backends implement this interface:

    * :doc:`/hazmat/backends/openssl`
    * :doc:`/hazmat/backends/commoncrypto`

    .. method:: cipher_supported(cipher, mode)

        Check if a ``cipher`` and ``mode`` combination is supported by
        this backend.

        :param cipher: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.CipherAlgorithm`
            provider.
        :param mode: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.Mode` provider.

        :returns: ``True`` if the specified ``cipher`` and ``mode`` combination
            is supported by this backend, otherwise ``False``


    .. method:: create_symmetric_encryption_ctx(cipher, mode)

        Create a
        :class:`~cryptography.hazmat.primitives.interfaces.CipherContext` that
        can be used for encrypting data with the symmetric ``cipher`` using
        the given ``mode``.

        :param cipher: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.CipherAlgorithm`
            provider.
        :param mode: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.Mode` provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.CipherContext`

        :raises ValueError: When tag is not None in an AEAD mode


    .. method:: create_symmetric_decryption_ctx(cipher, mode)

        Create a
        :class:`~cryptography.hazmat.primitives.interfaces.CipherContext` that
        can be used for decrypting data with the symmetric ``cipher`` using
        the given ``mode``.

        :param cipher: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.CipherAlgorithm`
            provider.
        :param mode: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.Mode` provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.CipherContext`

        :raises ValueError: When tag is None in an AEAD mode


.. class:: HashBackend

    A backend with methods for using cryptographic hash functions.

    The following backends implement this interface:

    * :doc:`/hazmat/backends/openssl`
    * :doc:`/hazmat/backends/commoncrypto`

    .. method:: hash_supported(algorithm)

        Check if the specified ``algorithm`` is supported by this backend.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns: ``True`` if the specified ``algorithm`` is supported by this
            backend, otherwise ``False``.


    .. method:: create_hash_ctx(algorithm)

        Create a
        :class:`~cryptography.hazmat.primitives.interfaces.HashContext` that
        uses the specified ``algorithm`` to calculate a message digest.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.HashContext`


.. class:: HMACBackend

    A backend with methods for using cryptographic hash functions as message
    authentication codes.

    The following backends implement this interface:

    * :doc:`/hazmat/backends/openssl`
    * :doc:`/hazmat/backends/commoncrypto`

    .. method:: hmac_supported(algorithm)

        Check if the specified ``algorithm`` is supported by this backend.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns: ``True`` if the specified ``algorithm`` is supported for HMAC
            by this backend, otherwise ``False``.

    .. method:: create_hmac_ctx(algorithm)

        Create a
        :class:`~cryptography.hazmat.primitives.interfaces.HashContext` that
        uses the specified ``algorithm`` to calculate a hash-based message
        authentication code.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.HashContext`


.. class:: CMACBackend

    .. versionadded:: 0.4

    A backend with methods for using CMAC

    .. method:: cmac_algorithm_supported(algorithm)

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.BlockCipherAlgorithm`
            provider.
        :return: Returns True if the block cipher is supported for CMAC by this backend

    .. method:: create_cmac_ctx(algorithm)

        Create a
        :class:`~cryptography.hazmat.primitives.interfaces.CMACContext` that
        uses the specified ``algorithm`` to calculate a message authentication code.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.BlockCipherAlgorithm`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.CMACContext`


.. class:: PBKDF2HMACBackend

    .. versionadded:: 0.2

    A backend with methods for using PBKDF2 using HMAC as a PRF.

    The following backends implement this interface:

    * :doc:`/hazmat/backends/openssl`
    * :doc:`/hazmat/backends/commoncrypto`

    .. method:: pbkdf2_hmac_supported(algorithm)

        Check if the specified ``algorithm`` is supported by this backend.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns: ``True`` if the specified ``algorithm`` is supported for
            PBKDF2 HMAC by this backend, otherwise ``False``.

    .. method:: derive_pbkdf2_hmac(self, algorithm, length, salt, iterations,
                                   key_material)

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param int length: The desired length of the derived key. Maximum is
            (2\ :sup:`32` - 1) * ``algorithm.digest_size``

        :param bytes salt: A salt.

        :param int iterations: The number of iterations to perform of the hash
            function. This can be used to control the length of time the
            operation takes. Higher numbers help mitigate brute force attacks
            against derived keys.

        :param bytes key_material: The key material to use as a basis for
            the derived key. This is typically a password.

        :return bytes: Derived key.


.. class:: RSABackend

    .. versionadded:: 0.2

    A backend with methods for using RSA.

    .. method:: generate_rsa_private_key(public_exponent, key_size)

        :param int public_exponent: The public exponent of the new key.
            Often one of the small Fermat primes 3, 5, 17, 257 or 65537.

        :param int key_size: The length in bits of the modulus. Should be
            at least 2048.

        :return: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
            provider.

        :raises ValueError: If the public_exponent is not valid.

    .. method:: create_rsa_signature_ctx(private_key, padding, algorithm)

        .. deprecated:: 0.5

        :param private_key: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
            provider.

        :param padding: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricSignatureContext`

    .. method:: create_rsa_verification_ctx(public_key, signature, padding, algorithm)

        .. deprecated:: 0.5

        :param public_key: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`
            provider.

        :param bytes signature: The signature to verify.

        :param padding: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricVerificationContext`

    .. method:: mgf1_hash_supported(algorithm)

        ..deprecated:: 0.5

        Check if the specified ``algorithm`` is supported for use with
        :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
        inside :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS`
        padding. This method is deprecated in favor of
        ``rsa_padding_supported``.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns: ``True`` if the specified ``algorithm`` is supported by this
            backend, otherwise ``False``.

    .. method:: rsa_padding_supported(padding)

        Check if the specified ``padding`` is supported by the backend.

        :param padding: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :returns: ``True`` if the specified ``padding`` is supported by this
            backend, otherwise ``False``.

    .. method:: generate_rsa_parameters_supported(public_exponent, key_size)

        Check if the specified parameters are supported for key generation by
        the backend.

        :param int public_exponent: The public exponent.

        :param int key_size: The bit length of the generated modulus.

    .. method:: decrypt_rsa(private_key, ciphertext, padding)

        .. deprecated:: 0.5

        :param private_key: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
            provider.

        :param bytes ciphertext: The ciphertext to decrypt.

        :param padding: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :return bytes: The decrypted data.

        :raises cryptography.exceptions.UnsupportedAlgorithm: If an unsupported
            MGF, hash function, or padding is chosen.

        :raises ValueError: When decryption fails or key size does not match
            ciphertext length.

    .. method:: encrypt_rsa(public_key, plaintext, padding)

        .. deprecated:: 0.5

        :param public_key: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`
            provider.

        :param bytes plaintext: The plaintext to encrypt.

        :param padding: An instance of an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :return bytes: The encrypted data.

        :raises cryptography.exceptions.UnsupportedAlgorithm: If an unsupported
            MGF, hash function, or padding is chosen.

        :raises ValueError: When plaintext is too long for the key size.

    .. method:: load_rsa_private_numbers(numbers):

        :param numbers: An instance of
            :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateNumbers`.

        :returns: A provider of
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`.

        :raises ValueError: This is raised when the values of ``p``, ``q``,
            ``private_exponent``, ``public_exponent``, or ``modulus`` do not
            match the bounds specified in :rfc:`3447`.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This raised when
            any backend specific criteria are not met.

    .. method:: load_rsa_public_numbers(numbers):

        :param numbers: An instance of
            :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateNumbers`.

        :returns: A provider of
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`.

        :raises ValueError: This is raised when the values of
            ``public_exponent`` or ``modulus`` do not match the bounds
            specified in :rfc:`3447`.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This raised when
            any backend specific criteria are not met.


.. class:: DSABackend

    .. versionadded:: 0.4

    A backend with methods for using DSA.

    .. method:: generate_dsa_parameters(key_size)

        :param int key_size: The length of the modulus in bits. It should be
            either 1024, 2048 or 3072. For keys generated in 2014 this should
            be at least 2048.
            Note that some applications (such as SSH) have not yet gained
            support for larger key sizes specified in FIPS 186-3 and are still
            restricted to only the 1024-bit keys specified in FIPS 186-2.

        :return: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
            provider.

    .. method:: generate_dsa_private_key(parameters)

        :param parameters: A
            :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
            provider.

        :return: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
            provider.

        :raises ValueError: This is raised if the key size is not one of 1024,
            2048, or 3072. It is also raised when OpenSSL is older than version
            1.0.0 and the key size is larger than 1024; older OpenSSL versions
            do not support keys larger than 1024 bits.

    .. method:: generate_dsa_private_key_and_parameters(key_size)

        :param int key_size: The length of the modulus in bits. It should be
            either 1024, 2048 or 3072. For keys generated in 2014 this should
            be at least 2048.
            Note that some applications (such as SSH) have not yet gained
            support for larger key sizes specified in FIPS 186-3 and are still
            restricted to only the 1024-bit keys specified in FIPS 186-2.

        :return: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
            provider.

        :raises ValueError: This is raised if the key size is not supported
            by the backend.

    .. method:: create_dsa_signature_ctx(private_key, algorithm)

        .. deprecated:: 0.5

        :param private_key: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
            provider.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricSignatureContext`

    .. method:: create_dsa_verification_ctx(public_key, signature, algorithm)

        .. deprecated:: 0.5

        :param public_key: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`
            provider.

        :param bytes signature: The signature to verify. DER encoded as
            specified in :rfc:`6979`.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricVerificationContext`

    .. method:: dsa_hash_supported(algorithm):

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :returns: ``True`` if the specified ``algorithm`` is supported by this
            backend, otherwise ``False``.

    .. method:: dsa_parameters_supported(p, q, g):

        :param int p: The p value of a DSA key.

        :param int q: The q value of a DSA key.

        :param int g: The g value of a DSA key.

        :returns: ``True`` if the given values of ``p``, ``q``, and ``g`` are
            supported by this backend, otherwise ``False``.

    .. method:: load_dsa_parameter_numbers(numbers):

        :param numbers: An instance of
            :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAParameterNumbers`.

        :returns: A provider of
            :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This raised when
            any backend specific criteria are not met.

    .. method:: load_dsa_private_numbers(numbers):

        :param numbers: An instance of
            :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateNumbers`.

        :returns: A provider of
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This raised when
            any backend specific criteria are not met.

    .. method:: load_dsa_public_numbers(numbers):

        :param numbers: An instance of
            :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicNumbers`.

        :returns: A provider of
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This raised when
            any backend specific criteria are not met.


.. class:: EllipticCurveBackend

    .. versionadded:: 0.5

    .. method:: elliptic_curve_supported(curve)

        :param curve: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurve`
            provider.

        :returns: True if the elliptic curve is supported by this backend.

    .. method:: elliptic_curve_signature_algorithm_supported(signature_algorithm, curve)

        :param signature_algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurveSignatureAlgorithm`
            provider.

        :param curve: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurve`
            provider.

        :returns: True if the signature algorithm and curve are supported by this backend.

    .. method:: generate_elliptic_curve_private_key(curve)

        :param curve: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurve`
            provider.

    .. method:: load_elliptic_curve_private_numbers(numbers)

        :param numbers: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurvePrivateNumbers`
            provider.

        :returns: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurvePrivateKey`
            provider.

    .. method:: load_elliptic_curve_public_numbers(numbers)

        :param numbers: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurvePublicNumbers`
            provider.

        :returns: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurvePublicKey`
            provider.

.. class:: PEMSerializationBackend

    .. versionadded:: 0.6

    A backend with methods for working with any PEM encoded keys.

    .. method:: load_pem_private_key(data, password)

        :param bytes data: PEM data to load.
        :param bytes password: The password to use if the data is encrypted.
            Should be ``None`` if the data is not encrypted.
        :return: A new instance of the appropriate type of private key that the
            serialized data contains.
        :raises ValueError: If the data could not be deserialized.
        :raises cryptography.exceptions.UnsupportedAlgorithm: If the data is
            encrypted with an unsupported algorithm.

    .. method:: load_pem_public_key(data)

        :param bytes data: PEM data to load.
        :return: A new instance of the appropriate type of public key
            serialized data contains.
        :raises ValueError: If the data could not be deserialized.

.. class:: TraditionalOpenSSLSerializationBackend

    .. versionadded:: 0.3

    A backend with methods for working with OpenSSL's "traditional" PKCS #1
    style key serialization.

    .. method:: load_openssl_pem_private_key(data, password)

        :param bytes data: PEM data to deserialize.

        :param bytes password: The password to use if this data is encrypted.
            Should be None if the data is not encrypted.

        :return: A new instance of the appropriate type of private key that the
            serialized data contains.

        :raises ValueError: If the data could not be deserialized correctly.

        :raises cryptography.exceptions.UnsupportedAlgorithm: If the data is
            encrypted with an unsupported algorithm.


.. class:: PKCS8SerializationBackend

    .. versionadded:: 0.5

    A backend with methods for working with PKCS #8 key serialization.

    .. method:: load_pkcs8_pem_private_key(data, password)

        :param bytes data: PEM data to deserialize.

        :param bytes password: The password to use if this data is encrypted.
            Should be None if the data is not encrypted.

        :return: A new instance of the appropriate private key or public key
            that the serialized data contains.

        :raises ValueError: If the data could not be deserialized correctly.

        :raises cryptography.exceptions.UnsupportedAlgorithm: If the data is
            encrypted with an unsupported algorithm.

