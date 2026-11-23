import altair as alt
import pandas as pd
import streamlit as st

EMPTY = "Sem dados para esta seleção."


def number(value) -> str:
    """Integer with Brazilian thousands separator: 730.502"""
    return f"{value:,.0f}".replace(",", ".")


def from_link(key: str, options) -> None:
    """Opened from a link of the questions page (?view=...): start on the view the link points to, then
    drop the parameter so the user's own clicks are not overridden."""
    value = st.query_params.get("view")

    if value in options:
        st.session_state[key] = value
        del st.query_params["view"]


def view(options: dict[str, str], key: str) -> str:
    """One switch per page: only the chosen answer is shown. Options are {id: label}."""
    from_link(key, options)

    if st.session_state.get(key) not in options:
        st.session_state[key] = next(iter(options))

    return st.segmented_control("Visão", list(options), format_func=options.get, required=True, key=key,
                                label_visibility="collapsed")


def bars(df: pd.DataFrame, value: str, label: str, title: str, fmt: str = ".1f", tooltip: list | None = None, color=None) -> None:
    """Horizontal bars, largest on top."""
    if df.empty:
        st.info(EMPTY)
        return

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{value}:Q", title=title),
        y=alt.Y(f"{label}:N", sort="-x", title=None),
        tooltip=[alt.Tooltip(f"{label}:N", title=" "), alt.Tooltip(f"{value}:Q", title=title, format=fmt), *(tooltip or [])],
    )

    if color is not None:
        chart = chart.encode(color=color)

    st.altair_chart(chart.properties(height=max(160, 26 * len(df))), width="stretch")


def dots(df: pd.DataFrame, value: str, label: str, title: str, tooltip: list | None = None) -> None:
    """Dots instead of bars, for values whose axis should not start at zero (GXE, speed)."""
    if df.empty:
        st.info(EMPTY)
        return

    chart = alt.Chart(df).mark_circle(size=90).encode(
        x=alt.X(f"{value}:Q", title=title, scale=alt.Scale(zero=False)),
        y=alt.Y(f"{label}:N", sort="-x", title=None),
        tooltip=[alt.Tooltip(f"{label}:N", title=" "), alt.Tooltip(f"{value}:Q", title=title), *(tooltip or [])],
    )

    st.altair_chart(chart.properties(height=max(160, 26 * len(df))), width="stretch")


def lines(df: pd.DataFrame, value: str, series: str, title: str, fmt: str = ".1f") -> None:
    """One line per series over the months."""
    if df.empty:
        st.info(EMPTY)
        return

    # Naive month start, so the browser's time zone can't shift a month into the previous one
    df = df.assign(month=df["date"].dt.tz_localize(None))

    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("month:T", title=None, axis=alt.Axis(format="%Y-%m")),
        y=alt.Y(f"{value}:Q", title=title),
        color=alt.Color(f"{series}:N", title=None, legend=alt.Legend(orient="bottom", columns=4)),
        tooltip=[alt.Tooltip(f"{series}:N", title=" "), alt.Tooltip("month:T", title="Mês", format="%Y-%m"),
                 alt.Tooltip(f"{value}:Q", title=title, format=fmt)],
    )

    st.altair_chart(chart, width="stretch")
