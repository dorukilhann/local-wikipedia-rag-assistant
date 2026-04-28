from wiki_rag.entities import PEOPLE, PLACES


def test_entity_lists_have_30_people_and_30_places():
    assert len(PEOPLE) == 30
    assert len(PLACES) == 30


def test_turkey_places_are_indexed():
    for title in ["Hagia Sophia", "Cappadocia", "Ephesus", "Topkapi Palace", "Sultan Ahmed Mosque"]:
        assert title in PLACES
