import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data
spacex_df   = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Build dropdown options list (add “All Sites” first)
launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

# ─────────────────── Dash app ───────────────────
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    # ── Task 1 · Launch‑site dropdown ─────────────────────────────
    dcc.Dropdown(id='site-dropdown',
                 options=dropdown_options,
                 value='ALL',
                 placeholder='Select a Launch Site here',
                 searchable=True),
    html.Br(),

    # ── Task 2 · Success pie‑chart ─────────────────────────────—
    dcc.Graph(id='success-pie-chart'),
    html.Br(),

    # ── Task 3 · Payload range slider ───────────────────────────
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000',
                           7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),
    html.Br(),

    # ── Task 4 · Payload‑vs‑success scatter plot ────────────────
    dcc.Graph(id='success-payload-scatter-chart')
])

# ─────────────────── Callbacks ───────────────────

# Task 2: pie‑chart (site → pie)
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value'))
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Success counts per site (class == 1)
        success_counts = (spacex_df[spacex_df['class'] == 1]
                          .groupby('Launch Site')['class']
                          .count()
                          .reset_index(name='Successes'))
        fig = px.pie(success_counts, values='Successes', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        # Success vs Failure counts for the chosen site
        filtered = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = (filtered.groupby('class')
                                   .size()
                                   .reset_index(name='Count'))
        outcome_counts['Outcome'] = outcome_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(outcome_counts, values='Count', names='Outcome',
                     title=f'Success vs. Failure for {selected_site}')
    return fig


# Task 4: scatter plot (site + payload range → scatter)
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown',  'value'),
     Input('payload-slider', 'value')])
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)

    if selected_site != 'ALL':
        mask &= spacex_df['Launch Site'] == selected_site

    filtered_df = spacex_df[mask]

    fig = px.scatter(filtered_df,
                     x='Payload Mass (kg)',
                     y='class',
                     color='Booster Version',
                     title=('Payload vs. Outcome for all Sites'
                            if selected_site == 'ALL'
                            else f'Payload vs. Outcome for {selected_site}'),
                     labels={'class': 'Launch Outcome (0 = Fail, 1 = Success)'})
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
