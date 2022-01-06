import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
import plotly.express as px
import scipy.stats as ss
import scikit_posthocs as sp

import data

server = flask.Flask(__name__)  # define flask app.server

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                server=server
                )

# Get the DataFrame that contains the data.
available_countries = data.get_available_countries();
available_countries_label_value_pairs = data.get_available_countries_label_value_pairs()

available_genres = data.get_available_genres();
available_genres_label_value_pairs = data.get_available_genres_label_value_pairs()

df = data.get_data(selected_genres=available_genres,
                   selected_countries=available_countries, selected_range=[0, 10000000])
#

## intial result for the statistical posthoc tests, this gets updated via callbacks afterwards
posthoc_result = sp.posthoc_dunn(df, val_col='vagueTotalPercentage', group_col='hostingLocation',
                                               p_adjust='bonferroni')
posthoc_result = posthoc_result.round(5)
posthoc_result['Country'] = posthoc_result.index
cols = posthoc_result.columns.tolist()
cols = cols[-1:] + cols[:-1]
posthoc_result = posthoc_result[cols]
posthoc_result_dict = posthoc_result.to_dict('records')
##

app.layout = html.Div([

    # Nothing to see here, just for keeping a margin.
    html.Div([

    ], className="one column"),

    # Top Bar
    html.Div([
        html.H1('Vagueness and Readability in Privacy Policies', style={
            'textAlign': 'center'
        }),

        html.Div(
            html.Label('Select the genres you want to include:'), style={'width': 300, 'display': 'inline-block'}
        ),

        html.Div(dcc.Checklist(
            id='genre-checklist-group',
            options=available_genres_label_value_pairs,
            value=available_genres,
            labelStyle={'display': 'inline-block'}
        ), style={'width': '70%', 'display': 'inline-block'}),

        html.Label('Select the countries you want to include:'),
        html.Div(dcc.Dropdown(
            id='selected_countries',
            options=available_countries_label_value_pairs,
            value=available_countries,
            multi=True,
            clearable=False
        ), style={'width': '100%', 'display': 'inline-block'}),

        html.Label('Slider to include policies based on the number of their installments (max value includes 10M+):'),
        html.Div(dcc.RangeSlider(
            id='selected_range',
            min=0,
            max=10000000,
            step=25000,
            value=[0, 10000000],
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": True},
        ), style={'width': '100%'}),
    ], className="eleven columns"),

    # left column
    html.Div([

        # Bloxplots
        html.H4(
            children='Boxplots',
        ),

        html.Div(dcc.Dropdown(
            id='box-y-value-dropdown',
            options=[{'label': label, 'value': value} for label, value in {
                'Percentage occurrence of Vague Terms': 'vagueTotalPercentage',
                'averageMinutesToReadNative': 'averageMinutesToReadNative',
                'SMOGIndex': 'SMOGIndex',
                'FleschKincaidGrade': 'FleschKincaidGrade',
                'ColemanLiau': 'ColemanLiau',
                'AutomatedReadabilityIndex': 'AutomatedReadabilityIndex',
                'GunningFog': 'GunningFog',
                'DaleChall': 'DaleChall',
                'meanReadability': 'meanReadability',
            }.items()],
            value='vagueTotalPercentage',
        ), style={'width': '50%', 'display': 'inline-block'}),

        html.Div(dcc.Dropdown(
            id='box-x-value-dropdown',
            options=[{'label': label, 'value': value} for label, value in {
                'hostingLocation': 'hostingLocation',
                'amountOfInstallsGrouped': 'amountOfInstallsGrouped',
                'MVLocationGenre': 'MVLocationGenre',
                'isNativelyEnglish': 'isNativelyEnglish',
            }.items()],
            value='hostingLocation',
        ), style={'width': '50%', 'display': 'inline-block'}),

        html.Div(dcc.Graph(
            id='box-plot',
            figure=px.box(df, x="amountOfInstallsGrouped", y="vagueTotalPercentage",
                          points="outliers", notched=False, color="amountOfInstallsGrouped",
                          labels={"hostingLocation": "hosting location",
                                  "vagueTotalPercentage": "percentage occurrence of vague terms"},
                          ),
        ), style={'width': '100%', 'display': 'inline-block'}),


    ], className="five columns"),

    # right column
    html.Div([
        # Kruskal Wallis
        html.H4(
            children='Statistical Tests',
        ),

        html.Div(dcc.Dropdown(
            id='statistical-1-value-dropdown',
            options=[{'label': label, 'value': value} for label, value in {
                'Percentage occurrence of Vague Terms': 'vagueTotalPercentage',
                'averageMinutesToReadNative': 'averageMinutesToReadNative',
                'SMOGIndex': 'SMOGIndex',
                'FleschKincaidGrade': 'FleschKincaidGrade',
                'ColemanLiau': 'ColemanLiau',
                'AutomatedReadabilityIndex': 'AutomatedReadabilityIndex',
                'GunningFog': 'GunningFog',
                'DaleChall': 'DaleChall',
                'meanReadability': 'meanReadability',
            }.items()],
            value='vagueTotalPercentage',
        ), style={'width': '40%', 'display': 'inline-block'}),

        html.Div(dcc.Dropdown(
            id='statistical-2-value-dropdown',
            options=[{'label': label, 'value': value} for label, value in {
                'hostingLocation': 'hostingLocation',
                'amountOfInstallsGrouped': 'amountOfInstallsGrouped',
            }.items()],
            value='hostingLocation',
        ), style={'width': '25%', 'display': 'inline-block'}),

        html.Div(dcc.Dropdown(
            id='posthoc-type-dropdown',
            options=[{'label': label, 'value': value} for label, value in {
                'Dunn': 'dunn',
                'Conover': 'conover',
                'Mann-Whitney': 'mann-whitney',
            }.items()],
            value='dunn',
        ), style={'width': '20%', 'display': 'inline-block'}),

        html.Div(dcc.Dropdown(
            id='statistical-adjustment-dropdown',
            options=[{'label': label, 'value': value} for label, value in {
                'Bonferroni': 'bonferroni',
                'Sidak': 'sidak',
                'Holm': 'holm',
                'Holm-sidak': 'holm-sidak',
            }.items()],
            value='bonferroni',
        ), style={'width': '15%', 'display': 'inline-block'}),

        html.Div(id='shapiro-output'),
        html.Div(id='kruskal-wallis-output'),

        html.H5(id='post-hoc-header',
                children='Kruskal Wallis Post-Hoc Dunn Test using bonferroni for adjusting p values'),

        html.Div(dash_table.DataTable(
            id='posthoc-output',
            columns=[{"name": i, "id": i} for i in posthoc_result.columns],
            data=posthoc_result_dict,
            tooltip_delay=0,
            tooltip_duration=None,
            style_data_conditional=(
                    [
                        {
                            'if': {
                                'filter_query': '{{{}}} < 0.05'.format(col),
                                'column_id': col
                            },
                            'backgroundColor': '#67a9f0',  # 0074D9 für dunkleres blau
                            'color': 'white'

                        } for col in posthoc_result.columns
                    ] +
                    [
                        {
                            'if': {
                                'filter_query': '{{{}}} < 0.01'.format(col),
                                'column_id': col
                            },
                            'backgroundColor': '#0074D9',  # 0074D9 für dunkleres blau
                            'color': 'white'

                        } for col in posthoc_result.columns
                    ] +
                    [
                        {
                            'if': {
                                'filter_query': '{{{}}} < 0.001'.format(col),
                                'column_id': col
                            },
                            'backgroundColor': '#004187',  # 0074D9 für dunkleres blau
                            'color': 'white'

                        } for col in posthoc_result.columns
                    ]

            )


        ), style={'width': '100%', 'display': 'inline-block'}),



    ], className="six columns"),

])


