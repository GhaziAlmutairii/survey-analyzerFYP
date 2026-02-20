# visualisations.py
# I put all my chart-building functions in here so I could reuse them
# across different pages without copy-pasting the same plotly code everywhere
# each function takes a dataframe and returns a plotly figure

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# colour palette - I used ColorBrewer Dark2 because it's colour-blind safe
# and looks professional on a white background
PALETTE = [
    "#1b9e77", "#d95f02", "#7570b3", "#e7298a",
    "#66a61e", "#e6ab02", "#a6761d", "#666666",
]

# I keep the Likert options in a specific order so they display correctly
# on charts rather than sorting alphabetically
LIKERT_ORDER = [
    "Not at all", "Slightly (a little)", "Moderately", "Very", "Extremely",
    "Strongly disagree", "Mildly disagree", "Neutral", "Mildly agree", "Strongly agree",
    "Very dissatisfied", "Somewhat dissatisfied",
    "Neither satisfied nor dissatisfied",
    "Somewhat satisfied", "Very satisfied",
    "Very poor", "Poor", "Average", "Good", "Excellent",
    "Not important", "Somewhat important", "Very important", "Extremely important",
    "Yes", "No",
]


# ---------------------------------------------------------------------------
# Chart 1: Nationality distribution — bar chart
# ---------------------------------------------------------------------------

