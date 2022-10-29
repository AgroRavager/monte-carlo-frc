import pandas as pd
import random

def filter_measures(measures, last_match = None):
    measures = measures[measures.match.str[2:].astype(int)<=int(last_match[2:])].copy()
    return measures

def filter_matches(matches, first_match = None, last_match = None):
    if first_match is not None:
        matches = matches[matches['match'].str[2:].astype(int)>=int(first_match[2:])]
    if last_match is not None: 
        matches = matches[matches.match.str[2:].astype(int)<=int(last_match[2:])].copy()
    return matches

def get_taxi_sums(measures):
    booldict = {'true':True, 'false':False}
    taxi = (
        measures[measures.task=='taxi']
        .copy()
        .assign(measure1 = lambda df: df.measure1.map(booldict))
        .groupby("team_number")
        .agg({"measure1": 'sum'})
        .assign(taxi = lambda df: df.measure1)
        .drop(columns = "measure1"))
    return taxi

def get_counts(measures):
    counts = pd.DataFrame(
        measures[(measures['measure_type']=='count')
        &(measures['task'].isin(['upper','lower','penalty_count']))]
        .copy()
        .assign(means=lambda df: df.measure1.astype('int'))
        .groupby(['team_number','phase','task'])
        .agg({'means':'sum'})
        .reset_index(level=[1,2])
        .assign(task=lambda df: df.phase+'_'+df.task)
        .drop(columns='phase')
        .pivot(columns='task',values='means'))
    return counts

def get_hangar_totals(measures):
    hangar_totals = (pd.get_dummies(measures[measures['task']=='hangar_level_end'].measure1)
                        .join(measures['team_number'])
                        .groupby(by=['team_number'])
                        .sum()
                        .rename(columns={'0':'probability_0','1':'probability_1', '2':'probability_2', '3': 'probability_3', '4': 'probability_4'}))
    return hangar_totals

def get_averages(taxi, counts, hangar_totals, matches):
    measure_means = (counts.join(taxi)
                     .join(hangar_totals)
                     .assign(matches_played=matches.groupby('team_number').count().match))
    measure_means.iloc[:,:-1]=measure_means.iloc[:,:-1].div(measure_means.matches_played,axis=0)
    measure_means = measure_means.drop(columns='matches_played')
    return measure_means

def get_matches(team_averages_df, matches):
    #The commented out line executed correctly, but I'm not sure how to sort one column by a function 
    #and another naturally
    matches=(matches.set_index('team_number', drop=True)
               .drop(columns=['match_time'])
               .join(team_averages_df)
               .assign(match=lambda df: df.match.str[2:].astype(int))
               .sort_values(by=['match','alliance', 'station'])
               .assign(match=lambda df: 'qm'+df.match.astype(str))
    #            .sort_values(by=['match'], key=lambda col: col.str[2:].astype(int))
                )
    return matches

def taxi(percentage):
        num = random.randint(1,100)
        if percentage*100>=num:
            return 1
        else:
            return 0