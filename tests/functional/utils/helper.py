def find_item_in_dict(obj={}, search_key=""):
    """
    Recursively searchs through a dictionary for the key provided and returns its value
    Args:
        obj (dict): the object to search through
        key (string): the key to find
    """
    if search_key in obj:
        return obj[search_key]

    for key, val in obj.items():
        if isinstance(val, dict):
            item = find_item_in_dict(val, search_key)
            if item is not None:
                return item
