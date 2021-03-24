import datetime

import dash
from dash_table import DataTable
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import deque
from dash.dependencies import Input, Output
import sys
import numpy as np
from flask import request
import time
from multiprocessing import Process, Queue


class Visual:

    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    def __init__(self, qDisp, qStart, qData):
        self.start = False
        self.qDisp = qDisp
        self.qStart = qStart
        self.qData = qData
        
        self.oldTime = time.time()
        
        self.maxData = 20
        self.maxDataE = 20
        
        prices, self.currentDateTime, self.equipes = self.qDisp.get()
        self.X = np.full(self.maxData,self.currentDateTime)
        self.dACPC = np.full(self.maxData, prices['ACPC'])
        self.dAME = np.full(self.maxData, prices['AME'])
        self.dOZV = np.full(self.maxData, prices['OZV'])
        self.dSHT = np.full(self.maxData, prices['SHT'])
        self.dLAL = np.full(self.maxData, prices['LAL'])
        self.dETF = np.full(self.maxData, prices['ETF'])
        
        self.XE = np.full(self.maxDataE,self.currentDateTime)
        self.totalValues = {}
        
        self.column = [{'id':0,'name':'Équipe'},
                       {'id':1,'name':'Total'},
                       {'id':2,'name':'Cash'},
                       {'id':3,'name':'ACPC'},
                       {'id':4,'name':'AME'},
                       {'id':5,'name':'OZV'},
                       {'id':6,'name':'SHT'},
                       {'id':7,'name':'LAL'},
                       {'id':8,'name':'ETF'}]
        
        titles = ("ACPC:",
                    "AME:",
                    "OZV:",
                    "SHT:",
                    "LAL:",
                    "ETF:")
        self.fig = plotly.subplots.make_subplots(rows=6, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=titles)
        self.figTot = go.Figure()
        self.table = go.Figure()
        
        self.app = dash.Dash(__name__, external_stylesheets=self.external_stylesheets)
        self.app.layout = html.Div(
            html.Div([
                html.H4('Compétition IEEE'),
                html.Button('Start', id='buttonStart'),
                html.Button('View all data', id='buttonView'),
                html.Button('Stop server', id='buttonStop'),
                html.P(id='StartPlaceholder'),
                html.P(id='ViewPlaceholder'),
                html.P(id='StopPlaceholder'),
                html.Div([
                    html.Div([
                        html.Div(id='live-update-text'),
                        dcc.Graph(id='live-update-graph')
                        ], className="one-third column"),
                    html.Div([
                        dcc.Graph(id='Total_Value'),
                        DataTable(
                            id='Table',
                            data=[]
                        )
                        ], className="two-thirds column"),
                    ], className="row"),
                dcc.Interval(
                    id='interval-component',
                    interval=1000, # in milliseconds
                    n_intervals=0
                )
            ])
        )
        self.app.callback(Output('live-update-text', 'children'),
                  Input('interval-component', 'n_intervals'))(self.update_metrics)
        self.app.callback(Output('live-update-graph', 'figure'),
                  Input('interval-component', 'n_intervals'))(self.update_graph_live)
        self.app.callback(Output('Total_Value', 'figure'),
                  Input('interval-component', 'n_intervals'))(self.update_total_value)
        self.app.callback([Output('Table', 'data'), Output('Table', 'columns')],
                  Input('interval-component', 'n_intervals'))(self.update_table)
        self.app.callback(Output('StartPlaceholder', 'children'),
                          Input('buttonStart', 'n_clicks'))(self.Start)
        self.app.callback(Output('ViewPlaceholder', 'children'),
                          Input('buttonView', 'n_clicks'))(self.View)
        self.app.callback(Output('StopPlaceholder', 'children'),
                          Input('buttonStop', 'n_clicks'))(self.Stop)
    
    def Start(self, n_clicks):
        if n_clicks:
            self.qStart.put(True)
            self.start = True
            return None
        else:
            return None
        
    def View(self, n_clicks):
        if n_clicks:
            self.qData.put(True)
            return None
        else:
            return None
        
    def Stop(self, n_clicks):
        if n_clicks:
            self.qStart.put(False)
            self.shutdown_server()
            
    def getStart(self):
        return self.start
    
    def getStop(self):
        return self.stop
    
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
    
    def update_metrics(self,n):
        style = {'padding': '5px', 'fontSize': '16px'}
        text = [ html.Span('Date et Heure: '+ self.currentDateTime.strftime("%d/%m/%Y, %H:%M:%S"), style=style)]
        return text
    
    
    # Multiple components can update everytime interval gets fired.
    def update_graph_live(self,n):
    
        
        if(self.start):
            self.oldTime = time.time()
            prices, self.currentDateTime, self.equipes = self.qDisp.get()
            
            self.X = np.roll(self.X,-1)
            self.X[-1] = self.currentDateTime
            self.dACPC = np.roll(self.dACPC,-1)
            self.dAME = np.roll(self.dAME,-1)
            self.dOZV = np.roll(self.dOZV,-1)
            self.dSHT = np.roll(self.dSHT,-1)
            self.dLAL = np.roll(self.dLAL,-1)
            self.dETF = np.roll(self.dETF,-1)
            self.dACPC[-1] = (prices['ACPC'])
            self.dAME[-1] = (prices['AME'])
            self.dOZV[-1] = (prices['OZV'])
            self.dSHT[-1] = (prices['SHT'])
            self.dLAL[-1] = (prices['LAL'])
            self.dETF[-1] = (prices['ETF'])
            
            self.fig['layout']['annotations'][0]['text'] = "ACPC: {:.2f}".format(prices['ACPC'])
            self.fig['layout']['annotations'][1]['text'] = "AME: {:.2f}".format(prices['AME'])
            self.fig['layout']['annotations'][2]['text'] = "OZV: {:.2f}".format(prices['OZV'])
            self.fig['layout']['annotations'][3]['text'] = "SHT: {:.2f}".format(prices['SHT'])
            self.fig['layout']['annotations'][4]['text'] = "LAL: {:.2f}".format(prices['LAL'])
            self.fig['layout']['annotations'][5]['text'] = "ETF: {:.2f}".format(prices['ETF'])
            
        
        self.fig.data = []
        #fig = plotly.subplots.make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.05,
         #                                   subplot_titles=titles)
        
        trace = go.Scatter(name="ACPC", x=(self.X), y=(self.dACPC), mode = 'lines+markers',connectgaps=True)
        self.fig.append_trace(trace, 1, 1)
        
        trace = go.Scatter(name="AME", x=(self.X), y=(self.dAME), mode = 'lines+markers',connectgaps=True)
        self.fig.append_trace(trace, 2, 1)
        
        trace = go.Scatter(name="OZV", x=(self.X), y=(self.dOZV), mode = 'lines+markers',connectgaps=True)
        self.fig.append_trace(trace, 3, 1)
        
        trace = go.Scatter(name="SHT", x=(self.X), y=(self.dSHT), mode = 'lines+markers',connectgaps=True)
        self.fig.append_trace(trace, 4, 1)
        
        trace = go.Scatter(name="LAL", x=(self.X), y=(self.dLAL), mode = 'lines+markers',connectgaps=True)
        self.fig.append_trace(trace, 5, 1)
        
        trace = go.Scatter(name="ETF", x=(self.X), y=(self.dETF), mode = 'lines+markers',connectgaps=True)
        self.fig.append_trace(trace, 6, 1)
        
        
        self.fig.update_layout(showlegend=False, height=800,
                               xaxis={'type': 'date',
                                      'rangebreaks':[dict(bounds=["sat", "mon"]),
                                                     {'pattern': 'hour', 'bounds': [16, 9.5]}]},
                              margin=dict(
                                    l=0,
                                    r=0,
                                    b=0,
                                    t=30,
                                    pad=4
                                ))
        
        
        return self.fig
    
    def update_total_value(self,n):
        self.figTot.data = []
       
        if self.start:
            self.XE = np.roll(self.XE,-1)
            self.XE[-1] = self.currentDateTime
            for key in self.equipes.keys():
                if not key in self.totalValues:
                    self.totalValues[key] = np.full(self.maxDataE, self.equipes[key][1])
                else:
                    self.totalValues[key] = np.roll(self.totalValues[key],-1)
                    self.totalValues[key][-1] = (self.equipes[key][1])
                
                trace = go.Scatter(name=key, x=(self.XE), y=(self.totalValues[key]), mode = 'lines+markers',connectgaps=True)
                self.figTot.add_trace(trace)
                
        self.figTot.update_layout(xaxis={'type': 'date',
                                      'rangebreaks':[dict(bounds=["sat", "mon"]),
                                                     {'pattern': 'hour', 'bounds': [16, 9.5]}]})
        
        return self.figTot
    
    def update_table(self,n):
        values = [self.equipes[key] for key in self.equipes.keys()]
        
        return values, self.column