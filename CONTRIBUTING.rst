Contributing
------------

If you find bugs, errors, omissions or other things that need improvement,
please create an issue or a pull request at
https://github.com/bastibe/PySoundFile/.
Contributions are always welcome!

Testing
^^^^^^^

If you fix a bug, you should add a test that exposes the bug (to avoid future
regressions), if you add a feature, you should add tests for it as well.

To run the tests, use::

   python setup.py test

This uses py.test_; if you haven't installed it already, it will be downloaded
and installed for you.

.. _py.test: http://pytest.org/

.. note:: There is a `known problem`_ that prohibits the use of file
   descriptors on Windows if the libsndfile DLL was compiled with a different
   compiler than the Python interpreter.
   Unfortunately, this is typically the case if the packaged DLLs are used.
   To skip the tests which utilize file descriptors, use::

      python setup.py test --pytest-args="-knot\ fd"

   .. _known problem: http://www.mega-nerd.com/libsndfile/api.html#open_fd

Coverage
^^^^^^^^

If you want to measure code coverage, you can use coverage.py_.
Just install it with::

   pip install coverage --user

... and run it with::

   coverage run --source soundfile.py -m py.test
   coverage html

The resulting HTML files will be written to the ``htmlcov/`` directory.

You can even check `branch coverage`_::

   coverage run --branch --source soundfile.py -m py.test
   coverage html

.. _coverage.py: http://nedbatchelder.com/code/coverage/
.. _branch coverage: http://nedbatchelder.com/code/coverage/branch.html

Documentation
^^^^^^^^^^^^^

If you make changes to the documentation, you can re-create the HTML pages
on your local system using Sphinx_.

.. _Sphinx: http://sphinx-doc.org/

You can install it and a few other necessary packages with::

   pip install -r doc/requirements.txt --user

To create the HTML pages, use::

   python setup.py build_sphinx

The generated files will be available in the directory ``build/sphinx/html/``.
