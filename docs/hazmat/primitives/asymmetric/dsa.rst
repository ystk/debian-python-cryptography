.. hazmat::

DSA
===

.. currentmodule:: cryptography.hazmat.primitives.asymmetric.dsa

`DSA`_ is a `public-key`_ algorithm for signing messages.

Generation
~~~~~~~~~~

.. function:: generate_private_key(key_size, backend)

    .. versionadded:: 0.5

    Generate a DSA private key from the given key size. This function will
    generate a new set of parameters and key in one step.

    :param int key_size: The length of the modulus in bits. It should be
        either 1024, 2048 or 3072. For keys generated in 2014 this should
        be `at least 2048`_ (See page 41).  Note that some applications
        (such as SSH) have not yet gained support for larger key sizes
        specified in FIPS 186-3 and are still restricted to only the
        1024-bit keys specified in FIPS 186-2.

    :param backend: A
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
        provider.

    :return: A :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
        provider.

    :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
        the provided ``backend`` does not implement
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`

.. function:: generate_parameters(key_size, backend)

    .. versionadded:: 0.5

    Generate DSA parameters using the provided ``backend``.

    :param int key_size: The length of the modulus in bits. It should be
        either 1024, 2048 or 3072. For keys generated in 2014 this should
        be `at least 2048`_ (See page 41).  Note that some applications
        (such as SSH) have not yet gained support for larger key sizes
        specified in FIPS 186-3 and are still restricted to only the
        1024-bit keys specified in FIPS 186-2.

    :param backend: A
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
        provider.

    :return: A :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
        provider.

    :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
        the provided ``backend`` does not implement
        :class:`~cryptography.hazmat.backends.interfaces.DSABackend`

Signing
~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
provider.

.. doctest::

    >>> from cryptography.hazmat.backends import default_backend
    >>> from cryptography.hazmat.primitives import hashes
    >>> from cryptography.hazmat.primitives.asymmetric import dsa
    >>> private_key = dsa.generate_private_key(
    ...     key_size=1024,
    ...     backend=default_backend()
    ... )
    >>> signer = private_key.signer(hashes.SHA256())
    >>> data = b"this is some data I'd like to sign"
    >>> signer.update(data)
    >>> signature = signer.finalize()

Verification
~~~~~~~~~~~~

Using a :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`
provider.

.. doctest::

    >>> public_key = private_key.public_key()
    >>> verifier = public_key.verifier(signature, hashes.SHA256())
    >>> verifier.update(data)
    >>> verifier.verify()

Numbers
~~~~~~~

