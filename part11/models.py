from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional
import re


# =========================
# Part 12 ToDo 0
# Normalization + Stemming
# =========================

_PUNCT_TRANSLATION = str.maketrans("", "", "',.")


class PorterStemmer:
    """
    Simplified Porter-style stemmer (sufficient for this homework).
    """
    def stem(self, word: str) -> str:
        if len(word) <= 2:
            return word

        w = word

        # Step 1a: plurals
        for suffix, replacement in [
            ("sses", "ss"),
            ("ies", "i"),
            ("ss", "ss"),
            ("s", ""),
        ]:
            if w.endswith(suffix):
                w = w[:-len(suffix)] + replacement
                break

        # Step 1b: past participles
        for suffix in ("eed", "ed", "ing"):
            if w.endswith(suffix):
                base = w[:-len(suffix)]
                if re.search(r"[aeiouy]", base):
                    w = base if suffix != "eed" else w[:-1]
                break

        # Step 1c: y -> i
        if w.endswith("y") and re.search(r"[aeiouy]", w[:-1]):
            w = w[:-1] + "i"

        return w


_stemmer = PorterStemmer()


def process_token(token: str) -> str:
    """
    Central token processing function (Part 12 requirement).
    Used BOTH during indexing and querying.
    """
    norm = token.lower().translate(_PUNCT_TRANSLATION)
    if not norm:
        return ""
    return _stemmer.stem(norm)


# =========================
# Data model + Search
# =========================

class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]

        # Part 11 ToDo 1
        self.id = int(self.title.split("Sonnet ")[1].split(":")[0])


class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, list(self.spans))


class Posting:
    """
    Stores enough info to highlight ORIGINAL tokens.
    """
    def __init__(self, line_no: Optional[int], position: int, length: int):
        self.line_no = line_no
        self.position = position
        self.length = length


class Index:
    def __init__(self, sonnets: list[Sonnet]):
        self.sonnets = {s.id: s for s in sonnets}
        self.dictionary: Dict[str, Dict[int, List[Posting]]] = {}

        # Part 12 ToDo 1: index normalized + stemmed tokens
        for sonnet in sonnets:
            doc_id = sonnet.id

            # title
            for surface, pos in self.tokenize(sonnet.title):
                key = process_token(surface)
                if key:
                    self._add_token(doc_id, key, None, pos, len(surface))

            # lines
            for line_no, line in enumerate(sonnet.lines):
                for surface, pos in self.tokenize(line):
                    key = process_token(surface)
                    if key:
                        self._add_token(doc_id, key, line_no, pos, len(surface))

    @staticmethod
    def tokenize(text: str):
        return [(m.group(), m.start()) for m in re.finditer(r"\S+", text)]

    def _add_token(self, doc_id: int, token: str, line_no: int | None, position: int, length: int):
        self.dictionary.setdefault(token, {}).setdefault(doc_id, []).append(
            Posting(line_no, position, length)
        )

    def search_for(self, raw_token: str) -> dict[int, "SearchResult"]:
        results: Dict[int, SearchResult] = {}

        # Part 12 ToDo 2: normalize + stem query
        token = process_token(raw_token)
        if not token or token not in self.dictionary:
            return results

        for doc_id, postings in self.dictionary[token].items():
            sonnet = self.sonnets[doc_id]

            for p in postings:
                span = (p.position, p.position + p.length)

                if p.line_no is None:
                    result = SearchResult(sonnet.title, [span], [], 1)
                else:
                    line_text = sonnet.lines[p.line_no]
                    lm = LineMatch(p.line_no + 1, line_text, [span])
                    result = SearchResult(sonnet.title, [], [lm], 1)

                results[doc_id] = (
                    result if doc_id not in results else results[doc_id].combine_with(result)
                )

        return results


class Searcher:
    def __init__(self, sonnets: List[Sonnet]):
        self.index = Index(sonnets)

    def search(self, query: str, search_mode: str) -> List["SearchResult"]:
        words = query.split()
        combined: Dict[int, SearchResult] = {}

        for word in words:
            results = self.index.search_for(word)

            if not combined:
                combined = dict(results)
                continue

            if search_mode == "OR":
                for doc_id, res in results.items():
                    combined[doc_id] = (
                        res if doc_id not in combined else combined[doc_id].combine_with(res)
                    )
            else:  # AND
                combined = {
                    doc_id: combined[doc_id].combine_with(results[doc_id])
                    for doc_id in combined.keys() & results.keys()
                }

        return sorted(combined.values(), key=lambda r: r.title)


class SearchResult:
    def __init__(
        self,
        title: str,
        title_spans: List[Tuple[int, int]],
        line_matches: List[LineMatch],
        matches: int,
    ):
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(
            self.title,
            list(self.title_spans),
            [lm.copy() for lm in self.line_matches],
            self.matches,
        )

    @staticmethod
    def ansi_highlight(text: str, spans, highlight_mode) -> str:
        if not spans:
            return text

        spans = sorted(spans)
        merged = []
        cs, ce = spans[0]
        for s, e in spans[1:]:
            if s <= ce:
                ce = max(ce, e)
            else:
                merged.append((cs, ce))
                cs, ce = s, e
        merged.append((cs, ce))

        ansi = "\033[43m\033[30m" if highlight_mode == "DEFAULT" else "\033[1;92m"

        out, i = [], 0
        for s, e in merged:
            out += [text[i:s], ansi, text[s:e], "\033[0m"]
            i = e
        out.append(text[i:])
        return "".join(out)

    def print(self, idx, highlight_mode: str | None, total_docs):
        title = self.ansi_highlight(self.title, self.title_spans, highlight_mode) if highlight_mode else self.title
        print(f"\n[{idx}/{total_docs}] {title}")
        for lm in self.line_matches:
            line = self.ansi_highlight(lm.text, lm.spans, highlight_mode) if highlight_mode else lm.text
            print(f"  [{lm.line_no:2}] {line}")

    def combine_with(self, other: "SearchResult") -> "SearchResult":
        combined = self.copy()
        combined.matches += other.matches
        combined.title_spans += other.title_spans

        by_no = {lm.line_no: lm.copy() for lm in combined.line_matches}
        for lm in other.line_matches:
            by_no.setdefault(lm.line_no, lm.copy()).spans += lm.spans

        combined.line_matches = sorted(by_no.values(), key=lambda x: x.line_no)
        return combined

#placeholder for ultimate commit