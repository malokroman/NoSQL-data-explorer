def navigate(list_or_dict: list | dict, path: str | list[str]):
    """This function navigate through the dictionary or list using the defined path structure.

    Path has keys split by "." and will navigate into it.
    List are noted by [] with an optional index inside.
    If the index is not provided, it iterates through the whole list.

    Note that this might not work as expected if some of the keys include "."
    or are surrounded by square brackets "[]".

    >>> data = {"top_level": {
    ...         "results": [{"name": "World", "id": 0}, {"name": "What", "id": 1, "only_me": "Yah"}],
    ...         "meta": {"type": "None",
    ...                  "lists": [{"name": "one", "elements": ["one"]},
    ...                            {"name": "two", "elements": ["two", "three"]}]},
    ...       }}

    >>> navigate(data, "top_level.results")
    [{'name': 'World', 'id': 0}, {'name': 'What', 'id': 1, 'only_me': 'Yah'}]

    >>> navigate(data, "top_level.results.[].name")
    ['World', 'What']

    >>> navigate(data, "top_level.results.[].only_me")
    ['Yah']

    >>> navigate(data, "top_level.results.[0].only_me")
    Traceback (most recent call last):
    KeyError: 'only_me'

    >>> navigate(data, "top_level.results.[1].only_me")
    'Yah'

    >>> navigate(data, "top_level.results.[].notexist")
    []

    >>> navigate(data, "top_level.[]")
    Traceback (most recent call last):
    TypeError: top_level is a dict and not a list
    """
    curr = list_or_dict
    if isinstance(path, str):
        path = path.split(".")

    for i, subpath in enumerate(path):
        if subpath.startswith("[") and subpath.endswith("]"):
            if isinstance(curr, dict):
                path_to = ".".join(path[:i])
                raise TypeError(f"{path_to} is a dict and not a list")
            subpath = subpath[1:-1]
            if subpath == "":  # []: Iterate through list
                result = []
                remaining_path = path[i + 1 :]
                for item in curr:
                    try:
                        navigated = navigate(item, remaining_path)
                        if isinstance(navigated, list):
                            result += navigated
                        else:
                            result.append(navigated)
                    except KeyError:
                        pass
                return result

            else:
                try:
                    curr = curr[int(subpath)]
                except ValueError:
                    raise ValueError(
                        f'Expect empty "[]" or an integer index in square brackets, get "[{subpath}]"'
                    )
        else:
            curr = curr[subpath]
    return curr
