__all__ = ['formats', 'constants', 'module', 'tables', 'util']

def File(filename, options=None):
    """Guess the type of the file and try to open it. If no appropriate 
    type could be found, None is returned."""

    # Modified code from the Mutagen library (http://code.google.com/p/mutagen/)
    if options is None:
        from pymod.formats.IT import IT
        from pymod.formats.MOD import MOD
        from pymod.formats.S3M import S3M
        from pymod.formats.XM import XM
        options = [IT, MOD, S3M, XM]

    if not options:
        return None

    try:
        results = [(Kind.detect(filename), Kind.__name__) for Kind in options]
    finally:
        pass
    
    results = zip(results, options)
    results.sort()
    (score, name), Kind = results[-1]
    if score > 0: return Kind(filename)
    else: return None
