.. hazmat::

RSA
===

.. currentmodule:: cryptography.hazmat.primitives.asymmetric.rsa

`RSA`_ is a `public-key`_ algorithm for encrypting and signing messages.

Generation
~~~~~~~~~~

.. function:: generate_private_key(public_exponent, key_size, backend)

    .. versionadded:: 0.5

    Generate an RSA private key using the provided ``backend``.

    :param int public_exponent: The public exponent of the new key.
        Usually one of the small Fermat primes 3, 5, 17, 257, 65537. If in
        doubt you should `use 65537`_.
    :param int key_size: The length of the modulus in bits. For keys
        generated in 2014 it is strongly recommended to be
        `at least 2048`_ (See page 41). It must not be less than 512.
        Some backends may have additional limitations.
    :param backend: A
        :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
        provider.
    :return: A :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
        provider.

    :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
        the provided ``backend`` does not implement
        :class:`~cryptography.hazmat.backends.interfaces.RSABackend`

Signing
~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
provider.

.. doctest::

    >>> from cryptography.hazmat.backends import default_backend
    >>> from cryptography.hazmat.primitives import hashes
    >>> from cryptography.hazmat.primitives.asymmetric import rsa, padding
    >>> private_key = rsa.generate_private_key(
    ...     public_exponent=65537,
    ...     key_size=2048,
    ...     backend=default_backend()
    ... )
    >>> signer = private_key.signer(
    ...     padding.PSS(
    ...         mgf=padding.MGF1(hashes.SHA256()),
    ...         salt_length=padding.PSS.MAX_LENGTH
    ...     ),
    ...     hashes.SHA256()
    ... )
    >>> signer.update(b"this is some data I'd like")
    >>> signer.update(b" to sign")
    >>> signature = signer.finalize()


Verification
~~~~~~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`
provider.

.. doctest::

    >>> public_key = private_key.public_key()
    >>> verifier = public_key.verifier(
    ...     signature,
    ...     padding.PSS(
    ...         mgf=padding.MGF1(hashes.SHA256()),
    ...         salt_length=padding.PSS.MAX_LENGTH
    ...     ),
    ...     hashes.SHA256()
    ... )
    >>> data = b"this is some data I'd like to sign"
    >>> verifier.update(data)
    >>> verifier.verify()

Encryption
~~~~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`
provider.

.. doctest::

    >>> from cryptography.hazmat.backends import default_backend
    >>> from cryptography.hazmat.primitives import hashes
    >>> from cryptography.hazmat.primitives.asymmetric import padding

    >>> # Generate a key
    >>> private_key = rsa.generate_private_key(
    ...     public_exponent=65537,
    ...     key_size=2048,
    ...     backend=default_backend()
    ... )
    >>> public_key = private_key.public_key()
    >>> # encrypt some data
    >>> ciphertext = public_key.encrypt(
    ...     b"encrypted data",
    ...     padding.OAEP(
    ...         mgf=padding.MGF1(algorithm=hashes.SHA1()),
    ...         algorithm=hashes.SHA1(),
    ...         label=None
    ...     )
    ... )

Decryption
~~~~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
provider.

.. doctest::

    >>> plaintext = private_key.decrypt(
    ...     ciphertext,
    ...     padding.OAEP(
    ...         mgf=padding.MGF1(algorithm=hashes.SHA1()),
    ...         algorithm=hashes.SHA1(),
    ...         label=None
    ...     )
    ... )

Numbers
~~~~~~~

These classes hold the constituent components of an RSA key. They are useful
only when more traditional :doc:`/hazmat/primitives/asymmetric/serialization`
is unavailable.

