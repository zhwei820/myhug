def u_(s):
    if isinstance(s, unicode):
        return s
    if not isinstance(s, str):
        s = str(s)
    return unicode(s, 'utf-8')


def generate_key_for_cached_func(key_prefix, func, *args, **kwargs):
    """Generate key for cached function. The cache key will be created with
    the name of the module + the name of the function + function arguments.
    """
    if key_prefix is None:
        key_prefix = []
    else:
        key_prefix = [key_prefix]
    module_name = func.__module__
    func_name = func.__name__
    # handle keyword arguments
    kwargs = kwargs.items()
    if kwargs:
        kwargs.sort(key=lambda t: t[0])
        kwargs = map(lambda t: (u_(t[0]), u_(t[1])), kwargs)
        kwargs = map(lambda t: u'='.join(t), kwargs)
    # handle positional arguments
    args = [str(x) for x in args]
    # join them together
    return '_'.join(key_prefix + [module_name, func_name] + args)
