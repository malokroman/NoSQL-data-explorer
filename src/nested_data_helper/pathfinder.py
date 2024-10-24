from typing import Callable, Iterable

from .navigation import navigate


def find_paths(
    list_or_dict: list | dict,
    path_include: str = "",
    *,
    start_from: str = "",
    use_list_index: bool = False,
    ignore_case: bool = True,
    _prefix: str = "",
) -> Iterable[tuple[str, type]]:
    """Yield the paths and their return type in a json-like structure.

    :param list_or_dict    The structure you want to inspect
    :param path_include    Yield the paths only if the last key has this str in it. Default show all keys.
    :param start_from      A path to tell this function what subset of data to look at. Default at the root.
    :param use_list_index  Whether to show the list index or not in the paths. Default False.
    :param ignore_case     Whether to ignore the case is path_include. Default True.

    :param _prefix       Used for development only. Do not use this param.

    >>> from collections import Counter
    >>> data = {
    ...  "results": [
    ...   {"type": "type_i",
    ...    "instances": [
    ...    {"id": "i_0", "name": "hello", "Favourite": "world"},
    ...    {"id": "i_1", "name": "world", "Favourite": "hello", "i1": "unique_attribute"},
    ...   ]},
    ...   {"type": "type_ii",
    ...    "instances": [
    ...    {"id": 0, "name": "hello", "Least favourite": "oh my"},
    ...    {"id": 1, "name": "oh my", "Least favourite": "world"},
    ...    ]},
    ...  ],
    ...  "meta": {
    ...    "status": 200,
    ...    "referrer": ["referrer1", "referrer2", "referrer3"]
    ...  },
    ... }

    >>> Counter(find_paths(data)).most_common(3)
    [(('results.[].instances.[]', <class 'dict'>), 4), (('results.[].instances.[].name', <class 'str'>), 4), (('meta.referrer.[]', <class 'str'>), 3)]

    >>> Counter(find_paths(data, start_from="results")).most_common(3)
    [(('results.[].instances.[]', <class 'dict'>), 4), (('results.[].instances.[].name', <class 'str'>), 4), (('results.[]', <class 'dict'>), 2)]

    >>> list(find_paths(data, "id"))
    [('results.[].instances.[].id', <class 'str'>), ('results.[].instances.[].id', <class 'str'>), ('results.[].instances.[].id', <class 'int'>), ('results.[].instances.[].id', <class 'int'>)]

    >>> list(find_paths(data, "name", use_list_index=True))
    [('results.[0].instances.[0].name', <class 'str'>), ('results.[0].instances.[1].name', <class 'str'>), ('results.[1].instances.[0].name', <class 'str'>), ('results.[1].instances.[1].name', <class 'str'>)]

    >>> list(find_paths(data, "name", start_from="meta"))
    []

    >>> list(find_paths(data, "favourite"))
    [('results.[].instances.[].Favourite', <class 'str'>), ('results.[].instances.[].Favourite', <class 'str'>), ('results.[].instances.[].Least favourite', <class 'str'>), ('results.[].instances.[].Least favourite', <class 'str'>)]

    >>> list(find_paths(data, "favourite", ignore_case=False))
    [('results.[].instances.[].Least favourite', <class 'str'>), ('results.[].instances.[].Least favourite', <class 'str'>)]

    >>> list(find_paths(data, "Favourite", ignore_case=False, use_list_index=True))
    [('results.[0].instances.[0].Favourite', <class 'str'>), ('results.[0].instances.[1].Favourite', <class 'str'>)]

    >>> list(find_paths(data, "favourite", start_from="results.[0]", ignore_case=False))
    []
    """
    if start_from:
        list_or_dict = navigate(list_or_dict, start_from)
        _prefix += start_from + "."
        # the [] will be added again for list, delete duplicate here
        if _prefix.endswith("[]."):
            _prefix = _prefix[:-3]

    if ignore_case:
        path_include = path_include.lower()

    if isinstance(list_or_dict, list):
        if use_list_index:
            iterable = ((f"[{i}]", item) for i, item in enumerate(list_or_dict))
        else:
            iterable = (("[]", item) for item in list_or_dict)
    elif isinstance(list_or_dict, dict):
        iterable = list_or_dict.items()
    else:
        return

    for k, v in iterable:
        path = f"{_prefix}{k}"

        if ignore_case:
            k = k.lower()

        if path_include in k:
            yield (path, type(v))

        yield from find_paths(
            v,
            path_include,
            _prefix=f"{path}.",
            use_list_index=use_list_index,
            ignore_case=ignore_case,
        )


