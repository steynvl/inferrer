import itertools


def prefix_set(s, alphabet=None):
    return _generate_set(s, alphabet, str.startswith)


def suffix_set(s, alphabet=None):
    return _generate_set(s, alphabet, str.endswith)


def determine_alphabet(s):
    return set(''.join(s))


def break_strings_in_two(red):
    we = set()
    for r in red:
        if len(r) == 0:
            we.add(('', ''))
        elif len(r) == 1:
            we.update({('', r), (r, '')})
        else:
            we.update({('', r), (r, '')})
            for i in range(len(r)):
                we.add((r[:i], r[i:]))
    return we


def _generate_set(s, alphabet, func):
    if alphabet is None:
        alphabet = determine_alphabet(s)

    longest = len(max(s, key=len))
    for comb in _get_all_combinations(alphabet, longest):
        if any([func(i, comb) for i in s]):
            yield comb


def _get_all_combinations(s, repeat):
    for rep in range(repeat + 1):
        for p in itertools.product(s, repeat=rep):
            yield ''.join(p)
