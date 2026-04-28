from wiki_rag.wiki_client import WIKI_TITLE_OVERRIDES


def test_ambiguous_wikipedia_title_override_for_christ_the_redeemer():
    assert WIKI_TITLE_OVERRIDES["Christ the Redeemer"] == "Christ the Redeemer (statue)"
