#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Import packages
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output


# In[4]:


# Load data
data = pd.read_csv('contributordata_au.csv', encoding='latin1')
data.index = pd.to_datetime(data['Date'])


# In[5]:


# Inspect data
data.head()


# In[6]:


# Add a new column to format and sort dates
data['date_numeric'] =  pd.to_datetime(data['Date'], format='%d/%m/%Y')
data = data.sort_values('pages', ascending=False)


# In[7]:


# Create a new dataframe for contributors dropdown menu
contributors = data['Contributor'].unique() # Extract contributor column - unique values only
contributor_list = np.array(contributors).tolist()
dfc = pd.DataFrame({'c' : contributor_list})
dfc = dfc.sort_values('c', ascending=True) # Sort alphabetically
dfc1 = pd.DataFrame({'c' : ['All BHL Contributors']}) # Create new dataframe with a single row 'All BHL Contributors'
dfc = dfc1.append(dfc) # Append old dataframe to the new dataframe (so 'All' appears at top of list)
dfc = dfc.reset_index(drop=True)
dfc


# In[8]:


# Create a new dataframe for contributors dropdown menu (unique and sorted)
dates_unique = data
dates_unique = dates_unique.sort_values('date_numeric', ascending=False)
dates_unique = dates_unique['Date'].unique()
dates_unique_list = np.array(dates_unique).tolist()
dfd = pd.DataFrame({'d' : dates_unique_list})


# In[9]:


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# In[ ]:


# Initialize the app

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Create initial version of figure
initial_figure1 = px.bar(data[data['Date'] == '1/12/2020'],
                        x='Contributor',
                        y='pages',
                        text='pages')

# Add figure elements

