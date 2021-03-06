python-pass
###########

.. image:: https://travis-ci.org/ReAzem/python-pass.svg?branch=master
    :target: https://travis-ci.org/ReAzem/python-pass

.. image:: https://img.shields.io/coveralls/ReAzem/python-pass.svg
  :target: https://coveralls.io/r/ReAzem/python-pass?branch=master

.. image:: https://readthedocs.org/projects/pypass/badge/?version=latest&style
    :target: http://pypass.readthedocs.org
    :alt: Documentation Status


.. image:: https://pypip.in/version/pypass/badge.svg
    :target: https://pypi.python.org/pypi/pypass/
    :alt: Latest Version

For fun, I have decided to write `pass <http://www.passwordstore.org/>`_ in Python.

Testing
+++++++

Python-pass is tested for python 2.7, 3.2, 3.3, 3.4, pypy and pypy3

On your machine
---------------

- Install the requirements: ``sudo apt-get install -y gnupg tree``
- Import the testing GPG key: ``gpg --allow-secret-key-import --import pypass/tests/test_key_sec.asc``
- Trust the key: ``gpg --import-ownertrust pypass/tests/test_ownertrust.txt``
- Run the tests: ``tox``


With Docker
-----------

- Run the tests in a container: ``make test``
- Or, get a shell with pypass installed: ``make run``

Documentation
+++++++++++++

Documentation for python-pass is available on `pypass.rtfd.org <http://pypass.readthedocs.org/>`_.

You can build the documentation and the man page yourself with ``tox -edocs``. The HTML documentation will be built in ``docs/build/html`` and the man page will be built in ``docs/build/man``.

Project Status
++++++++++++++

``pypass init``
---------------

- [X] ``pypass init`` -  creates a folder and a .gpg-id file
- [X] Support ``--path`` option
- [ ] re-encryption functionality
- [X] Should output: ``Password store initialized for [gpg-id].``

``pypass insert``
-----------------

- [X] ``pypass insert test.com`` prompts for a password and creates a test.com.gpg file
- [ ] multi-line support
- [ ] create a git commit

``pypass show``
---------------

- [X] ``pypass show test.com`` will display the content of test.com.gpg
- [ ] ``--clip, -c`` copies the first line to the clipboard

``pypass ls``
-------------

- [X] ``pypass ls`` shows the content of the password store with ``tree``
- [X] ``pypass`` invokes ``pypass ls`` by default
- [X] ``pypass ls subfolder`` calls tree on the subfolder only
- [X] Hide .gpg at the end of each entry
- [ ] Accept subfolder argument
- [ ] First output line should be ``Password Store``

``pypass rm``
-------------

- [X] ``pypass rm test.com`` removes the test.com.gpg file
- [ ] ``pypass remove`` and ``pypass delete`` aliases
- [X] ``pypass rm -r folder`` (or ``--recursive``)  will remove a folder and all of it's content (not interactive!)
- [ ] Ask for confirmation

``pypass find``
---------------

- [X] ``pypass find python.org pypass`` will show a tree with password entries that match python.org or pass
- [X] Accepts one or many search terms

``pypass cp``
-------------

- [ ] ``pypass cp old-path new-pah`` copies a password to a new path

``pypass mv``
-------------

- [X] ``pypass mv old-path new-path`` moves a password to a new path

``pypass git``
--------------

- [X] Pass commands to git
- [X] ``pypass git init`` should behave differently with an existing password store
- [X] Add tests