def find_paths_unique(
    list_or_dict: list | dict,
    path_include: str = "",
    *,
    start_from: str = "",
    ignore_case: bool = True,
    _prefix: str = "",
) -> Iterable[tuple[str, type]]:
    """find_paths but all the paths are unique. Order is not guaranteed and list index is not supported.

    >>> data = {
    ...  "results": [
    ...   {"type": "type_i",
    ...    "instances": [
    ...    {"id": "i_0", "name": "hello", "Favourite": "world"},
    ...    {"id": "i_1", "name": "world", "Favourite": "hello", "i1": "unique_attribute"},
    ...   ]},
    ...   {"type": "type_ii",
    ...    "instances": [
    ...    {"id": 0, "name": "hello", "Least favourite": "oh my"},
    ...    {"id": 1, "name": "oh my", "Least favourite": "world"},
    ...    ]},
    ...  ],
    ...  "meta": {
    ...    "status": 200,
    ...    "referrer": ["referrer1", "referrer2", "referrer3"]
    ...  },
    ... }

    >>> sum(1 for _ in find_paths(data))
    30
    >>> sum(1 for _ in find_paths_unique(data))
    15

    >>> list(find_paths_unique(data, 'name'))
    [('results.[].instances.[].name', <class 'str'>)]

    >>> sorted(find_paths_unique(data, 'id', start_from='results'), key=lambda x: str(x))
    [('results.[].instances.[].id', <class 'int'>), ('results.[].instances.[].id', <class 'str'>)]

    >>> list(find_paths_unique(data, 'id', start_from='meta'))
    []
    """
    return set(
        find_paths(
            list_or_dict,
            path_include,
            start_from=start_from,
            ignore_case=ignore_case,
            _prefix=_prefix,
        )
    )


def find_paths_unique_per_doc(
    docs: list[list | dict],
    path_includes: str = "",
    *,
    start_from: str = "",
    ignore_case: bool = True,
    _prefix: str = "",
) -> Iterable[tuple[str, type]]:
    """Wrapper for find_paths_unique and make it unique per doc,
    which means counting how many docs have these paths without inflating paths with many values within a doc.

    >>> data = {
    ...  "results": [
    ...   {"type": "type_i",
    ...    "instances": [
    ...      {"id": "i_0", "name": "hello", "Favourite": "world"},
    ...      {"id": "i_1", "name": "world", "Favourite": "hello", "i1": "unique_attribute"},
    ...   ]},
    ...   {"type": "type_ii",
    ...    "instances": [
    ...      {"id": 0, "name": "hello", "Least favourite": "oh my", "Three": [{"deep": 1}, {"deep": 2}, {"deep": 3}]},
    ...      {"id": 1, "name": "oh my", "Least favourite": "world", "Three": [{"deep": 1}, {"deep": 2}, {"deep": 3}]},
    ...    ]},
    ... ],
    ...  "meta": {
    ...    "status": 200,
    ...    "referrer": ["referrer1", "referrer2", "referrer3"]
    ...  },
    ... }

    >>> len(list(find_paths(data, "deep")))
    6

    >>> len(list(find_paths_unique(data, "deep")))
    1

    >>> len(list(find_paths_unique_per_doc(data, "deep")))
    Traceback (most recent call last):
    ValueError: You need to start from a list.

    >>> len(list(find_paths_unique_per_doc(data, "deep", start_from='results')))
    1

    >>> list(find_paths_unique_per_doc(data, "deep", start_from='results'))
    [('results.[].instances.[].Three.[].deep', <class 'int'>)]

    >>> len(list(find_paths_unique_per_doc(data, "deep", start_from='results.[].instances')))
    2

    >>> len(list(find_paths_unique_per_doc(data, "deep", start_from='results.[].instances.[].Three')))
    6

    >>> len(list(find_paths_unique_per_doc([data, data], "deep")))
    2

    """
    if start_from:
        docs = navigate(docs, start_from)
        _prefix += start_from + "."
        if not _prefix.endswith("[]."):
            _prefix += "[]."
    if isinstance(docs, dict):
        raise ValueError("You need to start from a list.")
    for doc in docs:
        yield from find_paths_unique(
            doc, path_includes, ignore_case=ignore_case, _prefix=_prefix
        )


