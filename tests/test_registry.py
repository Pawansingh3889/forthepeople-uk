"""Tests for the canonical council registry.

The live verification test cross-checks every GSS code against postcodes.io
reverse geocoding (one bulk request) and skips cleanly when offline, so the
registry can't drift from what the geocoder — the join key consumers actually
use — currently serves.
"""
from __future__ import annotations

import re

import pytest
import requests

from registry import COORDS, REGISTRY, UK_ALL, councils

GSS_PATTERN = re.compile(r"^[EKNSW]\d{8}$")


class TestRegistryShape:
    def test_every_council_in_regions_is_registered(self) -> None:
        for region, names in councils.items():
            for name in names:
                assert name in REGISTRY, f"{name} ({region}) missing from REGISTRY"

    def test_coords_derived_from_registry(self) -> None:
        assert set(COORDS) == set(REGISTRY)

    def test_gss_codes_look_like_gss_codes(self) -> None:
        for c in REGISTRY.values():
            assert GSS_PATTERN.match(c.gss), f"{c.name}: bad GSS {c.gss!r}"

    def test_uk_all_uses_country_code(self) -> None:
        assert REGISTRY[UK_ALL].gss == "K02000001"

    def test_coordinates_inside_uk_bounds(self) -> None:
        for c in REGISTRY.values():
            assert 49 < c.lat < 61, f"{c.name} lat {c.lat}"
            assert -9 < c.lon < 2, f"{c.name} lon {c.lon}"


class TestGoverningAuthority:
    """Towns that are not authorities must map to whoever governs them."""

    def test_town_to_authority_mapping(self) -> None:
        expected = {
            "Huddersfield": "Kirklees",
            "Halifax": "Calderdale",
            "Harrogate": "North Yorkshire",
            "Scarborough": "North Yorkshire",
            "Grimsby": "North East Lincolnshire",
            "Chester": "Cheshire West and Chester",
            "Northampton": "West Northamptonshire",
            "Bournemouth": "Bournemouth, Christchurch and Poole",
        }
        for town, authority in expected.items():
            assert REGISTRY[town].authority == authority

    def test_middlesbrough_is_north_east(self) -> None:
        # Tees Valley sits in the North East region in the ONS split.
        assert REGISTRY["Middlesbrough"].region == "North East"


class TestRegistryAgainstPostcodesIo:
    """Every GSS code must match postcodes.io reverse geocoding.

    One bulk request for all entries; the whole test skips when the API is
    unreachable so offline runs stay green.
    """

    def test_gss_codes_match_reverse_geocoding(self) -> None:
        entries = [c for c in REGISTRY.values() if c.name != UK_ALL]
        payload = {"geolocations": [
            {"longitude": c.lon, "latitude": c.lat, "radius": 1000, "limit": 1}
            for c in entries
        ]}
        try:
            r = requests.post("https://api.postcodes.io/postcodes", json=payload, timeout=30)
            body = r.json()
        except Exception as e:
            pytest.skip(f"postcodes.io unreachable: {e}")
        results = body.get("result") or []
        if len(results) != len(entries):
            pytest.skip("unexpected bulk response shape")
        verified, mismatches = 0, []
        for c, item in zip(entries, results):
            hits = item.get("result") or []
            if not hits:
                continue  # centroid has no postcode within radius; not a failure
            found = (hits[0].get("codes") or {}).get("admin_district")
            if found is None:
                continue
            verified += 1
            if found != c.gss:
                mismatches.append(f"{c.name}: registry {c.gss}, geocoder {found}")
        assert not mismatches, "; ".join(mismatches)
        assert verified >= 40, f"only {verified} entries verified — check the request"
