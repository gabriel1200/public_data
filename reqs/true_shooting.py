#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

import plotly.express as px
import plotly
plotly.offline.init_notebook_mode(connected=True)
import plotly.graph_objects as go


# In[2]:


start_year = 2007
end_year = 2022


# In[3]:


averages = pd.read_html('https://www.basketball-reference.com/leagues/NBA_stats_per_game.html#stats', header=1)[0]

averages= averages.dropna()

averages = averages[averages['Season']!='Season']
averages['PTS'] = averages['PTS'].astype(float)
averages['FGA'] = averages['FGA'].astype(float)
averages['FTA'] = averages['FTA'].astype(float)
averages['TS%'] = averages['PTS']/(2* (averages['FGA'] + .44 *averages['FTA'] ))
averages['TS%'] = averages['PTS']/(2* (averages['FGA'] + .44 *averages['FTA'] ))
averages = averages[['TS%','Season']]
averages['Season'] = averages['Season'].str[:4]
averages['Season'] = averages['Season'].astype(int)
averages['Season']+=1
averages = averages[averages['Season']>=start_year]
averages = averages[averages['Season']<=end_year]
averages = averages.iloc[::-1]


# In[4]:


s_data = averages.to_dict('split')['data']
seasons = {}
options = []
for i in s_data:
    seasons[int(i[1])] = float(i[0])
    options.append(int(i[1]))


# In[5]:


options


# In[6]:


from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import io


# In[7]:


import chart_studio.plotly as py
import chart_studio.tools as tls
from ipywidgets import interactive, HBox, VBox



# In[8]:


import sys
import pandas as pd

    
def get_table(link_1,link_2):

    df = pd.read_html(link_1)[0]
    df_2 = pd.read_html(link_2)[0]
    df = df.dropna(subset = ['MP'])
    df_2 = df_2.dropna(subset = ['MP','TS%'])
    df = df[df['MP'] != 'MP']
    df_2 = df_2[df_2['MP'] != 'MP']
    final_df = df.merge(df_2)
    final_df['MP'] = final_df['MP'].astype(float)
    final_df['PTS'] = final_df['PTS'].astype(float)
    final_df['TS%'] = final_df['TS%'].astype(float)
    final_df = final_df[final_df['MP'] >600]
    final_df['TS%'] *=100
    final_df = final_df.drop(columns = ['Unnamed: 24','Unnamed: 29','Unnamed: 19'])
    send_df = final_df[['Player','TS%','PTS','MP','Tm']]

    
    return send_df
    
def main(my_dict):
    team = my_dict['team']
    df = get_table()
    return df.to_dict()


# In[9]:


link_1 ='https://www.basketball-reference.com/leagues/NBA_2011_per_poss.html#per_poss_stats'
link_2 = 'https://www.basketball-reference.com/leagues/NBA_2011_advanced.html#advanced_stat'

df = pd.read_html(link_1)[0]
df_2 = pd.read_html(link_2)[0]

#df_2 = df_2.dropna()


# In[10]:


def get_tables(start_year,stop_year):
    tables = []
    for i in range(start_year,stop_year + 1):
        link_1 ='https://www.basketball-reference.com/leagues/NBA_'+str(i)+'_per_poss.html#per_poss_stats'
        link_2 = 'https://www.basketball-reference.com/leagues/NBA_'+str(i)+'_advanced.html#advanced_stat'

        df = get_table(link_1,link_2)
        tables.append(df)
    return tables


# In[11]:


tables = get_tables(start_year,end_year)


# In[12]:


#df = tables[0]


# In[13]:


def get_buttons(teams,year):
    my_list = []
    i = 0
    length = len(teams)
    seen = [False for i in range(length+ 1) ]

    seen[i] = True
    my_list.append(dict(label = 'all_teams',

                      args = [{'visible':[i for i in seen]},
                              {'title': 'all_teams',
                               'showlegend':False}]))
    seen[i] = False
    i +=1
    for team in teams:
        #print(i)
        df_team = df[df['Tm'] == team]
        seen[i] = True

        my_list.append(dict(label = team,
                      method = 'update',

                      args = [{'visible':[i for i in seen]},
                              {'title': str(year) + ' '+team,
                               'showlegend':False}]))
        seen[i] = False
        i+=1
    return my_list


