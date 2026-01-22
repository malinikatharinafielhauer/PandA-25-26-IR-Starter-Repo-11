# -------------------- Part 12 ToDo 0: Normalization + Stemming --------------------

import re
_PUNCT_TRANSLATION = str.maketrans("", "", "',.")

class PorterStemmer:
    def stem(self, word: str) -> str:
        if len(word) <= 2:
            return word

        w = word
#the logic replaced because there were many elif else loops going on. seemed unecological.
        for suffix, replacement in [
            ("sses", "ss"),
            ("ies", "i"),
            ("ss", "ss"),
            ("s", ""),
        ]:
            if w.endswith(suffix):
                w = w[:-len(suffix)] + replacement
                break

        # more suffixes
        for suffix in ("eed", "ed", "ing"):
            if w.endswith(suffix):
                base = w[:-len(suffix)]
                if re.search(r"[aeiouy]", base):
                    w = base if suffix != "eed" else w[:-1]
                break

        #even more ending
        if w.endswith("y") and re.search(r"[aeiouy]", w[:-1]):
            w = w[:-1] + "i"

        return w

_stemmer = PorterStemmer()

def process_token(token: str) -> str:
    """
    Part 12 ToDo 0:
    - lowercase
    - remove ',.
    - stem
    """
    norm = token.lower().translate(_PUNCT_TRANSLATION)
    if not norm:
        return ""
    return _stemmer.stem(norm)

###just ornamental for the upload