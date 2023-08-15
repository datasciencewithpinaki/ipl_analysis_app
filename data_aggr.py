import pandas as pd
import numpy as np
import re

import matplotlib.pyplot as plt


class CollectData:
    
    path_dir = '/Users/pinaki/Downloads/ML_datasets/IPL Player Stats/Batting Stats/'
    file_partial = 'BATTING STATS - IPL_'  # BATTING STATS - IPL_2022.csv
    YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022]
    
    def get_data():
        files = [f"{CollectData.file_partial}{year}.csv" for year in CollectData.YEARS]
        df_all = pd.DataFrame()
        for idx, year in enumerate(CollectData.YEARS):
            onefile = f"{CollectData.file_partial}{year}.csv"
            df_one = pd.read_csv(CollectData.path_dir + onefile)
            df_one['Year'] = year
            print(f"Data read complete for file {idx}")
            df_all = pd.concat([df_all, df_one])
        df_all.reset_index(inplace=True)
        df_all = CollectData.clean_data(df_all)
        return df_all
    
    def clean_data(df_raw):
        print(f'cleaning data')
        df = df_raw.copy()
        # HS has *; organize those
        df = CollectData.clean_HS(df)
        # Avg has '-'; Remove those
        df = CollectData.clean_Avg(df)
        return df
    
    def clean_HS(df_raw):
        print('formatting HS column')
        df = df_raw.copy()
        df['HS list'] = df['HS'].apply(lambda x: str(x).split('*'))
        df['HS clean'] = df['HS list'].apply(lambda x: int(x[0]))
        df['remained NO during HS'] = df['HS list'].apply(lambda x: '*' if len(x)>1 else '')
        df.drop(['HS', 'HS list'], axis=1, inplace=True)
        df.rename(columns={'HS clean': 'HS'}, inplace=True)
        return df
    
    def clean_Avg(df_raw):
        print('formatting Avg column')
        df = df_raw.copy()
        df['Avg'] = df['Avg'].apply(lambda x: float(x) if x!='-' else np.nan)
        return df


class BattingStats:
    
    EXCLD_METRICS_FOR_SUMMATION = ['POS', 'HS', 'Avg', 'SR', 'Year']
    
    def get_current_year(df)->int:
        return int(df['Year'].max())
    
    def subset_data_for_year(df, year:int=None)->pd.DataFrame:
        year = BattingStats.get_current_year(df) if not year else year
        filt_year = (df['Year']==year)
        df_subset = df.loc[(filt_year),:]
        return df_subset
    
    def agg_for_player(df, metric:str='Runs', method:str='sum')->pd.DataFrame:
        df_subset_for_year = BattingStats.subset_data_for_year(df)
        player_agg = df_subset_for_year\
                .groupby(['Player'], as_index=False)\
                .agg({metric: method}).sort_values([metric], ascending=False)\
                .reset_index(drop=True)
        return player_agg
    
    def top_batters(df, top_N:int=1, metric:str='Runs', method:str='sum')->list:
        player_agg = BattingStats.agg_for_player(df, metric, method)
        top_players = player_agg.loc[0:top_N, 'Player'].to_list()
        return top_players
    
    def agg_metric(df, metric:str='Runs', method:str='sum'):
        tot_runs = df.agg({metric: method})[0]
        return tot_runs
    
    def total_capped_players(df)->int:
        cnt_capped_players = len(set(df['Player']))
        return cnt_capped_players
        
    def agg_metrics(df, metrics:list): 
        dict_agg_metrics = {f"Total {metric}": df[metric].sum() for metric in metrics if metric not in BattingStats.EXCLD_METRICS_FOR_SUMMATION}
        if 'HS' in metrics:  # Get highest individual score in an innings
            dict_agg_metrics['Highest Individual Score'] = df['HS'].max()
        if 'SR' in metrics:
            dict_agg_metrics['Highest Strike Rate'] = df['SR'].max()
        return dict_agg_metrics
        
    def get_rank(df_raw, metric:str='Runs'):
        df = df_raw.copy()
        df['Rank'] = df.groupby(['Year'])[metric].rank('dense', ascending=False)
        return df
    
    def get_top_batters_as_df(df, top_N:int=1):
        top_batters = BattingStats.top_batters(df, top_N)
        dict_top_batters = {idx+1: bat for idx, bat in enumerate(top_batters)}
        return dict_top_batters
        
        
class BatsmanStats:
    
    def filter_batsman(df, batsman:str|list):
        if type(batsman)==str:
            filt_bat = (df['Player']==batsman)
        elif type(batsman)==list:
            filt_bat = (df['Player'].isin(batsman))
        df_subset = df.loc[filt_bat,:]
        if df_subset.shape[0]==0:
            raise ValueError
        return df_subset
    
    def select_columns(df, columns:list):
        columns = [col for col in columns if col in df.columns]
        if len(columns)==0:
            raise KeyError
        df_subset = df[columns]
        return df_subset
    
    def batsman_agg(df, batsman:str, metrics:list):
        df_subset = BatsmanStats.filter_batsman(df, batsman)        
        dict_metric_method = {metric:'sum' for metric in metrics}
        exception_metrics = list(set(metrics).intersection(set(BattingStats.EXCLD_METRICS_FOR_SUMMATION)))
        for metric in exception_metrics:
            dict_metric_method[metric] = 'max'
        df_batsman_agg_metrics = df_subset.groupby(['Player'], as_index=False).agg(dict_metric_method)
        if 'Avg' in metrics:
            df_batsman_agg_metrics['Avg'] = round(df_batsman_agg_metrics['Runs'] / (df_batsman_agg_metrics['Inns'] - df_batsman_agg_metrics['NO']),2)
        if 'SR' in metrics:
            df_batsman_agg_metrics['SR'] = round((df_batsman_agg_metrics['Runs'] / df_batsman_agg_metrics['BF'])*100, 2)
        return df_batsman_agg_metrics
    
    def bar_plot(df, batsman:str, metric:str='Runs')->plt:
        df_subset = BatsmanStats.filter_batsman(df, batsman)
        df_agg = df_subset.groupby(['Year'], as_index=False)[metric].sum()
        plt.figure(figsize=(4,3))
        plt.bar('Year', metric, data=df_agg, color='green')
        if len(batsman)>1:
            plt.title(f"{metric} scored by {batsman[0]} + others by Year")    
        else:
            plt.title(f"{metric} scored by {batsman[0]} by Year")
        plt.show();
        
    def search_batsman(df, search_str:str)->list:
        players = set(df['Player'])
        batsman_list = [player for player in players if re.findall(search_str.lower(), player.lower())]
        if len(batsman_list)==0:
            raise NameError
        return sorted(batsman_list)
    
    def current_best_rank(df_raw, batsman:str, metric:str='Runs')->int:
        df_w_rank = BattingStats.get_rank(df_raw, metric)
        df_subset = BatsmanStats.filter_batsman(df_w_rank, batsman)
        df_this_year = BattingStats.subset_data_for_year(df_subset)
        curr_rank = df_this_year['Rank'].iloc[0]
        best_rank = df_subset['Rank'].min()
        year_w_best_rank = df_subset.loc[(df_subset['Rank']==best_rank), 'Year'].iloc[0]
        return curr_rank, best_rank, year_w_best_rank
    
    