@app.callback(
    dash.dependencies.Output('box-plot', 'figure'),
    [dash.dependencies.Input('genre-checklist-group', 'value'),
     dash.dependencies.Input('selected_countries', 'value'),
     dash.dependencies.Input('selected_range', 'value'),
     dash.dependencies.Input('box-x-value-dropdown', 'value'),
     dash.dependencies.Input('box-y-value-dropdown', 'value')])
def update_box_chart(genre, selected_countries, selected_range, boxplot_x_value, boxplot_y_value):
    return px.box(data.get_data(genre, selected_countries, selected_range), x=boxplot_x_value, y=boxplot_y_value,
                  points="outliers", notched=False, color=boxplot_x_value,
                  )


@app.callback(
    dash.dependencies.Output(component_id='shapiro-output', component_property='children'),
    [dash.dependencies.Input('genre-checklist-group', 'value'),
     dash.dependencies.Input('selected_countries', 'value'),
     dash.dependencies.Input('selected_range', 'value'),
     dash.dependencies.Input('statistical-1-value-dropdown', 'value')])
def calculate_shapiro(genre, selected_countries, selected_range, statistical_1_value):
    helper_df = data.get_data(genre, selected_countries, selected_range)
    return str(ss.shapiro(helper_df[statistical_1_value]))


