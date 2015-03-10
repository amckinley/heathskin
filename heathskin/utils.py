from tabulate import tabulate

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

class MultiDictDiffer(object):
    def __init__(self, dicts):
        self.ds = dicts

    def get_diff(self):
        all_keys = set()
        for d in self.ds:
            for k in d.keys():
                all_keys.add(k)

        diff_table = []
        for k in all_keys:
            values = list()
            for d in self.ds:
                values.append(d.get(k, "<missing>"))

            first_val = values[0]
            found_diff = False
            for v in values[1:]:
                if v != first_val:
                    found_diff = True
                    break

            if found_diff:
                values.insert(0, k)
                diff_table.append(values)

        print tabulate(diff_table)




class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])