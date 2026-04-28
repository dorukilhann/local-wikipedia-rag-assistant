from wiki_rag.routing import classify_query


def test_routes_known_person():
    route = classify_query("What did Marie Curie discover?")

    assert route.route == "person"
    assert route.matched_people == ("Marie Curie",)


def test_routes_known_place():
    route = classify_query("Where is the Eiffel Tower located?")

    assert route.route == "place"
    assert route.matched_places == ("Eiffel Tower",)


def test_routes_person_place_mixed_query():
    route = classify_query("Compare Albert Einstein and the Eiffel Tower")

    assert route.route == "both"


def test_routes_keyword_person_query():
    route = classify_query("Which person is associated with electricity?")

    assert route.route == "person"
