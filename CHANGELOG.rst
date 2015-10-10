Changelog
=========

0.6.1 - 2014-10-15
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.1j.
* Fixed an issue where OpenSSL 1.0.1j changed the errors returned by some
  functions.
* Added our license file to the ``cryptography-vectors`` package.
* Implemented DSA hash truncation support (per FIPS 186-3) in the OpenSSL
  backend. This works around an issue in 1.0.0, 1.0.0a, and 1.0.0b where
  truncation was not implemented.

0.6 - 2014-09-29
~~~~~~~~~~~~~~~~

* Added
  :func:`~cryptography.hazmat.primitives.serialization.load_pem_private_key` to
  ease loading private keys, and
  :func:`~cryptography.hazmat.primitives.serialization.load_pem_public_key` to
  support loading public keys.
* Removed the, deprecated in 0.4, support for the ``salt_length`` argument to
  the :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1`
  constructor. The ``salt_length`` should be passed to
  :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS` instead.
* Fix compilation on OS X Yosemite.
* Deprecated ``elliptic_curve_private_key_from_numbers`` and
  ``elliptic_curve_public_key_from_numbers`` in favor of
  ``load_elliptic_curve_private_numbers`` and
  ``load_elliptic_curve_public_numbers`` on
  :class:`~cryptography.hazmat.backends.interfaces.EllipticCurveBackend`.
* Added
  :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurvePrivateKeyWithNumbers`
  and
  :class:`~cryptography.hazmat.primitives.interfaces.EllipticCurvePublicKeyWithNumbers`
  support.
* Work around three GCM related bugs in CommonCrypto and OpenSSL.

  * On the CommonCrypto backend adding AAD but not subsequently calling update
    would return null tag bytes.

  * One the CommonCrypto backend a call to update without an empty add AAD call
    would return null ciphertext bytes.

  * On the OpenSSL backend with certain versions adding AAD only would give
    invalid tag bytes.

* Support loading EC private keys from PEM.

0.5.4 - 2014-08-20
~~~~~~~~~~~~~~~~~~

* Added several functions to the OpenSSL bindings to support new
  functionality in pyOpenSSL.
* Fixed a redefined constant causing compilation failure with Solaris 11.2.

0.5.3 - 2014-08-06
~~~~~~~~~~~~~~~~~~

* Updated Windows wheels to be compiled against OpenSSL 1.0.1i.

0.5.2 - 2014-07-09
~~~~~~~~~~~~~~~~~~

* Add
  :class:`~cryptography.hazmat.backends.interfaces.TraditionalOpenSSLSerializationBackend`
  support to :doc:`/hazmat/backends/multibackend`.
* Fix compilation error on OS X 10.8 (Mountain Lion).

0.5.1 - 2014-07-07
~~~~~~~~~~~~~~~~~~

* Add
  :class:`~cryptography.hazmat.backends.interfaces.PKCS8SerializationBackend`
  support to :doc:`/hazmat/backends/multibackend`.

0.5 - 2014-07-07
~~~~~~~~~~~~~~~~

* **BACKWARDS INCOMPATIBLE:**
  :class:`~cryptography.hazmat.primitives.ciphers.modes.GCM` no longer allows
  truncation of tags by default. Previous versions of ``cryptography`` allowed
  tags to be truncated by default, applications wishing to preserve this
  behavior (not recommended) can pass the ``min_tag_length`` argument.
* Windows builds now statically link OpenSSL by default. When installing a
  wheel on Windows you no longer need to install OpenSSL separately. Windows
  users can switch between static and dynamic linking with an environment
  variable. See :doc:`/installation` for more details.
* Added :class:`~cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand`.
* Added :class:`~cryptography.hazmat.primitives.ciphers.modes.CFB8` support
  for :class:`~cryptography.hazmat.primitives.ciphers.algorithms.AES` and
  :class:`~cryptography.hazmat.primitives.ciphers.algorithms.TripleDES` on
  :doc:`/hazmat/backends/commoncrypto` and :doc:`/hazmat/backends/openssl`.
* Added ``AES`` :class:`~cryptography.hazmat.primitives.ciphers.modes.CTR`
  support to the OpenSSL backend when linked against 0.9.8.
* Added
  :class:`~cryptography.hazmat.backends.interfaces.PKCS8SerializationBackend`
  and
  :class:`~cryptography.hazmat.backends.interfaces.TraditionalOpenSSLSerializationBackend`
  support to the :doc:`/hazmat/backends/openssl`.
* Added :doc:`/hazmat/primitives/asymmetric/ec` and
  :class:`~cryptography.hazmat.backends.interfaces.EllipticCurveBackend`.
* Added :class:`~cryptography.hazmat.primitives.ciphers.modes.ECB` support
  for :class:`~cryptography.hazmat.primitives.ciphers.algorithms.TripleDES` on
  :doc:`/hazmat/backends/commoncrypto` and :doc:`/hazmat/backends/openssl`.
* Deprecated
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey` in
  favor of backend specific providers of the
  :class:`~cryptography.hazmat.primitives.interfaces.RSAPrivateKey` interface.
