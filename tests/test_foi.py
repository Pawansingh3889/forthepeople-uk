"""Tests for FOI signposting link + template building."""
from __future__ import annotations

import foi


class TestFoiLinks:
    def test_authority_specific_link_uses_governing_body(self) -> None:
        # Hull's governing authority, not the display name "Hull".
        links = foi.foi_links("Hull")
        assert links["authority"] == "Kingston upon Hull, City of"
        assert "select_authority?query=" in links["whatdotheyknow"]
        assert "Kingston" in links["whatdotheyknow"]
        assert "%2C" in links["whatdotheyknow"]  # comma is URL-encoded

    def test_town_maps_to_its_authority(self) -> None:
        # Huddersfield is governed by Kirklees.
        links = foi.foi_links("Huddersfield")
        assert links["authority"] == "Kirklees"
        assert "Kirklees" in links["whatdotheyknow"]

    def test_uk_all_gets_generic_finder(self) -> None:
        links = foi.foi_links("United Kingdom")
        assert links["authority"] is None
        assert links["whatdotheyknow"].endswith("/select_authority")

    def test_unknown_council_gets_generic_finder(self) -> None:
        links = foi.foi_links("Atlantis")
        assert links["authority"] is None
        assert links["whatdotheyknow"].endswith("/select_authority")

    def test_guidance_links_present(self) -> None:
        links = foi.foi_links("Leeds")
        assert links["gov_guide"].startswith("https://www.gov.uk/")
        assert links["ico_guide"].startswith("https://ico.org.uk/")
        assert links["response_days"] == 20


class TestRequestTemplate:
    def test_names_the_authority(self) -> None:
        body = foi.request_template("Leeds")
        assert "Dear Leeds," in body
        assert "Freedom of Information Act 2000" in body

    def test_falls_back_to_placeholder(self) -> None:
        body = foi.request_template(None)
        assert "[council name]" in body
