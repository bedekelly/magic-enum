from contextlib import contextmanager
import importlib

@contextmanager
def patch(pathspec, patch_object):
    import_failed = False
    try:
        # Import our module from the given path.
        module_name, _, object_name = pathspec.rpartition(".")
        module = importlib.import_module(module_name)

        # Save the original object to which the name was bound.
        original = getattr(module, object_name)

        # Set the name to our new object.
        setattr(module, object_name, patch_object)
        yield patch_object
        
    except ImportError:
        import_failed = True
        raise

    finally:
        # Restore the original object to the given path.
        if not import_failed:
            setattr(module, object_name, original)
