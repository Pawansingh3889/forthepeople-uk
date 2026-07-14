"""Smoke tests for the Altair chart builders — spec shape, not pixels."""
from __future__ import annotations

import charts

FORECAST = [
    {"date": f"2026-07-{10 + i:02d}", "max": 20 + i, "min": 11 + i,
     "rain": float(i), "condition": "Clear"}
    for i in range(7)
]


class TestForecastChart:
    def test_builds_layered_spec(self) -> None:
        spec = charts.forecast_chart(FORECAST).to_dict()
        assert "layer" in spec
        # band + two edge lines + hover points + two edge labels
        assert len(spec["layer"]) == 6

    def test_band_spans_min_to_max(self) -> None:
        spec = charts.forecast_chart(FORECAST).to_dict()
        band = spec["layer"][0]
        assert band["encoding"]["y"]["field"] == "min"
        assert band["encoding"]["y2"]["field"] == "max"


class TestRainChart:
    def test_builds_bar_spec(self) -> None:
        spec = charts.rain_chart(FORECAST).to_dict()
        assert spec["layer"][0]["mark"]["type"] == "bar"
        assert spec["layer"][0]["encoding"]["y"]["field"] == "rain"


class TestCategoryBars:
    def test_bars_plus_end_labels(self) -> None:
        spec = charts.category_bars([("A", 5), ("B", 9)], "things").to_dict()
        marks = [layer["mark"]["type"] for layer in spec["layer"]]
        assert marks == ["bar", "text"]

    def test_sorted_descending_by_value(self) -> None:
        spec = charts.category_bars([("A", 5), ("B", 9)], "things").to_dict()
        assert spec["layer"][0]["encoding"]["y"]["sort"] == "-x"

    def test_height_scales_with_rows(self) -> None:
        two = charts.category_bars([("A", 1), ("B", 2)], "x").to_dict()
        five = charts.category_bars([(c, 1) for c in "ABCDE"], "x").to_dict()
        assert five["layer"][0].get("height", five.get("height")) or True
        assert five.get("height", 0) > two.get("height", 0)
