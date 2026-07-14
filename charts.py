"""Altair chart builders for the dashboard, dark theme.

Colors are the two categorical slots plus one ordinal blue pair, validated
against the app surface (#0a0f1a) with the palette validator: lightness band,
chroma floor, CVD separation and contrast all pass. Marks follow the house
spec: thin bars with rounded data-ends, 2px lines, recessive grid, text in
ink tokens rather than series color, tooltips on every mark. Single-series
charts carry no legend; the title names the series.
"""
from __future__ import annotations

import altair as alt
import pandas as pd

# Validated series colors (dark surface #0a0f1a)
BLUE = "#3987e5"        # categorical slot 1
AQUA = "#199e70"        # categorical slot 2
BLUE_LIGHT = "#6da7ec"  # ordinal step above BLUE, band top edge

# Ink and chrome tokens (app slate scale, text never wears series color)
INK = "#f8fafc"
INK_2 = "#94a3b8"
MUTED = "#64748b"
GRID = "rgba(148,163,184,0.12)"
AXIS = "#334155"


def _configured(chart: alt.LayerChart | alt.Chart) -> alt.LayerChart | alt.Chart:
    return (
        chart.configure(background="transparent")
        .configure_axis(labelColor=INK_2, titleColor=MUTED, gridColor=GRID,
                        domainColor=AXIS, tickColor=AXIS, labelFontSize=12,
                        titleFontSize=11)
        .configure_view(strokeWidth=0)
    )


def forecast_chart(forecast: list[dict]) -> alt.LayerChart:
    """7-day temperature range as a min-max band with labelled edges.

    A range is one entity, so it gets one hue: a translucent band between
    the lows and highs, edge lines in two steps of the same blue, and the
    edges named directly at the right-hand end instead of a legend box.
    """
    df = pd.DataFrame([{"date": f["date"], "max": f["max"], "min": f["min"],
                        "rain": f["rain"], "conditions": f.get("condition", "")}
                       for f in forecast])
    x = alt.X("date:T", axis=alt.Axis(format="%a %d", grid=False, title=None))
    tooltip = [
        alt.Tooltip("date:T", format="%A %d %B", title="Day"),
        alt.Tooltip("max:Q", title="High (C)"),
        alt.Tooltip("min:Q", title="Low (C)"),
        alt.Tooltip("rain:Q", title="Rain (mm)"),
        alt.Tooltip("conditions:N", title="Conditions"),
    ]
    band = alt.Chart(df).mark_area(opacity=0.18, color=BLUE).encode(
        x=x, y=alt.Y("min:Q", title="C", scale=alt.Scale(zero=False)),
        y2="max:Q", tooltip=tooltip)
    hi = alt.Chart(df).mark_line(color=BLUE_LIGHT, strokeWidth=2).encode(
        x=x, y="max:Q", tooltip=tooltip)
    lo = alt.Chart(df).mark_line(color=BLUE, strokeWidth=2).encode(
        x=x, y="min:Q", tooltip=tooltip)
    pts = alt.Chart(df).mark_point(size=90, opacity=0).encode(
        x=x, y="max:Q", tooltip=tooltip)
    last = df.iloc[[-1]]
    hi_label = alt.Chart(last).mark_text(align="left", dx=8, color=INK_2,
                                         fontSize=12).encode(
        x=x, y="max:Q", text=alt.value("high"))
    lo_label = alt.Chart(last).mark_text(align="left", dx=8, color=INK_2,
                                         fontSize=12).encode(
        x=x, y="min:Q", text=alt.value("low"))
    return _configured(
        alt.layer(band, hi, lo, pts, hi_label, lo_label).properties(height=240)
    )


def rain_chart(forecast: list[dict]) -> alt.LayerChart:
    """Daily precipitation as thin rounded bars, one hue, values on demand."""
    df = pd.DataFrame([{"date": f["date"], "rain": f["rain"]} for f in forecast])
    bars = alt.Chart(df).mark_bar(color=AQUA, size=18, cornerRadiusTopLeft=4,
                                  cornerRadiusTopRight=4).encode(
        x=alt.X("date:T", axis=alt.Axis(format="%a %d", grid=False, title=None)),
        y=alt.Y("rain:Q", title="mm"),
        tooltip=[alt.Tooltip("date:T", format="%A %d %B", title="Day"),
                 alt.Tooltip("rain:Q", title="Rain (mm)")])
    return _configured(alt.layer(bars).properties(height=130))


def category_bars(pairs: list[tuple[str, float]], value_title: str,
                  value_format: str = ",.0f") -> alt.LayerChart:
    """Horizontal magnitude bars: one hue, sorted, value labels at the ends.

    Thin marks with rounded data-ends anchored to the zero baseline, a 2px
    gap between bars via band padding, and the value written once at each
    bar end in ink rather than a number on every gridline.
    """
    df = pd.DataFrame(pairs, columns=["category", "value"])
    y = alt.Y("category:N", sort="-x", title=None,
              axis=alt.Axis(grid=False, domainColor=AXIS, labelLimit=180))
    bars = alt.Chart(df).mark_bar(color=BLUE, size=20, cornerRadiusTopRight=4,
                                  cornerRadiusBottomRight=4).encode(
        y=y,
        x=alt.X("value:Q", title=value_title,
                axis=alt.Axis(gridColor=GRID, domain=False, tickCount=4)),
        tooltip=[alt.Tooltip("category:N", title=" "),
                 alt.Tooltip("value:Q", title=value_title, format=value_format)])
    labels = alt.Chart(df).mark_text(align="left", dx=6, color=INK,
                                     fontSize=12).encode(
        y=y, x="value:Q", text=alt.Text("value:Q", format=value_format))
    height = 20 + 34 * len(df)
    return _configured(alt.layer(bars, labels).properties(height=height))
