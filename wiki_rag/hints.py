"""Small local hint maps for broad attribute-style questions."""

from __future__ import annotations

from dataclasses import dataclass

from wiki_rag.entities import normalize_title


LOCATION_ENTITY_HINTS = {
    "turkey": ["Hagia Sophia", "Cappadocia", "Ephesus", "Topkapi Palace", "Sultan Ahmed Mosque"],
    "turkiye": ["Hagia Sophia", "Cappadocia", "Ephesus", "Topkapi Palace", "Sultan Ahmed Mosque"],
    "istanbul": ["Hagia Sophia", "Topkapi Palace", "Sultan Ahmed Mosque"],
    "france": ["Eiffel Tower", "Louvre"],
    "paris": ["Eiffel Tower", "Louvre"],
    "china": ["Great Wall of China"],
    "india": ["Taj Mahal"],
    "united states": ["Statue of Liberty", "Grand Canyon", "Yellowstone National Park", "Golden Gate Bridge"],
    "usa": ["Statue of Liberty", "Grand Canyon", "Yellowstone National Park", "Golden Gate Bridge"],
    "america": ["Statue of Liberty", "Grand Canyon", "Yellowstone National Park", "Golden Gate Bridge"],
    "new york": ["Statue of Liberty"],
    "arizona": ["Grand Canyon"],
    "peru": ["Machu Picchu"],
    "italy": ["Colosseum", "Vatican City"],
    "rome": ["Colosseum", "Vatican City"],
    "greece": ["Acropolis of Athens"],
    "athens": ["Acropolis of Athens"],
    "egypt": ["Pyramids of Giza"],
    "nepal": ["Mount Everest"],
    "tibet": ["Mount Everest"],
    "cambodia": ["Angkor Wat"],
    "jordan": ["Petra"],
    "australia": ["Sydney Opera House"],
    "sydney": ["Sydney Opera House"],
    "united kingdom": ["Stonehenge", "Tower of London"],
    "uk": ["Stonehenge", "Tower of London"],
    "england": ["Stonehenge", "Tower of London"],
    "london": ["Tower of London"],
    "united arab emirates": ["Burj Khalifa"],
    "uae": ["Burj Khalifa"],
    "dubai": ["Burj Khalifa"],
    "spain": ["Sagrada Familia", "Alhambra"],
    "barcelona": ["Sagrada Familia"],
    "granada": ["Alhambra"],
    "brazil": ["Christ the Redeemer"],
    "rio de janeiro": ["Christ the Redeemer"],
    "japan": ["Mount Fuji"],
}

ASSOCIATION_ENTITY_HINTS = {
    "electricity": ["Nikola Tesla", "Albert Einstein"],
    "alternating current": ["Nikola Tesla"],
    "relativity": ["Albert Einstein"],
    "radioactivity": ["Marie Curie"],
    "painting": ["Leonardo da Vinci", "Frida Kahlo", "Pablo Picasso"],
    "literature": ["William Shakespeare", "Jane Austen"],
    "music": ["Taylor Swift", "Michael Jackson", "Ludwig van Beethoven", "Wolfgang Amadeus Mozart"],
    "civil rights": ["Martin Luther King Jr.", "Nelson Mandela", "Mahatma Gandhi"],
    "computer": ["Ada Lovelace", "Steve Jobs"],
    "aviation": ["Amelia Earhart"],
}

LOCATION_QUERY_TERMS = {
    "located",
    "location",
    "where",
    "country",
    "city",
    "in",
}

ASSOCIATION_QUERY_TERMS = {
    "associated",
    "known",
    "famous",
    "invent",
    "discover",
    "person",
    "people",
}


@dataclass(frozen=True)
class EntityHint:
    title: str
    reason: str


def find_entity_hints(query: str) -> list[EntityHint]:
    normalized = normalize_title(query)
    hints: list[EntityHint] = []

    if _contains_any(normalized, LOCATION_QUERY_TERMS):
        hints.extend(_matches(normalized, LOCATION_ENTITY_HINTS, "matched location term"))

    if _contains_any(normalized, ASSOCIATION_QUERY_TERMS):
        hints.extend(_matches(normalized, ASSOCIATION_ENTITY_HINTS, "matched association term"))

    seen: set[str] = set()
    unique: list[EntityHint] = []
    for hint in hints:
        key = normalize_title(hint.title)
        if key not in seen:
            unique.append(hint)
            seen.add(key)
    return unique


def _contains_any(query: str, terms: set[str]) -> bool:
    padded = f" {query} "
    return any(f" {term} " in padded for term in terms)


def _matches(
    query: str, mapping: dict[str, list[str]], reason: str
) -> list[EntityHint]:
    return [
        EntityHint(title=title, reason=f"{reason}: {term}")
        for term, titles in mapping.items()
        if term in query
        for title in titles
    ]
