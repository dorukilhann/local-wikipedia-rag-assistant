from wiki_rag.hints import find_entity_hints


def test_turkey_location_question_hints_turkey_places():
    hints = find_entity_hints("Which famous place is located in Turkey?")
    titles = [hint.title for hint in hints]

    assert "Hagia Sophia" in titles
    assert "Cappadocia" in titles
    assert "Ephesus" in titles


def test_electricity_question_hints_tesla():
    hints = find_entity_hints("Which person is associated with electricity?")
    titles = [hint.title for hint in hints]

    assert "Nikola Tesla" in titles