initial_figure1.update_layout(title={
        'text': "Number of pages contributed by each BHL Australia member (at 1 November 2020).",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

# Define app layout

app.layout = html.Div(children=[
    html.Div(className='row', children=[
        html.H1(children='BHL Australia'),
        dcc.Markdown('''[BHL Australia](https://www.biodiversitylibrary.org/collection/bhlau) is a national project working to digitise Australia's biodiversity literature
        and to make it openly accessible online on the [Biodiversity Heritage Library website](https://www.biodiversitylibrary.org/). 
        The digitisation operation is hosted by [Museums Victoria](https://museumsvictoria.com.au/)
        and is nationally funded by the [Atlas of Living Australia](https://www.ala.org.au/). 
        To peruse the 2700+ volumes and 380,000+ pages contributed to BHL by Australia's museums, herbaria, royal societies, field naturalist clubs and government organisations, 
        [click here](https://www.biodiversitylibrary.org/collection/bhlau).'''),  
html.Br(),
dcc.Markdown('''**There are currently 30 Australian organisations contributing to the BHL. The graph below shows their contributions.**'''),        

# Define initial static graph
        
dcc.Graph(id='staticgraph',
           figure = initial_figure1),

html.Br(),                                   
dcc.Markdown('''**To view the contributions for a specific organisation, make your selections below.**'''),    
dcc.Markdown('''*(Note: drops in values across time reflect the reassignment of content from one contributor to another.)*'''),
html.Br(),                                  

# Create the dropdown menu for "Contributors"
        
    dcc.Dropdown(
        id='contributor_dropdown',
        options=[{'label':i, 'value':i} for i in dfc['c'].unique()],
        value='All BHL Contributors',
        placeholder="Select a Contributor", style=dict(width='50%', verticalAlign="middle")),
html.Br(),

# Define the radio buttons for content types
        
   dcc.RadioItems(
        id='input_column',
        options=[
            {'label': 'Titles', 'value': 'titles'},
            {'label': 'Volumes', 'value': 'volumes'},
            {'label': 'Pages', 'value': 'pages'}],
        value='pages'),
html.Br(),        
html.Div(id='totals_for_selected_contributor'),

# Define dynamic graph
        
    dcc.Graph(id='timeseries'),                                   
                                   
dcc.Markdown('''**To view your selected organisations contributions across a date range, select: **'''),  
html.Div(children=''' 1) a date from'''),

# Create the dropdown menu for "Date from"
        
        dcc.Dropdown(
        id='date_from_dropdown',
        options=[{'label':i, 'value':i} for i in dfd['d'].unique()],
        value=dfd['d'].iloc[-1],
        placeholder="Select a from date",
                style={'width': '45%'}),
        
html.Br(),
html.Div(children=''' 2) a date to'''),  

# Create the dropdown menu for "Date to"
        
        dcc.Dropdown(
        id='date_to_dropdown',
        options=[{'label':i, 'value':i} for i in dfd['d'].unique()],
        value=dfd['d'].iloc[0],
        placeholder="Select a to date",
                style={'width': '45%'}),

html.Br(),        

# Create the final output line 
        
dcc.Markdown('''**Output:**'''),
html.Div(id='display-selected-values')

]),
])

# Callbacks

@app.callback(Output('timeseries', 'figure'),
              [Input('contributor_dropdown', 'value'),
              Input('input_column', 'value')])
def update_timeseries(selected_contributor, selected_column):
        data_sub = data.sort_values('date_numeric', ascending=True)
        if selected_contributor != 'All BHL Contributors':
            data_sub = data_sub[data_sub['Contributor'] == selected_contributor]     
            data_sub = data_sub[data_sub['pages'] > 0]
            figure = px.line(data_sub, x='Date', y=selected_column)
            figure_title = u'The numer of {} contributed by the {}'.format(selected_column, selected_contributor,)
        else:
            data_sub = data_sub.groupby('date_numeric')[selected_column].sum()
            figure = px.line(data_sub, labels={
                     "value": selected_column,
                     "date_numeric": "date"
                 })

            figure_title = u'The numer of {} contributed by all BHL contributors'.format(selected_column,)
            
        figure.update_layout(
            title={
        'text': figure_title,
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}, showlegend=False)
        return figure

@app.callback(
    Output('totals_for_selected_contributor', 'children'),
    Input('contributor_dropdown', 'value'),
    Input('input_column', 'value'))

def totals_for_a_contributor(selected_contributor, selected_content_type):
    if selected_contributor != 'All BHL Contributors':
        value_total_selected_contributor = data[(data['Date'] == dfd['d'].iloc[0]) & (data['Contributor'] == selected_contributor)][selected_content_type].values[0]
        return u'The {} has contributed a total of {} {} to BHL'.format(selected_contributor, value_total_selected_contributor, selected_content_type,)
    else:
        value_total_selected_contributor = data[data['Date'] == dfd['d'].iloc[0]][selected_content_type].values.sum()
        return u'All BHL contributors have together contributed {} {} to BHL.'.format(value_total_selected_contributor, selected_content_type,) 

@app.callback(
    Output('display-selected-values', 'children'),
    Input('contributor_dropdown', 'value'),
    Input('input_column', 'value'),
    Input('date_from_dropdown', 'value'),
    Input('date_to_dropdown', 'value'))

def set_display_children(selected_contributor, selected_content_type, selected_date_from, selected_date_to):
    if selected_contributor != 'All BHL Contributors':
        value_date_to = data[(data['Date'] == selected_date_to) & (data['Contributor'] == selected_contributor)][selected_content_type].values[0]
        value_date_from = data[(data['Date'] == selected_date_from) & (data['Contributor'] == selected_contributor)][selected_content_type].values[0]
        value_date_range = value_date_to - value_date_from
        return u'The {} has contributed {} {} to BHL between {} and {}'.format(selected_contributor, value_date_range, selected_content_type, selected_date_from, selected_date_to,)
    else:
        value_date_to = data[(data['Date'] == selected_date_to)][selected_content_type].values[0]
        value_date_from = data[(data['Date'] == selected_date_from)][selected_content_type].values[0]
        value_date_range = value_date_to - value_date_from
        return u'All BHL contributors have together contributed {} {} to BHL between {} and {}.'.format(value_date_range, selected_content_type, selected_date_from, selected_date_to,)        

if __name__ == '__main__':
    app.run_server(debug=False)


# In[ ]:




