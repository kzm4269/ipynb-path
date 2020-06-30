def get(name='__main__', password=None):
    import sys
    try:
        return sys.modules[name].__file__
    except AttributeError:
        from . import core
        return core.current_notebook_path(password=password)