def nationality_bar_chart(dist_df, title="Responses by Home Country"):
    """
    Vertical bar chart of response counts per nationality.

    Parameters
    ----------
    dist_df : pd.DataFrame
        Columns: Country, Count, Percentage.
    title : str
        Chart title.

    Returns
    -------
    plotly.graph_objs.Figure
    """
    fig = px.bar(
        dist_df,
        x="Country",
        y="Count",
        text="Percentage",
        color="Country",
        color_discrete_sequence=PALETTE,
        title=title,
        labels={"Count": "Number of Students", "Country": "Home Country"},
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-30,
        height=420,
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#e9ecef"),
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 2: Nationality distribution — donut chart
# ---------------------------------------------------------------------------

def nationality_donut_chart(dist_df, title="Nationality Breakdown"):
    """
    Donut (pie) chart of response percentages per nationality.

    Parameters
    ----------
    dist_df : pd.DataFrame
        Columns: Country, Count, Percentage.

    Returns
    -------
    plotly.graph_objs.Figure
    """
    fig = go.Figure(data=go.Pie(
        labels=dist_df["Country"],
        values=dist_df["Count"],
        hole=0.45,
        marker_colors=PALETTE * (len(dist_df) // len(PALETTE) + 1),
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} students (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        height=420,
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5),
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 3: Single question response — horizontal bar
# ---------------------------------------------------------------------------

def response_horizontal_bar(response_df, title="Response Distribution"):
    """
    Horizontal bar chart of response counts for a single question.
    Useful when response labels are long.

    Parameters
    ----------
    response_df : pd.DataFrame
        Columns: Response, Count, Percentage.

    Returns
    -------
    plotly.graph_objs.Figure
    """
    fig = px.bar(
        response_df,
        x="Count",
        y="Response",
        orientation="h",
        text="Percentage",
        color="Response",
        color_discrete_sequence=PALETTE,
        title=title,
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        showlegend=False,
        height=max(280, len(response_df) * 55),
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#e9ecef"),
        yaxis=dict(autorange="reversed"),
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 4: Stacked bar — Likert distribution by nationality
# ---------------------------------------------------------------------------

def stacked_likert_bar(df, question_column, countries=None,
                       title=None, use_percentage=True):
    """
    Stacked horizontal bar chart showing Likert response distribution
    for each nationality side-by-side.

    This is the primary Week 7 comparative visualisation — it allows viewers
    to see all nationality groups' response patterns simultaneously.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame with Country_Clean column.
    question_column : str
        Survey question column to visualise.
    countries : list of str or None
        Countries to include. None = all.
    title : str or None
        Chart title. Auto-generated if None.
    use_percentage : bool
        If True, shows column percentages (normalised per country).
        If False, shows raw counts.

    Returns
    -------
    plotly.graph_objs.Figure
    """
    from utils.statistics import filter_by_nationality

    if countries:
        df = filter_by_nationality(df, countries)

    # Prepare data
    valid = df[["Country_Clean", question_column]].copy()
    valid[question_column] = valid[question_column].astype(str).str.strip()
    valid = valid[
        (valid[question_column].str.lower() != "not applicable") &
        (valid[question_column].str.lower() != "nan") &
        (valid[question_column] != "")
    ]

    if valid.empty:
        return go.Figure().update_layout(title="No data available")

    ct = pd.crosstab(valid["Country_Clean"], valid[question_column])

    # Sort columns by Likert order
    order_map = {r: i for i, r in enumerate(LIKERT_ORDER)}
    sorted_cols = sorted(ct.columns, key=lambda c: order_map.get(c, 999))
    ct = ct[sorted_cols]

    if use_percentage:
        plot_df = (ct.div(ct.sum(axis=1), axis=0) * 100).round(1)
        value_suffix = "%"
        xaxis_label = "Percentage of Responses (%)"
    else:
        plot_df = ct
        value_suffix = ""
        xaxis_label = "Number of Responses"

    # Build stacked bars
    fig = go.Figure()
    colour_cycle = PALETTE * (len(sorted_cols) // len(PALETTE) + 1)

    for i, col in enumerate(sorted_cols):
        vals = plot_df[col]
        fig.add_trace(go.Bar(
            name=col,
            x=vals.values,
            y=vals.index.tolist(),
            orientation="h",
            marker_color=colour_cycle[i],
            text=[f"{v:.1f}{value_suffix}" if v > 3 else "" for v in vals.values],
            textposition="inside",
            hovertemplate=f"{col}: %{{x:.1f}}{value_suffix}<extra></extra>",
        ))

    auto_title = title or f"{'Percentage' if use_percentage else 'Count'} Distribution by Nationality"
    fig.update_layout(
        barmode="stack",
        title=auto_title,
        xaxis_title=xaxis_label,
        yaxis_title="Nationality",
        height=max(300, len(plot_df) * 60 + 120),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
        ),
        plot_bgcolor="white",
        xaxis=dict(gridcolor="#e9ecef"),
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 5: Grouped bar — compare two questions across nationalities
# ---------------------------------------------------------------------------

def grouped_mean_score_bar(score_rows, title="Mean Scores by Nationality"):
    """
    Grouped bar chart comparing mean scores across multiple metrics
    for each nationality.

    Parameters
    ----------
    score_rows : list of dict
        Each dict: {'Country': str, 'Metric': str, 'Mean Score': float}
    title : str

    Returns
    -------
    plotly.graph_objs.Figure
    """
    if not score_rows:
        return go.Figure().update_layout(title="No data")

    plot_df = pd.DataFrame(score_rows)
    fig = px.bar(
        plot_df,
        x="Country",
        y="Mean Score",
        color="Metric",
        barmode="group",
        color_discrete_sequence=PALETTE,
        title=title,
        range_y=[0, 5.5],
        labels={"Mean Score": "Mean Score (1–5)"},
        text="Mean Score",
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        height=460,
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#e9ecef"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 6: Programme distribution — donut
# ---------------------------------------------------------------------------

def programme_donut_chart(prog_dist_df):
    """Donut chart of programme category distribution."""
    fig = go.Figure(data=go.Pie(
        labels=prog_dist_df["Programme"],
        values=prog_dist_df["Count"],
        hole=0.45,
        marker_colors=PALETTE[:len(prog_dist_df)],
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} students<extra></extra>",
    ))
    fig.update_layout(
        title="MSc Programme Distribution",
        height=380,
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# Chart 7: Heatmap for mean scores
# ---------------------------------------------------------------------------

def mean_score_heatmap(sat_df, title="Mean Agreement & Difficulty Scores (1–5)"):
    """
    Heatmap of mean numeric scores per nationality across all
    agreement and difficulty questions.

    Parameters
    ----------
    sat_df : pd.DataFrame
        Index = Country, columns = metric names, values = mean scores.
    title : str

    Returns
    -------
    plotly.graph_objs.Figure
    """
    clean = sat_df.drop(columns=["n"], errors="ignore").dropna(axis=1, how="all")
    if clean.empty:
        return go.Figure().update_layout(title="Insufficient data")

    z = clean.values.astype(float)
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=list(clean.columns),
        y=list(clean.index),
        colorscale="YlGn",
        zmin=1, zmax=5,
        text=[[f"{v:.2f}" if not pd.isna(v) else "–" for v in row] for row in z],
        texttemplate="%{text}",
        hovertemplate="Country: %{y}<br>Metric: %{x}<br>Score: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        height=max(320, len(clean) * 55 + 130),
        xaxis_tickangle=-40,
        margin=dict(l=110, r=20, t=70, b=150),
    )
    return fig
