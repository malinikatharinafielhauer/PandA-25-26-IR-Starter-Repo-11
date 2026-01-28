from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional
import re


class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]

        # ToDo 1 (Part 11): unique id from title like "Sonnet 11: ..."
        self.id = int(self.title.split("Sonnet ")[1].split(":")[0])

    @staticmethod
    def find_spans(text: str, pattern: str):
        spans = []
        if not pattern:
            return spans
        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
                spans.append((i, i + len(pattern)))
        return spans


class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no  # 1-based for printing
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, list(self.spans))


class Posting:
    """
    line_no:
      - None => token is in title
      - 0..n-1 => token is in sonnet.lines
    position:
      - character start offset within the title/line string
    """
    def __init__(self, line_no: Optional[int], position: int):
        self.line_no = line_no
        self.position = position

    def __repr__(self) -> str:
        return f"{self.line_no}:{self.position}"


class Index:
    def __init__(self, sonnets: list[Sonnet]):
        self.sonnets = {sonnet.id: sonnet for sonnet in sonnets}
        self.dictionary: Dict[str, Dict[int, List[Posting]]] = {}

        for sonnet in sonnets:
            doc_id = sonnet.id

            # ToDo 2: index title tokens with line_no=None
            for token, position in self.tokenize(sonnet.title):
                self._add_token(doc_id, token, None, position)

            # ToDo 2: index line tokens with line_no=0..n-1
            for line_no, line_text in enumerate(sonnet.lines):
                for token, position in self.tokenize(line_text):
                    self._add_token(doc_id, token, line_no, position)

    @staticmethod
    def tokenize(text: str):
        return [(m.group(), m.start()) for m in re.finditer(r"\S+", text)]

    def _add_token(self, doc_id: int, token: str, line_no: int | None, position: int):
        if token not in self.dictionary:
            self.dictionary[token] = {}

        postings_map = self.dictionary[token]
        if doc_id not in postings_map:
            postings_map[doc_id] = []

        postings_map[doc_id].append(Posting(line_no, position))

    def search_for(self, token: str) -> dict[int, "SearchResult"]:
        results: Dict[int, SearchResult] = {}

        if token not in self.dictionary:
            return results

        postings_map = self.dictionary[token]

        for doc_id, postings in postings_map.items():
            sonnet = self.sonnets[doc_id]

            for posting in postings:
                # ToDo 3: create SearchResult from posting
                start = posting.position
                end = posting.position + len(token)

                if posting.line_no is None:
                    result = SearchResult(
                        title=sonnet.title,
                        title_spans=[(start, end)],
                        line_matches=[],
                        matches=1,
                    )
                else:
                    line_text = sonnet.lines[posting.line_no]
                    lm = LineMatch(posting.line_no + 1, line_text, [(start, end)])
                    result = SearchResult(
                        title=sonnet.title,
                        title_spans=[],
                        line_matches=[lm],
                        matches=1,
                    )

                if doc_id not in results:
                    results[doc_id] = result
                else:
                    results[doc_id] = results[doc_id].combine_with(result)

        return results


class Searcher:
    def __init__(self, sonnets: List[Sonnet]):
        self.index = Index(sonnets)

    def search(self, query: str, search_mode: str) -> List["SearchResult"]:
        words = query.split()
        combined_results: Dict[int, SearchResult] = {}

        for word in words:
            results = self.index.search_for(word)

            if not combined_results:
                combined_results = dict(results)
                continue

            # ToDo 4: AND / OR combination
            if search_mode == "OR":
                # union
                for doc_id, res in results.items():
                    if doc_id in combined_results:
                        combined_results[doc_id] = combined_results[doc_id].combine_with(res)
                    else:
                        combined_results[doc_id] = res
            else:
                # AND: intersection
                new_combined = {}
                for doc_id in combined_results.keys() & results.keys():
                    new_combined[doc_id] = combined_results[doc_id].combine_with(results[doc_id])
                combined_results = new_combined

        out = list(combined_results.values())
        return sorted(out, key=lambda sr: sr.title)


class SearchResult:
    def __init__(
        self,
        title: str,
        title_spans: List[Tuple[int, int]],
        line_matches: List[LineMatch],
        matches: int,
    ) -> None:
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

        ansi_sequence = "\033[43m\033[30m" if highlight_mode == "DEFAULT" else "\033[1;92m"

        out = []
        i = 0
        for s, e in merged:
            out.append(text[i:s])
            out.append(ansi_sequence)
            out.append(text[s:e])
            out.append("\033[0m")
            i = e
        out.append(text[i:])
        return "".join(out)

    def print(self, idx, highlight_mode: str | None, total_docs):
        title_line = self.ansi_highlight(self.title, self.title_spans, highlight_mode) if highlight_mode else self.title
        print(f"\n[{idx}/{total_docs}] {title_line}")

        for lm in self.line_matches:
            line_out = self.ansi_highlight(lm.text, lm.spans, highlight_mode) if highlight_mode else lm.text
            print(f"  [{lm.line_no:2}] {line_out}")

    def combine_with(self, other: "SearchResult") -> "SearchResult":
        combined = self.copy()
        combined.matches = self.matches + other.matches
        combined.title_spans = sorted(self.title_spans + other.title_spans)

        lines_by_no = {lm.line_no: lm.copy() for lm in self.line_matches}
        for lm in other.line_matches:
            if lm.line_no in lines_by_no:
                lines_by_no[lm.line_no].spans.extend(lm.spans)
            else:
                lines_by_no[lm.line_no] = lm.copy()

        combined.line_matches = sorted(lines_by_no.values(), key=lambda x: x.line_no)
        return combined