@app.callback(
    dash.dependencies.Output(component_id='kruskal-wallis-output', component_property='children'),
    [dash.dependencies.Input('genre-checklist-group', 'value'),
     dash.dependencies.Input('selected_countries', 'value'),
     dash.dependencies.Input('selected_range', 'value'),
     dash.dependencies.Input('statistical-1-value-dropdown', 'value'),
     dash.dependencies.Input('statistical-2-value-dropdown', 'value')])
def calculate_kruskal(genre, selected_countries, selected_range, statistical_1_value, statistical_2_value):
    helper_df = data.get_data(genre, selected_countries, selected_range)
    kruskal_data = [helper_df.loc[ids, statistical_1_value].values for ids in helper_df.groupby(statistical_2_value).groups.values()]
    return str(ss.kruskal(*kruskal_data))


@app.callback(
    dash.dependencies.Output('posthoc-output', 'data'),
    dash.dependencies.Output('posthoc-output', 'columns'),
    dash.dependencies.Output('posthoc-output', 'tooltip_data'),
    [dash.dependencies.Input('genre-checklist-group', 'value'),
     dash.dependencies.Input('selected_countries', 'value'),
     dash.dependencies.Input('selected_range', 'value'),
     dash.dependencies.Input('statistical-1-value-dropdown', 'value'),
     dash.dependencies.Input('statistical-2-value-dropdown', 'value'),
     dash.dependencies.Input('posthoc-type-dropdown', 'value'),
     dash.dependencies.Input('statistical-adjustment-dropdown', 'value'),
     ])
def calculate_posthoc(genre, selected_countries, selected_range, statistical_1_value, statistical_2_value, posthoctype, adjustment):

    global posthoc_result
    global cols
    global posthoc_result_dict

    helper_df = data.get_data(genre, selected_countries, selected_range)
    posthoc_result = sp.posthoc_dunn(helper_df, val_col=statistical_1_value, group_col=statistical_2_value, p_adjust=adjustment)
    if posthoctype == "dunn":
        posthoc_result = sp.posthoc_dunn(helper_df, val_col=statistical_1_value, group_col=statistical_2_value, p_adjust=adjustment)
    if posthoctype == "conover":
        posthoc_result = sp.posthoc_conover(helper_df, val_col=statistical_1_value, group_col=statistical_2_value, p_adjust=adjustment)
    if posthoctype == "mann-whitney":
        posthoc_result = sp.posthoc_mannwhitney(helper_df, val_col=statistical_1_value, group_col=statistical_2_value, p_adjust=adjustment)
    posthoc_result = posthoc_result.round(5)
    posthoc_result['Country'] = posthoc_result.index
    cols = posthoc_result.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    posthoc_result = posthoc_result[cols]
    columns_result = [{"name": i, "id": i} for i in posthoc_result.columns]
    posthoc_result_dict = posthoc_result.to_dict('records')
    ranked_dataframe = data.get_ranked_dataframe(statistical_2_value, statistical_1_value)
    tooltip_data = [
                {
                    column_id: {'value': str(next(iter(row.values()))) #left country
                                         + " with mean rank: "
                                         + str(data.get_mean_rank(ranked_dataframe, statistical_1_value, str(next(iter(row.values())))))
                                         + " vs "
                                         + str(column_id) # upper contry
                                         + " with mean rank: "
                                         + str(data.get_mean_rank(ranked_dataframe, statistical_1_value, str(column_id)))
                                         + ". Total N = "
                                         + str(helper_df.shape[0])
                                         ,
                                'type': 'markdown'}
                    for column_id, row_id in row.items()
                } for row in posthoc_result_dict
            ]
    return posthoc_result_dict, columns_result, tooltip_data


@app.callback(
    dash.dependencies.Output('post-hoc-header', 'children'),
    dash.dependencies.Input('posthoc-type-dropdown', 'value'),
    dash.dependencies.Input('statistical-adjustment-dropdown', 'value')
)
def set_posthoc_header(posthoctype, adjustment):
    return 'Kruskal Wallis Post-Hoc ' + posthoctype.title() + '-Test using ' + adjustment.title() + ' for adjusting p values'



# Run the application.
# You can run this application simply by using the command "python app.py" to run this Service directly on your machine
# or you can use "docker-compose up -d" to create a docker container running this application.
if __name__ == '__main__':
    # Check whether the right right amount of docker arguments is provided.
    # The standard ones are provided in the Dockerfile.
    if len(sys.argv) == 3:
        # Retrieve the host and port arguments provided in the dockerfile.
        host = str(sys.argv.__getitem__(1))
        port = int(sys.argv.__getitem__(2))
        app.run_server(host=host, port=port, debug=True)
    else:
        app.run_server(debug=True)
