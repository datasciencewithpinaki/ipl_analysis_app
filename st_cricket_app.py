import streamlit as st
import pandas as pd
import numpy as np
import re
import altair as alt

from data_aggr import CollectData, BattingStats, BatsmanStats

st.set_page_config('IPL Analysis', page_icon=":fish:")

st.title('IPL | Cricket Analysis')
st.subheader('[2017-2022]')

@st.cache_data
def read_data():
    df = CollectData.get_data()
    return df

def agg_data_for_plot(df, batsman:str, metric:str='Runs'):
    df_subset = BatsmanStats.filter_batsman(df, batsman)
    metrics_all = ['Runs', 'Inns', 'NO', 'BF', 'Avg', 'SR']
    df_agg = df_subset.groupby(['Year'], as_index=False)[metrics_all].sum()
    return df_agg

tab_bat, tab_bowl = st.tabs(['Batting', 'Bowling'])

with tab_bat:
    df = read_data()

    top_container = st.container()
    bottom_container = st.container()

    ## top container
    with top_container:
        st.markdown("*IPL till now*")
        col1, col2, col3 = st.columns(3)
        df_top_batters = BattingStats.get_top_batters_as_df(df, 3)
        col1.info('Top Batters', icon="🤖")
        col1.dataframe(df_top_batters)
        
        total_runs = BattingStats.agg_metric(df, 'Runs', 'sum')
        cnt_capped_players = BattingStats.total_capped_players(df)
        col2.info('Overall Figures', icon="☢")
        col2.metric('Total Runs scored', f"{total_runs:,}")
        col2.metric('Total Capped Players', cnt_capped_players)
        
        METRICS = ['6s', '100', '50', 'HS']
        dict_overall_stats = BattingStats.agg_metrics(df, METRICS)
        col3.info('Records', icon="🚨")
        col3.dataframe(dict_overall_stats, )
        
    ## sidebar
    with st.sidebar.form('Sidebar Player Select'):
        st.markdown('## User Choices')
        player_search = st.text_input('Search a player', placeholder='Search player name', max_chars=30, label_visibility='collapsed')
        try:
            players = BatsmanStats.search_batsman(df, player_search)
        except NameError as e:
            players = BatsmanStats.search_batsman(df, 'kohli')
            st.write('Showing default results as no player found')
        status_player = True if len(players)>0 else False
        if status_player:
            player = st.selectbox('Select a Player', players, placeholder='Select Player', label_visibility='collapsed', disabled=False)
            if player:
                st.success(f'Chosen player is {player}')
            elif not player:
                st.warning(f'Choose player to see statistics')

        METRICS_BOTTOM_CONTAINER = ['Inns', 'NO', 'Runs', 'Avg', 'BF', 'SR', '100', '50', '6s', '4s']
        metric = st.selectbox('Select Metric', METRICS_BOTTOM_CONTAINER, index=2)
        color_chart = st.color_picker('Pick color for chart', "#00FF00")
        btn_submit = st.form_submit_button('Submit')
        if btn_submit:
            st.success(f'Chosen metric is {metric}')

    ## bottom container
    with bottom_container:
        st.markdown("---")
        if not btn_submit:
            st.warning('Choose a player to see their statistics')
        if btn_submit:
            st.markdown(f'Statistics for _{player}_')
            df_oneplayer = BatsmanStats.batsman_agg(df, player, METRICS_BOTTOM_CONTAINER)
            st.dataframe(df_oneplayer)
            st.markdown('---')
            st.markdown(f'Plots based on **{metric}** for _{player}_')
            df_for_plot = agg_data_for_plot(df, player, metric)
            st.bar_chart(df_for_plot, x='Year', y=metric)
            
with tab_bowl:
    st.markdown('This section has not been implemented yet')