def find_value[T](
    list_or_dict: list | dict,
    value_finder: Callable[[T], bool],
    *,
    start_from: str = "",
    ignore_finder_error: bool = True,
    ignore_unknown_iterable: bool = False,
    _prefix: str = "",
) -> Iterable[tuple[str, T]]:
    r"""Yield all paths and value where value_finder(value) returns a True value.
    Any error is treated as False if ignore_finder_error is set to True.

    >>> data = {"top_level": {
    ...         "results": [{"name": "World", "id": 0}, {"name": "What", "id": 1, "only_me": "Yah"}],
    ...         "meta": {"type": "None",
    ...           "lists": [{"name": "one", "elements": ["one"]},
    ...                     {"name": "two", "elements": ["two", "three"]}]},
    ...        }}

    >>> list(find_value(data, lambda x: isinstance(x, int)))
    [('top_level.results.[0].id', 0), ('top_level.results.[1].id', 1)]

    >>> list(find_value(data, lambda x: 'one' in x.lower()))
    [('top_level.meta.type', 'None'), ('top_level.meta.lists.[0].name', 'one'), ('top_level.meta.lists.[0].elements.[0]', 'one')]

    >>> import re
    >>> list(find_value(data, lambda x: re.search(r'\bone\b', x, re.I)))
    [('top_level.meta.lists.[0].name', 'one'), ('top_level.meta.lists.[0].elements.[0]', 'one')]

    >>> list(find_value(data, lambda x: re.search(r'\bone\b', x, re.I), ignore_finder_error=False))
    Traceback (most recent call last):
    TypeError: expected string or bytes-like object, got 'dict'

    >>> list(find_value({'a', 'set', 'of', 'data'}, lambda x: True))
    Traceback (most recent call last):
    NotImplementedError: Iterable type <class 'set'> is not handled
    """
    if start_from:
        list_or_dict = navigate(list_or_dict, start_from)
        _prefix += start_from + "."
        # the [] will be added again for list, delete duplicate here
        if _prefix.endswith("[]."):
            _prefix = _prefix[:-3]

    if isinstance(list_or_dict, list):
        iterable = ((f"[{i}]", item) for i, item in enumerate(list_or_dict))
    elif isinstance(list_or_dict, dict):
        iterable = list_or_dict.items()
    elif (
        not ignore_unknown_iterable
        and isinstance(list_or_dict, Iterable)
        and not isinstance(list_or_dict, str)
    ):
        raise NotImplementedError(f"Iterable type {type(list_or_dict)} is not handled")
    else:
        return

    for k, v in iterable:
        path = f"{_prefix}{k}"
        try:
            if value_finder(v):
                yield (path, v)
        except Exception:
            if not ignore_finder_error:
                raise

        yield from find_value(
            v,
            value_finder,
            _prefix=f"{path}.",
        )