* Deprecated
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey` in favor
  of backend specific providers of the
  :class:`~cryptography.hazmat.primitives.interfaces.RSAPublicKey` interface.
* Deprecated
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKey` in
  favor of backend specific providers of the
  :class:`~cryptography.hazmat.primitives.interfaces.DSAPrivateKey` interface.
* Deprecated
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKey` in favor
  of backend specific providers of the
  :class:`~cryptography.hazmat.primitives.interfaces.DSAPublicKey` interface.
* Deprecated
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAParameters` in
  favor of backend specific providers of the
  :class:`~cryptography.hazmat.primitives.interfaces.DSAParameters` interface.
* Deprecated ``encrypt_rsa``, ``decrypt_rsa``, ``create_rsa_signature_ctx`` and
  ``create_rsa_verification_ctx`` on
  :class:`~cryptography.hazmat.backends.interfaces.RSABackend`.
* Deprecated ``create_dsa_signature_ctx`` and ``create_dsa_verification_ctx``
  on :class:`~cryptography.hazmat.backends.interfaces.DSABackend`.

0.4 - 2014-05-03
~~~~~~~~~~~~~~~~

* Deprecated ``salt_length`` on
  :class:`~cryptography.hazmat.primitives.asymmetric.padding.MGF1` and added it
  to :class:`~cryptography.hazmat.primitives.asymmetric.padding.PSS`. It will
  be removed from ``MGF1`` in two releases per our :doc:`/api-stability`
  policy.
* Added :class:`~cryptography.hazmat.primitives.ciphers.algorithms.SEED`
  support.
* Added :class:`~cryptography.hazmat.primitives.cmac.CMAC`.
* Added decryption support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
  and encryption support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`.
* Added signature support to
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPrivateKey`
  and verification support to
  :class:`~cryptography.hazmat.primitives.asymmetric.dsa.DSAPublicKey`.

0.3 - 2014-03-27
~~~~~~~~~~~~~~~~

* Added :class:`~cryptography.hazmat.primitives.twofactor.hotp.HOTP`.
* Added :class:`~cryptography.hazmat.primitives.twofactor.totp.TOTP`.
* Added :class:`~cryptography.hazmat.primitives.ciphers.algorithms.IDEA`
  support.
* Added signature support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey`
  and verification support to
  :class:`~cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey`.
* Moved test vectors to the new ``cryptography_vectors`` package.

0.2.2 - 2014-03-03
~~~~~~~~~~~~~~~~~~

* Removed a constant definition that was causing compilation problems with
  specific versions of OpenSSL.

0.2.1 - 2014-02-22
~~~~~~~~~~~~~~~~~~

* Fix a bug where importing cryptography from multiple paths could cause
  initialization to fail.

0.2 - 2014-02-20
~~~~~~~~~~~~~~~~

* Added :doc:`/hazmat/backends/commoncrypto`.
* Added initial :doc:`/hazmat/bindings/commoncrypto`.
* Removed ``register_cipher_adapter`` method from
  :class:`~cryptography.hazmat.backends.interfaces.CipherBackend`.
* Added support for the OpenSSL backend under Windows.
* Improved thread-safety for the OpenSSL backend.
* Fixed compilation on systems where OpenSSL's ``ec.h`` header is not
  available, such as CentOS.
* Added :class:`~cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC`.
* Added :class:`~cryptography.hazmat.primitives.kdf.hkdf.HKDF`.
* Added :doc:`/hazmat/backends/multibackend`.
* Set default random for the :doc:`/hazmat/backends/openssl` to the OS
  random engine.
* Added :class:`~cryptography.hazmat.primitives.ciphers.algorithms.CAST5`
  (CAST-128) support.

0.1 - 2014-01-08
~~~~~~~~~~~~~~~~

* Initial release.

.. _`master`: https://github.com/pyca/cryptography/
