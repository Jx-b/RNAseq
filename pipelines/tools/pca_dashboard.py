#!/usr/bin/env python3
# -*- codinchmodg: utf-8 -*-

# Imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
import numpy as np
import pandas as pd

from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import json

class Dash_PCA(dash.Dash):
    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    
    def __init__(self, data, labels):
        super().__init__(__name__, external_stylesheets= self.external_stylesheets)
        self.title = 'PCA analysis'
        self.labels = labels
        self.labelled_data = pd.DataFrame.join(data, labels)
        self.projected_data, self.variance_explained, self.components = self.perform_pca(data)

        #Create layout
        self.layout = html.Div([    
            dcc.Store(id='pca_storage', data={}),
            
            html.Div([
                        html.H4('Feature scaling (zscore)'),
                        dcc.RadioItems(
                            id= 'scaling_radio',
                            options=[
                                {'label': 'On', 'value': 'On'},
                                {'label': 'Off', 'value': 'Off'}
                            ],
                            value= 'On',
                            labelStyle={'display': 'inline-block'}
                    ),], style= {'grid-area': 'pca-options'}
                 ),
            
            html.Div([
                        html.H4('Color by'),
                        dcc.Dropdown(
                            id = 'colorby_dropdown',
                            options= [{'label': group, 'value': group} for group in self.labelled_data.columns],
                            value= self.labels.columns[0],   
                    )], style= {'grid-area': 'scatter-plot-options'}
                 ),
            html.Div([
                    dcc.Graph(
                            id= 'histo_var',
                            figure= self.plot_var(self.variance_explained), 
                            style= {'grid-area': 'var'}
                    ),
                    dcc.Graph(
                            id= 'histo_coef',
                            figure= self.plot_coef(self.components), 
                            style= {'grid-area': 'coef'}
                    )
                ],
                style= {'grid-area': 'histo',
                        'display': 'grid', 'grid-template-rows': '1fr 1fr', 'grid-template-areas': '"var" "coef"'}
            ),
            
            dcc.Graph(
                    id='3d scatter',
                    figure= self.plot_pca(self.projected_data, self.variance_explained, self.labels.iloc[:,0]),
                    config=dict(showSendToCloud=True),
                    style= {'grid-area': 'pca'}
            ),
            
            html.Div([
                html.H4(children='Data table'),
                self.generate_table(self.labels)
                ], 
                style= {'grid-area': 'table'}

            )], style= {'display': 'grid', 
                    'grid-template-columns': '1fr 2fr', 
                    'grid-template-rows': '8% 50% auto', 
                    'grid-template-areas': ' "pca-options scatter-plot-options" "histo pca" "table table"',
                    'margin-left': '5%',
                    'margin-right': '5%'
                    }
    )
        
    def perform_pca(self, data, zscore=True):
        """Performs principal component analysis on a dataframe"""
        
        if zscore:
            # Standardise using StandardScaler
            norm_data= pd.DataFrame(StandardScaler().fit_transform(data), columns=data.columns)
        else:
            norm_data=data

        # Perform PCA
        pca = PCA(n_components=None)    
        pca.fit(norm_data)
        variance_explained = pca.explained_variance_ratio_ * 100
        projected_data = pd.DataFrame(pca.transform(norm_data), index= data.index, 
                                      columns= ['PC'+str(i+1) for i in range(len(pca.explained_variance_ratio_))])
        components = pd.DataFrame(pca.components_, columns=norm_data.columns)

        return projected_data, variance_explained, components
        
    def plot_group_pca(self, projected_data, color_by):
        """Plots a 3D scatter plot of 3 consecutive principal components with dots colored by group"""
        pca_data = pd.DataFrame.join(projected_data, color_by)
        data= [go.Scatter3d(
                        x= group.PC1,
                        y= group.PC2,
                        z= group.PC3,
                        text= group.index,
                        mode='markers',
                        marker= {
                            'size': 10,
                            'color': idx,
                            'opacity': .8,
                        },
                        name= name) for idx,(name, group) in enumerate(pca_data.groupby(color_by))]
        return data
    
    def plot_heatmap_pca(self, projected_data, color_by):
        """Plots a 3D scatter plot of 3 consecutive principal components with dots colored by value"""
        data=  [go.Scatter3d(
                        x= projected_data.PC1,
                        y= projected_data.PC2,
                        z= projected_data.PC3,
                        text= projected_data.index,
                        mode='markers',
                        marker= {
                            'size': 10,
                            'color': color_by,
                            'colorscale': 'Viridis',
                            'opacity': .8,
                        },
                        name= color_by.name
                    )
                ]
        return data
    
    def plot_pca(self, projected_data, variance_explained, color_by):
        """Plots a 3D scatter plot of 3 consecutive principal components"""
        if np.issubdtype(color_by.dtype, np.number):
            data = self.plot_heatmap_pca(projected_data, color_by)
        else:
            data = self.plot_group_pca(projected_data, color_by)
        layout = go.Layout(
                            title= 'PCA',
                            scene= {
                                    'xaxis': {'title': f'PC1 ({variance_explained[0]:.2f}% of variance)'},
                                    'yaxis': {'title': f'PC2 ({variance_explained[1]:.2f}% of variance)'},
                                    'zaxis': {'title': f'PC3 ({variance_explained[2]:.2f}% of variance)'}
                                    },
                            clickmode= 'event+select',
                            uirevision= True
                        )
        return {'data': data, 'layout':layout}

    def plot_var(self, variance_explained):
        """Plots a bar chart of the percentage of variance explained by each principal component"""
        figure= {
                'data': [go.Bar(
                    x= ['PC'+str(i+1) for i in range(len(variance_explained))],
                    y= variance_explained,
                    text= [f'{x:.2f}%' for x in variance_explained],
                    hoverinfo= 'text',
                    selectedpoints= [0],
                    )],
                'layout': go.Layout(
                            title= 'Explained variance',
                            yaxis= {'title':{'text':'% Variance explained'}},
                            clickmode= 'event+select',
                            )
                }
        return figure
    
    def plot_coef(self, components, PC=0, selectedData= None, max_bar_to_plot=10):
        """Plots a bar chart of the coeficient attached to each feature for the selected principal component"""
        sort_comp = components.sort_values(PC, axis=1, ascending=False)
        if len(sort_comp.columns)>max_bar_to_plot:
            sort_comp = sort_comp.iloc[:,:max_bar_to_plot]
        if selectedData:
            try:
                selectedData = [list(sort_comp.columns).index(selectedData)]
            except ValueError:
                selectedData = None
            
        figure= {
                'data': [go.Bar(
                    x= sort_comp.columns,
                    y= sort_comp.iloc[PC,:],
                    selectedpoints= selectedData,
                    )],
                'layout': go.Layout(
                            title= f'PC{PC+1} Components',
                            clickmode= 'event+select',
                            )
                }

        return figure

    def generate_table(self, df):
        """Generate a html table displaying the content of a pandas dataframe"""
        dataframe = df.reset_index()
        table = dash_table.DataTable(
            id= 'table',
            columns= [{"name": i, "id": i, 'deletable': True} for i in dataframe.columns],
            data= dataframe.to_dict("rows"),
            sorting=True,
            filtering=True,
            sorting_type='multi',
            style_as_list_view=True,
            style_cell={'padding': '5px'},
            style_header={
                'fontWeight': 'bold'
                },
            n_fixed_rows= 2,
            )

        return table