# In[15]:


#zmax = df['TS%'].max()
#zmin = df['TS%'].min()
#zmin


# In[16]:


def full_trace(fig,df,zmin,zmax,av_shooting):
    fig.add_trace(
            go.Scatter(

                visible = True,
                x = df['PTS'],
                y = df['TS%'],
                customdata = df['TS%'] - av_shooting,

                text = df['Player'],
                hovertemplate =
                '<b>%{text}</b>'+
        '<br><i>Points per 75</i>: %{x:.2f}<br>'+
        'True Shooting: %{y}'
                + ' <br>Relative True Shooting: %{customdata:.2f}<extra></extra></br>'
        ,
                name = 'all_teams',
                marker=dict(
                cmin=zmin ,
                cmax=zmax,
                size=df['MP'] / 65,
                colorbar=dict(
                title="Scoring Efficiency"


            ),
            autocolorscale = True,
            color=  df['TS%'],

        ),


        mode="markers"
            ))
    return fig
    


# In[17]:


def team_trace(fig,df,teams,zmin,zmax,av_shooting):
    for team in teams:
        df_team = df[df['Tm'] == team]


        fig.add_trace(
            go.Scatter(
                
                visible = False,
                x = df_team['PTS'],
                y = df_team['TS%'],
                customdata = df_team['TS%'] - av_shooting,
                
                text = df_team['Player'],
                hovertemplate =
                '<b>%{text}</b>'+
        '<br><i>Points per 75</i>: %{x:.2f}<br>'+
        'True Shooting: %{y}'
                + ' <br>Relative True Shooting: %{customdata:.2f}<extra></extra></br>'
        ,
                name = team,
                marker=dict(
                cmin=zmin ,
                cmax=zmax,
                size=df_team['MP'] / 65,
                colorbar=dict(
                title="Scoring Efficiency"


            ),
            autocolorscale = True,
            color=  df_team['TS%'],

        ),


        mode="markers"
            )

        ) 
    return fig


# In[18]:


def season_graph(df,year,true_shooting):
    fig = go.Figure()
    teams = list(df['Tm'].unique())
    my_buttons = get_buttons(teams,year)
    zmax = df['TS%'].max()
    zmin = df['TS%'].min()
    fig.update_layout(
        title={
        'text':str(year) +" Season",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    updatemenus=[go.layout.Updatemenu(
            active=0,
            buttons= my_buttons,
            direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,


    )],
    font=dict(
        size=15,
    )
    )
   
    fig = full_trace(fig,df,zmin,zmax,true_shooting)
    fig = team_trace(fig,df,teams,zmin,zmax,true_shooting)
    fig.update_layout(
        autosize=False,
        width=1000,
        height=800,
    showlegend= False)  

    fig.update_layout(yaxis_range=[int(zmin -3),int(zmax +2)], xaxis_range = [0,50])
    fig.update_yaxes(tickvals=[i for i in range(int(zmin)-3,int(zmax)+3,5)], title_text = "True Shooting %",)
    fig.update_xaxes(tickvals = [i for i in range (5,50,5)], title_text = 'Points per 100 Possesions')
    fig.add_hline(y=true_shooting)
    return fig


# In[19]:


#fig = season_graph(df,2009,seasons[2009]*100)
#fig.show()


# In[20]:


#fig.write_html("index.html")


# In[21]:


app = JupyterDash(__name__)
app.layout = html.Div(children=[
    html.H1(children='Scoring by Year', style={'text-align': 'center'}),
    html.Div(children='Player scoring & true shooting', style={'text-align': 'center'}),

    html.Div([
        html.Label(['Choose a season:'],style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='dropdown',
            options=options,
                
            value=start_year,
            style={"width": "60%"}),
        
    html.Div(dcc.Graph(id='graph')),        
        ]),

])

@app.callback(
    Output('graph', 'figure'),
    [Input(component_id='dropdown', component_property='value')]
)

def update_output(value):
    print(value)
    print(seasons[value])
    t_num = options.index(value)
    fig = season_graph(tables[t_num],value,seasons[value]* 100)
    return fig


# Run app and display result inline in the notebook
if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




