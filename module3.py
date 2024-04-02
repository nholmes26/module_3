import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Read data from CSV
data = pd.read_csv('food_access.csv')

# Create Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    dcc.Dropdown(
        id='state-dropdown',
        options=[{'label': state, 'value': state} for state in data['State'].unique()],
        value=''  # Default value
    ),
    dcc.Dropdown(
        id='county-dropdown',
        options=[],  # Will be updated based on selected state
        value=''  # Default value
    ),
    html.Div(id='choropleth-container'),
    html.Div([
        html.Div(id='bar-chart-container', className='six columns'),
        html.Div(id='scatter-plot-container', className='six columns'),
    ], className='row'),
])

# Callback to update county dropdown based on selected state
@app.callback(
    Output('county-dropdown', 'options'),
    [Input('state-dropdown', 'value')]
)
def update_county_dropdown(selected_state):
    if selected_state:
        counties = [{'label': county, 'value': county} for county in data[data['State'] == selected_state]['County'].unique()]
    else:
        counties = []
    return counties

# Callback to update choropleth map based on selected state
@app.callback(
    Output('choropleth-container', 'children'),
    [Input('state-dropdown', 'value')]
)
def update_choropleth(selected_state):
    if selected_state:
        # Filter data based on selected state
        filtered_data = data[data['State'] == selected_state]
        # Create choropleth map
        fig = px.choropleth(filtered_data, geojson='https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json', locations='FIPS', color='Low_Income_Rate_1-2_Mile',
                           color_continuous_scale="reds",
                           scope="usa",
                           labels={'Low_Income_Rate_1-2_Mile':'Low Income Rate'},
                           hover_name='County', 
                           title='Low Income Rates by County')
    else:
        # Create choropleth map for the entire US
        fig = px.choropleth(data, geojson='https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json', locations='FIPS', color='Low_Income_Rate_1-2_Mile',
                           color_continuous_scale="reds",
                           scope="usa",
                           labels={'Low_Income_Rate_1-2_Mile':'Low Income Rate'},
                           hover_name='County', 
                           title='Low Income Rates by County')
    
    # Return choropleth map
    return dcc.Graph(figure=fig)

# Callback to update line plot based on selected state and county
@app.callback(
    Output('bar-chart-container', 'children'),
    [Input('state-dropdown', 'value'),
     Input('county-dropdown', 'value')]
)
def update_line_plot(selected_state, selected_county):
    if selected_state and selected_county:
        # Filter data based on selected state and county
        filtered_data = data[(data['State'] == selected_state) & (data['County'] == selected_county)]
    elif selected_state:
        # Filter data based on selected state
        filtered_data = data[data['State'] == selected_state]
    else:
        filtered_data = data  # No filter applied
    # Create line plot
    line_trace = go.Scatter(
        x=['0.5', '1', '10', '20'],
        y=[filtered_data['Low_Income_Rate_1-2_Mile'].mean(),
           filtered_data['Low_Income_Rate_1_Mile'].mean(),
           filtered_data['Low_Income_Rate_10_Miles'].mean(),
           filtered_data['Low_Income_Rate_20_Miles'].mean()],
        mode='lines+markers',
        name='Low Income Rate',
    )
    line_layout = go.Layout(
        title='Average Low Income Rates at Different Distances',
        xaxis=dict(title='Distance (miles)'),
        yaxis=dict(title='Average Low Income Rate'),
    )
    line_fig = go.Figure(data=[line_trace], layout=line_layout)
    # Return line plot
    return dcc.Graph(figure=line_fig)


# Callback to update scatter plot based on selected state and county
@app.callback(
    Output('scatter-plot-container', 'children'),
    [Input('state-dropdown', 'value'),
     Input('county-dropdown', 'value')]
)
def update_scatter_plot(selected_state, selected_county):
    if selected_state and selected_county:
        # Filter data based on selected state and county
        filtered_data = data[(data['State'] == selected_state) & (data['County'] == selected_county)]
    elif selected_state:
        # Filter data based on selected state
        filtered_data = data[data['State'] == selected_state]
    else:
        filtered_data = data  # No filter applied
    # Create scatter plot
    scatter_trace = go.Scatter(
        x=filtered_data['Low_Income_Rate_1-2_Mile'],
        y=filtered_data['Vehicle_Access_1-2_Mile'],
        mode='markers',
        text=filtered_data['County'],
        marker=dict(
            size=10,
            color='blue',
            opacity=0.5
        )
    )
    scatter_layout = go.Layout(
        title='Low Income Percentage vs No Vehicle Access Houses (over 1/2 mile from supermarket)',
        xaxis=dict(title='Low Income Population Percentage'),
        yaxis=dict(title='No Vehicle Access Households'),
        hovermode='closest'
    )
    scatter_fig = go.Figure(data=[scatter_trace], layout=scatter_layout)
    # Return scatter plot
    return dcc.Graph(figure=scatter_fig)

if __name__ == '__main__':
    app.run_server(debug=True)