def run_dashboard(data, labels):
    """Creates a dashboard for visual exploration of PCA analysis
    
    data: a pandas dataFrame whose columns contain the features on which to perform PCA
    labels: a pandas dataFrame whose columns contain the labels, the index must be identical to data
    """
    ### Create App ###
    app = Dash_PCA(data, labels)
    
    ### Add Interactivity ###
    @app.callback(
        dash.dependencies.Output('pca_storage', 'data'),
        [dash.dependencies.Input('scaling_radio', 'value')])
    def update_pca(scaling):
        #recompute pca
        zscore = True if scaling == 'On' else False
        projected_data, variance_explained, components = app.perform_pca(data, zscore)
        pca_results = { 
            'projected_data': projected_data.to_json(), 
            'variance_explained': json.dumps(variance_explained.tolist()),
            'components': components.to_json()
                      }
        return pca_results
        
    @app.callback(
        dash.dependencies.Output('histo_var', 'figure'),
        [dash.dependencies.Input('pca_storage', 'data')])
    def update_var_plot(pca_results):
        variance_explained = json.loads(pca_results['variance_explained'])
        return app.plot_var(variance_explained)
    
    @app.callback(
        dash.dependencies.Output('colorby_dropdown', 'value'),
        [dash.dependencies.Input('histo_coef', 'clickData')])
    def select_feature(clickData):
        if clickData:
            return clickData['points'][0]['x']
        else:
            return app.labels.columns[0]
    
    @app.callback(
        dash.dependencies.Output('histo_coef', 'figure'),
        [dash.dependencies.Input('colorby_dropdown', 'value'),
         dash.dependencies.Input('histo_var', 'selectedData'), 
         dash.dependencies.Input('pca_storage', 'data')])
    def update_coef_plot(dropdown_value, selectedPC, pca_results):
        PC = selectedPC['points'][0]['pointIndex'] if selectedPC else 0
        #read json data from pca_results
        components = pd.read_json(pca_results['components'])
        return app.plot_coef(components, PC, dropdown_value)
    
    @app.callback(
        dash.dependencies.Output('3d scatter', 'figure'),
        [dash.dependencies.Input('colorby_dropdown', 'value'), 
         dash.dependencies.Input('pca_storage', 'data')])
    def update_coloring(dropdown_value, pca_results):
        #read json data from pca_results
        projected_data = pd.read_json(pca_results['projected_data'])
        variance_explained = json.loads(pca_results['variance_explained'])
        return app.plot_pca(projected_data, variance_explained, app.labelled_data.loc[:,dropdown_value])

    #link table to scatter plot
    @app.callback(
        dash.dependencies.Output('table', 'style_data_conditional'),
        [dash.dependencies.Input('3d scatter', 'clickData'), dash.dependencies.Input('table', 'derived_virtual_indices')])
    def highlight_row(clickData, rows):
        if clickData:
            try:
                row = rows.index(clickData['points'][0]['text'])
            except ValueError:
                return []
            return [{
                "if": {"row_index": row},
                "backgroundColor": "#3D9970",
                'color': 'white'
            }]
    
    app.run_server(debug=False)

if __name__ == '__main__':
    
    # Import data
    iris_data = datasets.load_iris()
    data = pd.DataFrame(iris_data['data'], columns= iris_data['feature_names'])
    labels = pd.DataFrame(iris_data['target'], columns = ['class']).apply(lambda x : iris_data['target_names'][x])
    labels['class_num'] = iris_data['target']

    # Create App
    run_dashboard(data, labels)