.. class:: DSAParameterNumbers(p, q, g)

    .. versionadded:: 0.5

    The collection of integers that make up a set of DSA parameters.

    .. attribute:: p

        :type: int

        The public modulus.

    .. attribute:: q

        :type: int

        The sub-group order.

    .. attribute:: g

        :type: int

        The generator.

    .. method:: parameters(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
            provider.

.. class:: DSAPublicNumbers(y, parameter_numbers)

    .. versionadded:: 0.5

    The collection of integers that make up a DSA public key.

    .. attribute:: y

        :type: int

        The public value ``y``.

    .. attribute:: parameter_numbers

        :type: :class:`~cryptography.hazmat.primitives.dsa.DSAParameterNumbers`

        The :class:`~cryptography.hazmat.primitives.dsa.DSAParameterNumbers`
        associated with the public key.

    .. method:: public_key(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`
            provider.

.. class:: DSAPrivateNumbers(x, public_numbers)

    .. versionadded:: 0.5

    The collection of integers that make up a DSA private key.

    .. warning::

        Revealing the value of ``x`` will compromise the security of any
        cryptographic operations performed.

    .. attribute:: x

        :type: int

        The private value ``x``.

    .. attribute:: public_numbers

        :type: :class:`~cryptography.hazmat.primitives.dsa.DSAPublicNumbers`

        The :class:`~cryptography.hazmat.primitives.dsa.DSAPublicNumbers`
        associated with the private key.

    .. method:: private_key(backend)

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns: A new instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
            provider.

Deprecated Concrete Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

These classes were deprecated in version 0.5 in favor of backend specific
providers of the
:class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`,
:class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`, and
:class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey` interfaces.

.. class:: DSAParameters(modulus, subgroup_order, generator)

    .. versionadded:: 0.4

    .. deprecated:: 0.5

    DSA Parameters are required for generating a DSA private key.

    You should use :meth:`~generate` to generate new parameters.

    .. warning::
        This method only checks a limited set of properties of its arguments.
        Using DSA parameters that you do not trust or with incorrect arguments
        may lead to insecure operation, crashes, and other undefined behavior.
        We recommend that you only ever load parameters that were generated
        with software you trust.


    This class conforms to the
    :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
    interface.

    :raises TypeError: This is raised when the arguments are not all integers.

    :raises ValueError: This is raised when the values of ``modulus``,
                        ``subgroup_order``, or ``generator`` do
                        not match the bounds specified in `FIPS 186-4`_.

    .. classmethod:: generate(key_size, backend)

        Generate a new ``DSAParameters`` instance using ``backend``.

        :param int key_size: The length of the modulus in bits. It should be
            either 1024, 2048 or 3072. For keys generated in 2014 this should
            be `at least 2048`_ (See page 41).  Note that some applications
            (such as SSH) have not yet gained support for larger key sizes
            specified in FIPS 186-3 and are still restricted to only the
            1024-bit keys specified in FIPS 186-2.

        :return: A new instance of ``DSAParameters``

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`


.. class:: DSAPrivateKey(modulus, subgroup_order, generator, x, y)

    .. versionadded:: 0.4

    .. deprecated:: 0.5

    A DSA private key is required for signing messages.

    You should use :meth:`~generate` to generate new keys.

    .. warning::
        This method only checks a limited set of properties of its arguments.
        Using a DSA private key that you do not trust or with incorrect
        parameters may lead to insecure operation, crashes, and other undefined
        behavior. We recommend that you only ever load private keys that were
        generated with software you trust.


    This class conforms to the
    :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey`
    interface.

    :raises TypeError: This is raised when the arguments are not all integers.

    :raises ValueError: This is raised when the values of ``modulus``,
                        ``subgroup_order``, or ``generator`` do
                        not match the bounds specified in `FIPS 186-4`_.

    .. classmethod:: generate(parameters, backend)

        Generate a new ``DSAPrivateKey`` instance using ``backend``.

        :param parameters: A
            :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters`
            provider.
        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.
        :return: A new instance of ``DSAPrivateKey``.

        :raises cryptography.exceptions.UnsupportedAlgorithm: This is raised if
            the provided ``backend`` does not implement
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`

        :raises ValueError: This is raised if the key size is not (1024 or 2048 or 3072)
            or if the OpenSSL version is older than 1.0.0 and the key size is larger than 1024
            because older OpenSSL versions don't support a key size larger than 1024.

    .. method:: signer(algorithm, backend)

        .. versionadded:: 0.4

        Sign data which can be verified later by others using the public key.

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
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`


.. class:: DSAPublicKey(modulus, subgroup_order, generator, y)

    .. versionadded:: 0.4

    .. deprecated:: 0.5

    A DSA public key is required for verifying messages.

    Normally you do not need to directly construct public keys because you'll
    be loading them from a file, generating them automatically or receiving
    them from a 3rd party.

    This class conforms to the
    :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey`
    interface.

    :raises TypeError: This is raised when the arguments are not all integers.

    :raises ValueError: This is raised when the values of ``modulus``,
                        ``subgroup_order``, ``generator``, or ``y``
                        do not match the bounds specified in `FIPS 186-4`_.

    .. method:: verifier(signature, algorithm, backend)

        .. versionadded:: 0.4

        Verify data was signed by the private key associated with this public
        key.

        :param bytes signature: The signature to verify. DER encoded as
            specified in :rfc:`6979`.

        :param algorithm: An instance of a
            :class:`~cryptography.hazmat.primitives.interfaces.HashAlgorithm`
            provider.

        :param backend: A
            :class:`~cryptography.hazmat.backends.interfaces.DSABackend`
            provider.

        :returns:
            :class:`~cryptography.hazmat.primitives.interfaces.AsymmetricVerificationContext`

.. _`DSA`: https://en.wikipedia.org/wiki/Digital_Signature_Algorithm
.. _`public-key`: https://en.wikipedia.org/wiki/Public-key_cryptography
.. _`FIPS 186-4`: http://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf
.. _`at least 2048`: http://www.ecrypt.eu.org/documents/D.SPA.20.pdf
