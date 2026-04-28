"""Entity lists required by the assignment."""

from __future__ import annotations

from dataclasses import dataclass


PEOPLE = [
    "Albert Einstein",
    "Marie Curie",
    "Leonardo da Vinci",
    "William Shakespeare",
    "Ada Lovelace",
    "Nikola Tesla",
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Taylor Swift",
    "Frida Kahlo",
    "Isaac Newton",
    "Charles Darwin",
    "Nelson Mandela",
    "Mahatma Gandhi",
    "Cleopatra",
    "Ludwig van Beethoven",
    "Wolfgang Amadeus Mozart",
    "Martin Luther King Jr.",
    "Pablo Picasso",
    "Oprah Winfrey",
    "Aristotle",
    "Galileo Galilei",
    "Jane Austen",
    "Amelia Earhart",
    "Michael Jackson",
    "Queen Victoria",
    "Abraham Lincoln",
    "Walt Disney",
    "Steve Jobs",
    "Mother Teresa",
]

PLACES = [
    "Eiffel Tower",
    "Great Wall of China",
    "Taj Mahal",
    "Grand Canyon",
    "Machu Picchu",
    "Colosseum",
    "Hagia Sophia",
    "Statue of Liberty",
    "Pyramids of Giza",
    "Mount Everest",
    "Louvre",
    "Acropolis of Athens",
    "Stonehenge",
    "Burj Khalifa",
    "Angkor Wat",
    "Petra",
    "Sydney Opera House",
    "Yellowstone National Park",
    "Vatican City",
    "Niagara Falls",
    "Cappadocia",
    "Ephesus",
    "Topkapi Palace",
    "Sultan Ahmed Mosque",
    "Tower of London",
    "Sagrada Familia",
    "Christ the Redeemer",
    "Golden Gate Bridge",
    "Alhambra",
    "Mount Fuji",
]


@dataclass(frozen=True)
class Entity:
    title: str
    entity_type: str


def all_entities() -> list[Entity]:
    return [Entity(title, "person") for title in PEOPLE] + [
        Entity(title, "place") for title in PLACES
    ]


def normalize_title(title: str) -> str:
    return " ".join(title.lower().strip().split())
