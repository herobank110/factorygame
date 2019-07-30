"""Change case of a string between snake, camel and pascal."""

from string import whitespace as str_whitespace

def general_split(s, first_index=0):
    """
    Yield each word in a string that starts with a capital letter or that
    has any whitespace immediately before it.
    """
    s = s.strip() + "A"
    for i, letter in enumerate(s):
        if i > first_index:
            # Split at capital letter
            if letter.isupper():
                yield s[first_index:i]
                first_index = i
            # Split at underscore
            elif letter == "_":
                yield s[first_index:i]
                first_index = i + 1
            # Split at whitespace
            elif letter in str_whitespace \
                and (i+1 < len(s) and not s[i + 1] in str_whitespace):
                yield s[first_index:i]
                first_index = i + 1

def camel_split(s):
    """
    Split a string into words list using camelCase rules.
    """
    return [word for word in general_split(s)]

def pascal_split(s):
    """
    Split a string into words list using PascalCase rules.
    """
    return [word for word in general_split(s, -1)]

def snake_split(s):
    """
    Split a string into words list using snake_case rules.
    """
    s = s.strip().replace(" ", "")
    return s.split("_")

def to_words(s):
    """
    Return a list of words for a given string.
    """
    return general_split(s)

def to_camel(s):
    """
    Convert a string or list of words to camelCase.
    """
    if isinstance(s, str):
        return to_camel(to_words(s))
    ret = ""
    for word in s:
        if word:
            if not ret:
                ret += word.lower()
            else:
                ret += word[0].upper()
                ret += word[1:].lower()
    return ret

def to_pascal(s):
    """
    Convert a string or list of words to PascalCase.
    """
    if isinstance(s, str):
        return to_pascal(to_words(s))
    ret = ""
    for word in s:
        if word:
            ret += word[0].upper()
            ret += word[1:].lower()
    return ret

def to_snake(s):
    """
    Convert a string or list of words to snake_case.
    """
    if isinstance(s, str):
        return to_snake(to_words(s))
    return "_".join(word.lower().replace("_", "") for word in s if word)

def get_case(s):
    """
    Return the best estimate for what case a string is using.
    """
    # Calculate words lists for all cases.
    cases = ({"name":"snake",   "words":snake_split(s)},
             {"name":"camel",   "words":camel_split(s)},
             {"name":"pascal",  "words":pascal_split(s)})
    # Get lengths of calculated lists.
    case_lens = [len(case["words"]) for case in cases]
    # Pick the case that identified the most individual words.
    return cases[case_lens.index(max(case_lens))]["name"]