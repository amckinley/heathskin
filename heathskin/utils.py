def params_to_dict(param_str):
    splits = param_str.split(" ")
    data = {}
    prev_key = None
    prev_val = None

    for s in splits:
        if "=" in s:
            key, val = s.split("=")
            if prev_key:
                data[prev_key] = prev_val
            prev_val = val
            prev_key = key
        else:
            new_val = prev_val + " " + s
            prev_val = new_val

    data[prev_key] = prev_val
    return data