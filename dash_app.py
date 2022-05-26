# Import Modules
import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input

import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


# Get Data
df_origin = pd.read_csv('data.csv')

# Get External CSS Sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Init Dash App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# <----------------------------> #
# <-------- Web Layout --------> #
# <----------------------------> #

app.layout = html.Div([
    
    html.H1(id= 'Title1', children= 'Visualization Dashboard of Mental Health Treatments During Covid Quarantine',
            style= {'text-align':'left'}),
    
    # Select the Dataframe
    html.H6(id= 'optionTitle1', children= 'Focus on a Group', style= {'text-align':'left'}),
    
    dcc.Dropdown(id= 'option1', value= 'By Age', multi= False,
                 options= [{'label': x, 'value': x} for x in df_origin['Group'].unique()]),
    
    html.Div([
        html.Div([
            # (Subgroup) Select Plot
            html.H6(id= 'leftOptionTitle1', children= 'Focus on a Subgroup', style= {'text-align':'left'}),
            
            dcc.Dropdown(id= 'leftOption1', 
                         options= [{'label': x, 'value': x} for x in df_origin['Subgroup'].unique()],
                         value= '40 - 49 years',
                         multi= False,
                         clearable= False),
            
            # (Indicator) Select Lines on Line Plots
            html.H6(id='leftOptionTitle2',children='Plot Indicator by Subgroup', style={'text-align':'left'}),
            
            dcc.Dropdown(id='leftOption2', value= ['Took Prescription Medication'], multi=True, 
                         options= [{'label': x, 'value': x} for x in df_origin['Indicator'].unique()]),
            
            # Pie Chart of all Indicator of (Subgroup)
            dcc.Graph(id='pie-graph', figure={}),
            
            # Line Plot of (Subgroup), Displaying Lines (Indicator)
            dcc.Graph(id='my-graph', figure= {}, clickData= None, hoverData= None)
            
        ], className= 'six columns'),
        
        html.Div([
            # (Subgroup) Select Lines on Each Plot
            html.H6(id='rightOptionTitle1',children='Plot Subgroups by Indicator',style={'text-align':'left'}),
            
            dcc.Dropdown(id= 'rightOption1', 
                         options= [{'label': x, 'value': x} for x in df_origin['Subgroup'].unique()],
                         value= ['18 - 29 years', '70 - 79 years'],
                         multi= True),
            
            # Line Plot for Indicator 1: 'Took Prescription Medication'
            dcc.Graph(id= 'indicator1', figure= {}),
            
            # Line Plot for Indicator 2: 'Received Counseling or Therapy'
            dcc.Graph(id= 'indicator2', figure= {}),
            
            # Line Plot for Indicator 3: 'Prescription Medication And/Or Counseling or Therapy'
            dcc.Graph(id= 'indicator3', figure= {}),
            
            # Line Plot for Indicator 4: 'No Treatment, Despite Individual\'s Need of Treatment'
            dcc.Graph(id= 'indicator4', figure= {})
            
                
        ], className= 'six columns')
    ])
])

# <---------------------------> #
# <-------- Callbacks --------> #
# <---------------------------> #

# <-------- Option Menus --------> #

# Making the Subgroup Choices based on Group Choice
@app.callback(
    Output(component_id= 'leftOption1', component_property= 'options'),
    Output(component_id= 'rightOption1', component_property= 'options'),
    Input(component_id= 'option1', component_property= 'value')
)
def get_subgroup_choices(group):
    df_main = df_origin[df_origin['Group'] == group]
    choice = [{'label': x, 'value': x} for x in df_main['Subgroup'].unique()]
    return choice, choice # List of Subgroups


# <---- Left Side ----> #
# Plotting Line Plot based on Indicator Choice
@app.callback(
    Output(component_id= 'my-graph', component_property= 'figure'),
    Input(component_id= 'leftOption1', component_property= 'value'),
    Input(component_id= 'leftOption2', component_property= 'value')
)
def plot_indicator_linePlot(subgroup, indicators):
    df_sub = df_origin[df_origin['Subgroup'] == subgroup]
    df = df_sub[df_sub['Indicator'].isin(indicators)]
    fig = px.line(data_frame= df, x= 'Time Period', y= 'Value', color= 'Indicator',
                  error_y= 'Spread', error_y_minus= 'Spread')
    fig.update_traces(mode='lines+markers')
    return fig