.. class:: RSAPublicNumbers(e, n)

    .. versionadded:: 0.5

    The collection of integers that make up an RSA public key.

    .. attribute:: n

        :type: int

        The public modulus.

    .. attribute:: e

        :type: int

        The public exponent.

    .. method:: public_key(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey`
            provider.

.. class:: RSAPrivateNumbers(p, q, d, dmp1, dmq1, iqmp, public_numbers)

    .. versionadded:: 0.5

    The collection of integers that make up an RSA private key.

    .. warning::

        With the exception of the integers contained in the
        :class:`RSAPublicNumbers` all attributes of this class must be kept
        secret. Revealing them will compromise the security of any
        cryptographic operations performed with a key loaded from them.

    .. attribute:: public_numbers

        :type: :class:`~cryptography.hazmat.primitives.rsa.RSAPublicNumbers`

        The :class:`RSAPublicNumbers` which makes up the RSA public key
        associated with this RSA private key.

    .. attribute:: p

        :type: int

        ``p``, one of the two primes composing the :attr:`modulus`.

    .. attribute:: q

        :type: int

        ``q``, one of the two primes composing the :attr:`modulus`.

    .. attribute:: d

        :type: int

        The private exponent. Alias for :attr:`private_exponent`.

    .. attribute:: dmp1

        :type: int

        A `Chinese remainder theorem`_ coefficient used to speed up RSA
        operations. Calculated as: d mod (p-1)

    .. attribute:: dmq1

        :type: int

        A `Chinese remainder theorem`_ coefficient used to speed up RSA
        operations. Calculated as: d mod (q-1)

    .. attribute:: iqmp

        :type: int

        A `Chinese remainder theorem`_ coefficient used to speed up RSA
        operations. Calculated as: q\ :sup:`-1` mod p

    .. method:: private_key(backend)

        :param backend: A new instance of a
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :returns: A
            :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey`
            provider.

Handling partial RSA private keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are trying to load RSA private keys yourself you may find that not all
parameters required by ``RSAPrivateNumbers`` are available. In particular the
`Chinese Remainder Theorem`_ (CRT) values ``dmp1``, ``dmq1``, ``iqmp`` may be
missing or present in a different form. For example `OpenPGP`_ does not include
the ``iqmp``, ``dmp1`` or ``dmq1`` parameters.

The following functions are provided for users who want to work with keys like
this without having to do the math themselves.

.. function:: rsa_crt_iqmp(p, q)

    .. versionadded:: 0.4

    Generates the ``iqmp`` (also known as ``qInv``) parameter from the RSA
    primes ``p`` and ``q``.

.. function:: rsa_crt_dmp1(private_exponent, p)

    .. versionadded:: 0.4

    Generates the ``dmp1`` parameter from the RSA private exponent and prime
    ``p``.

.. function:: rsa_crt_dmq1(private_exponent, q)

    .. versionadded:: 0.4

    Generates the ``dmq1`` parameter from the RSA private exponent and prime
    ``q``.

Deprecated Concrete Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

These classes were deprecated in version 0.5 in favor of backend specific
providers of the
:class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey` and
:class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey` interfaces.

.. class:: RSAPrivateKey(p, q, private_exponent, dmp1, dmq1, iqmp, public_exponent, modulus)

    .. versionadded:: 0.2

    .. deprecated:: 0.5

    An RSA private key is required for decryption and signing of messages.

    You should use :func:`generate_private_key` to generate new keys.

    .. warning::
        This method only checks a limited set of properties of its arguments.
        Using an RSA private key that you do not trust or with incorrect
        parameters may lead to insecure operation, crashes, and other undefined
        behavior. We recommend that you only ever load private keys that were
        generated with software you trust.


    :raises TypeError: This is raised when the arguments are not all integers.

    :raises ValueError: This is raised when the values of ``p``, ``q``,
                        ``private_exponent``, ``public_exponent``, or
                        ``modulus`` do not match the bounds specified in
                        :rfc:`3447`.

    .. classmethod:: generate(public_exponent, key_size, backend)

        Generate a new ``RSAPrivateKey`` instance using ``backend``.

        :param int public_exponent: The public exponent of the new key.
            Usually one of the small Fermat primes 3, 5, 17, 257, 65537. If in
            doubt you should `use 65537`_.
        :param int key_size: The length of the modulus in bits. For keys
            generated in 2014 it is strongly recommended to be
            `at least 2048`_ (See page 41). It must not be less than 512.
            Some backends may have additional limitations.
        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.
        :return: A new instance of ``RSAPrivateKey``.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`


    .. method:: signer(padding, algorithm, backend)

        .. versionadded:: 0.3

        Sign data which can be verified later by others using the public key.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider. Valid values are
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS` and
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15`
            (``PSS`` is recommended for all new applications).

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricSignatureContext`

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend` or if
            the backend does not support the chosen hash or padding algorithm.
            If the padding is
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS`
            with the
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
            mask generation function it may also refer to the ``MGF1`` hash
            algorithm.

        :raises TypeError: This is raised when the padding is not an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :raises ValueError: This is raised when the chosen hash algorithm is
            too large for the key size.

    .. method:: decrypt(ciphertext, padding, backend)

        .. versionadded:: 0.4

        Decrypt data that was encrypted with the public key.

        :param bytes ciphertext: The ciphertext to decrypt.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :return bytes: Decrypted data.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend` or if
            the backend does not support the chosen hash or padding algorithm.
            If the padding is
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.OAEP`
            with the
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
            mask generation function it may also refer to the ``MGF1`` hash
            algorithm.

        :raises TypeError: This is raised when the padding is not an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :raises ValueError: This is raised when decryption fails or the data
            is too large for the key size. If the padding is
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.OAEP`
            it may also be raised for invalid label values.


.. class:: RSAPublicKey(public_exponent, modulus)

    .. versionadded:: 0.2

    .. deprecated:: 0.5

    An RSA public key is required for encryption and verification of messages.

    Normally you do not need to directly construct public keys because you'll
    be loading them from a file, generating them automatically or receiving
    them from a 3rd party.

    :raises TypeError: This is raised when the arguments are not all integers.

    :raises ValueError: This is raised when the values of ``public_exponent``
                        or ``modulus`` do not match the bounds specified in
                        :rfc:`3447`.

    .. method:: verifier(signature, padding, algorithm, backend)

        .. versionadded:: 0.3

        Verify data was signed by the private key associated with this public
        key.

        :param bytes signature: The signature to verify.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider. Valid values are
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS` and
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15`
            (``PSS`` is recommended for all new applications).

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricVerificationContext`

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend` or if
            the backend does not support the chosen hash or padding algorithm.
            If the padding is
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS`
            with the
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
            mask generation function it may also refer to the ``MGF1`` hash
            algorithm.

        :raises TypeError: This is raised when the padding is not an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :raises ValueError: This is raised when the chosen hash algorithm is
            too large for the key size.

    .. method:: encrypt(plaintext, padding, backend)

        .. versionadded:: 0.4

        Encrypt data using the public key. The resulting ciphertext can only
        be decrypted with the private key.

        :param bytes plaintext: The plaintext to encrypt.

        :param padding: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend`
            provider.

        :return bytes: Encrypted data.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.RSABackend` or if
            the backend does not support the chosen hash or padding algorithm.
            If the padding is
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.OAEP`
            with the
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
            mask generation function it may also refer to the ``MGF1`` hash
            algorithm.

        :raises TypeError: This is raised when the padding is not an
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricPadding`
            provider.

        :raises ValueError: This is raised if the data is too large for the
            key size. If the padding is
            :class:`~cryptography.hazmat.primitives.asymmetric.padding.OAEP`
            it may also be raised for invalid label values.


.. _`RSA`: https://en.wikipedia.org/wiki/RSA_(cryptosystem)
.. _`public-key`: https://en.wikipedia.org/wiki/Public-key_cryptography
.. _`use 65537`: http://www.daemonology.net/blog/2009-06-11-cryptographic-right-answers.html
.. _`at least 2048`: http://www.ecrypt.eu.org/documents/D.SPA.20.pdf
.. _`OpenPGP`: https://en.wikipedia.org/wiki/Pretty_Good_Privacy
.. _`Chinese Remainder Theorem`: http://en.wikipedia.org/wiki/RSA_%28cryptosystem%29#Using_the_Chinese_remainder_algorithm
