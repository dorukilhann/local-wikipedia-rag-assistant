"""Simple rule-based query routing for person/place retrieval."""

from __future__ import annotations

import re
from dataclasses import dataclass

from wiki_rag.entities import PEOPLE, PLACES, normalize_title


PERSON_KEYWORDS = {
    "person",
    "people",
    "who",
    "born",
    "died",
    "scientist",
    "artist",
    "writer",
    "poet",
    "composer",
    "singer",
    "footballer",
    "athlete",
    "discover",
    "invent",
    "known for",
    "associated with",
}

PLACE_KEYWORDS = {
    "place",
    "places",
    "where",
    "located",
    "location",
    "landmark",
    "monument",
    "tower",
    "wall",
    "mountain",
    "museum",
    "city",
    "country",
    "used for",
    "important",
}

MIXED_KEYWORDS = {"compare", "comparison", "versus", " vs ", " both ", "difference"}


@dataclass(frozen=True)
class QueryRoute:
    route: str
    reason: str
    matched_people: tuple[str, ...]
    matched_places: tuple[str, ...]


def _contains_keyword(query: str, keywords: set[str]) -> bool:
    return any(
        re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", query) is not None
        for keyword in keywords
    )


def classify_query(query: str) -> QueryRoute:
    normalized = normalize_title(query)
    matched_people = tuple(title for title in PEOPLE if normalize_title(title) in normalized)
    matched_places = tuple(title for title in PLACES if normalize_title(title) in normalized)

    if matched_people and matched_places:
        return QueryRoute("both", "matched both people and places", matched_people, matched_places)
    if matched_people:
        return QueryRoute("person", "matched known person name", matched_people, matched_places)
    if matched_places:
        return QueryRoute("place", "matched known place name", matched_people, matched_places)

    has_person_keyword = _contains_keyword(normalized, PERSON_KEYWORDS)
    has_place_keyword = _contains_keyword(normalized, PLACE_KEYWORDS)
    has_mixed_keyword = _contains_keyword(f" {normalized} ", MIXED_KEYWORDS)

    if has_person_keyword and has_place_keyword:
        return QueryRoute("both", "matched person and place keywords", matched_people, matched_places)
    if has_person_keyword:
        return QueryRoute("person", "matched person keywords", matched_people, matched_places)
    if has_place_keyword:
        return QueryRoute("place", "matched place keywords", matched_people, matched_places)
    if has_mixed_keyword:
        return QueryRoute("both", "matched comparison keywords", matched_people, matched_places)
    return QueryRoute("both", "no specific route matched", matched_people, matched_places)