# Plotting Pie Chart based on Subgroup Choice
@app.callback(
    Output(component_id= 'pie-graph', component_property= 'figure'),
    Input(component_id= 'my-graph', component_property= 'hoverData'),
    Input(component_id= 'my-graph', component_property= 'clickData'),
    Input(component_id= 'my-graph', component_property= 'selectedData'),
    Input(component_id= 'leftOption1', component_property= 'value')
)
def update_side_graph(hov_data, clk_data, slct_data, subgroup):
    if hov_data is None:
        df_sub = df_origin[df_origin['Subgroup'] == subgroup]
        df = df_sub[df_sub['Time Period'] == 13]
        
        fig = px.pie(data_frame=df, values='Value', names='Indicator',
                      title=f'Percent Chance of {subgroup} in Indicator during Time Period: 13')
        return fig
    
    else:
        print(f'hover data: {hov_data}')
        df_sub = df_origin[df_origin['Subgroup'] == subgroup]
        time_period = hov_data['points'][0]['x']
        df = df_sub[df_sub['Time Period'] == time_period]
        
        fig = px.pie(data_frame=df, values='Value', names='Indicator',
                      title=f'Percent Chance of {subgroup} in Indicator during Time Period: {time_period}')
        return fig

# <---- Right Side ----> #
# Plot Lines based on Subgroup Choice
@app.callback(
    Output(component_id= 'indicator1', component_property= 'figure'),
    Output(component_id= 'indicator2', component_property= 'figure'),
    Output(component_id= 'indicator3', component_property= 'figure'),
    Output(component_id= 'indicator4', component_property= 'figure'),
    Input(component_id= 'rightOption1', component_property= 'value')
)
def subgroups_among_indicators(subgroup):
    # Indicator 1: 'Took Prescription Medication'
    df_ind1 = df_origin[df_origin['Indicator'] == 'Took Prescription Medication']
    df = df_ind1[df_ind1['Subgroup'].isin(subgroup)]
    
    fig1 = px.line(data_frame= df,
                   x= 'Time Period', y= 'Value', color= 'Subgroup',
                   error_y= 'Spread', error_y_minus= 'Spread',
                   title= 'Took Prescription Medication')    
    
    # Indicator 2: 'Received Counseling or Therapy'
    df_ind2 = df_origin[df_origin['Indicator'] == 'Received Counseling or Therapy']
    df = df_ind2[df_ind2['Subgroup'].isin(subgroup)]
    
    fig2 = px.line(data_frame= df, 
                   x= 'Time Period', y= 'Value', color= 'Subgroup',
                   error_y= 'Spread', error_y_minus= 'Spread',
                   title= 'Received Counseling or Therapy')

    # Indicator 3: 'Prescription Medication And/Or Counseling or Therapy'
    df_ind3 = df_origin[df_origin['Indicator'] == 'Prescription Medication And/Or Counseling or Therapy']
    df = df_ind3[df_ind3['Subgroup'].isin(subgroup)]
    
    fig3 = px.line(data_frame= df, 
                   x= 'Time Period', y= 'Value', color= 'Subgroup',
                   error_y= 'Spread', error_y_minus= 'Spread',
                   title= 'Prescription Medication And/Or Counseling or Therapy')
    
    # Indicator 4: 'No Treatment, Despite Individual\'s Need of Treatment'
    df_ind4 = df_origin[df_origin['Indicator'] == 'No Treatment, Despite Individual\'s Need of Treatment']
    df = df_ind4[df_ind4['Subgroup'].isin(subgroup)]
    
    fig4 = px.line(data_frame= df,
                   x= 'Time Period', y= 'Value', color= 'Subgroup',
                   error_y= 'Spread', error_y_minus= 'Spread',
                   title= 'No Treatment, Despite Individual\'s Need of Treatment')
    
    return fig1, fig2, fig3, fig4 

if __name__ == '__main__':
    app.run_server()