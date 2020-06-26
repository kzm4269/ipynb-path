ipynb-path
==========

A simple python package to get the path of the current IPython / Jupyter Notebook file.

Installation
------------

.. code:: bash

    pip install ipynb-path

Usage
-----

If you can access to your Jupyter Notebook/Lab server without a password, 
you can use just ``ipynb_path.get()`` in a ``.ipynb`` file.

.. code:: python

    import ipynb_path
    __file__ = ipynb_path.get()

If you need a password to access the server, you should specify it.

.. code:: python

    import ipynb_path
    __file__ = ipynb_path.get(password='foo')

You can also specify ``__name__`` for compatibility between ``.py`` and ``.ipynb``.
In this case, ``ipynb_path.get()`` does not overwrite ``__file__`` even if it is called in a ``.py`` file.

.. code:: python

    import ipynb_path
    __file__ = ipynb_path.get(__name__)
