import pandas as pd
import geopandas as gpd


pd.set_option('display.max_columns', None)


def check(row):
    return (row.filter(regex="^rp_code_")!=row.filter(regex="^sp.*adj$").min()).all()

def filter_edf(edf):
    # Update vehicle ownership to re-code "other" to "large car" and "other powertrain" to "ICE"
    # Also, add a new column with the SP code for each vehicle
    df = pd.DataFrame(data={"veh_type" : [1,2,3,1,2,3,1,2,3,1,2,3], "veh_pt" : [1,1,1,2,2,2,3,3,3,4,4,4], 
                    "rp_code" : [1,3,5,2,4,6,2,4,6,2,4,6]})

    for i in range(1,7):
        edf.loc[edf["veh_pt_{0}".format(i)]==5,"veh_pt_{0}".format(i)] = 1
        edf.loc[edf["veh_type_{0}".format(i)]==4,"veh_type_{0}".format(i)] = 2
        edf = edf.merge(df, how="left", left_on=["veh_type_{0}".format(i),"veh_pt_{0}".format(i)], right_on=["veh_type","veh_pt"], suffixes=[None,"_{0}".format(i)])
    edf.rename(columns={"rp_code": "rp_code_1"}, inplace=True)

    edf.veh_type_1.head(25)
    # Check condition that min SP response = max SP response - i.e., that all responses are the same
    colmin = edf.loc[:,edf.filter(regex="^sp.*adj$").columns].min(axis=1)
    colmax = edf.loc[:,edf.filter(regex="^sp.*adj$").columns].max(axis=1)
    cond1 = (colmin==colmax)
    # Check that none of the current HH vehicles are the same as the min SP choice, conditional on only one SP choice


    cond2 = edf.apply(check, axis=1)

    return edf[~(cond1*cond2)]

edf = pd.read_csv("../data/ev_survey_data.csv")
# filter out records where the respondent gave the same answer to all SP experiments AND they also don't own that vehicle type
# print("edf rows before filter:", edf.shape[0])

filt_edf = filter_edf(edf)
# print("edf rows after filter:", filt_edf.shape[0])

geo_edf = gpd.GeoDataFrame(filt_edf, 
    geometry = gpd.points_from_xy(filt_edf['longitude'], filt_edf['latitude']), 
    crs = 'EPSG:3857')

ctydf = gpd.read_file("../data/county_shp/county_L48_only.shp")
# ctydf = ctydf.to_crs(3857)
# filter states to include only survey region
survey_states = ["19","20","27","29","31","38","46"]
ctydf = ctydf.loc[ctydf.STATEFP.isin(survey_states)]


# standard data frame for all plots
hh_size_dict = {
    16.0: "1",
    17.0: "2",
    18.0: "3",
    19.0: "4",
    20.0: "5",
    21.0: "6 or more"
}

next_veh_dict = {
    1: "Small car",
    2: "Large car",
    3: "Pickup truck",
    4: "Other vehicles"
}


occupation_dict = {
    1.0: "Management, professional, and related",
    2.0: "Service",
    3.0: "Sales and office",
    4.0: "Farming, fishing, and forestry",
    5.0: "Construction, extraction, and maintenance",
    6.0: "Production, transportation, and material moving",
    7.0: "Government",
    8.0: "Retired",
    9.0: "Unemployed"
}


off_road_freq_dict = {
    1.0: "Rarely \n (1-3 times per year)",
    2.0: "Sometimes \n (1-3 times per month)",
    3.0: "Seasonally \n (1 or more times per week \n for one season)",
    4.0: "Frequently \n (1 or more times per week \n throughout the year)"
}


parking_dict = {
    "bev_dwell_1": "Private enclosed garage",
    "bev_dwell_2": "Private non-enclosed garage",
    "bev_dwell_3": "Dedicated parking in shared facility (accommodate)",
    "bev_dwell_4": "Dedicated parking in shared facility (not accommodate)",
    "bev_dwell_5": "Street parking (accommodate)",
    "bev_dwell_6": "Street parking (not accommodate)",
    "bev_dwell_7": "No dedicated parking facility"
}

sp_dict = {1: "Small ICE", 2: "Small BEV", 3: "Large ICE", 4: "Large BEV", 5:"Pickup truck ICE", 6: "Pickup truck BEV"}



geo_edf.loc[:, 'hh_size'] = geo_edf['hh_size'].map(hh_size_dict)
geo_edf.loc[:, 'next_veh_type_1'] = geo_edf['next_veh_type_1'].map(next_veh_dict)
geo_edf.loc[:, 'occupation'] = geo_edf['occupation'].map(occupation_dict)
geo_edf.loc[:, 'off_road_freq'] = geo_edf['off_road_freq'].map(off_road_freq_dict)

# keys are current column names values are new column names
geo_edf.rename(columns=parking_dict, inplace=True)


cols = ['survey_duration', 'person_age', 'survey_state_code', 'state_name',
       'county_name', 'geoid', 'county_IA', 'county_KS', 'county_MN',
       'county_MO', 'county_NE', 'county_ND', 'county_SD',
       'definition_check', 'hh_veh_own', 'veh_pt_1', 'veh_pt_2',
       'veh_pt_3', 'veh_pt_4', 'veh_pt_5', 'veh_pt_6', 'veh_type_1',
       'veh_type_2', 'veh_type_3', 'veh_type_4', 'veh_type_5',
       'veh_type_6', 'veh_make_1', 'veh_make_2', 'veh_make_3',
       'veh_make_4', 'veh_make_5', 'veh_make_6', 'veh_year_1',
       'veh_year_2', 'veh_year_3', 'veh_year_4', 'veh_year_5',
       'veh_year_6', 'next_veh', 'next_veh_new', 'next_veh_pt_1',
       'next_veh_pt_2', 'next_veh_pt_3', 'next_veh_pt_4', 'next_veh_pt_5',
       'next_veh_pt_6', 'next_veh_type_1', 'next_veh_type_2',
       'next_veh_type_3', 'next_veh_type_4', 'next_veh_type_5',
       'next_veh_type_6', 'veh_tow', 'veh_off_road', 'tow_freq',
       'off_road_freq', 'ctrip_min', 'ctrip_mode', 'nc_min', 'trip_purp',
       'trip_mode', 'ld_trip_freq', 'ld_75_nb_mode', 'ld_b_75_mode',
       'ld_500_nb_mode', 'ld_b_500_mode', 'ld_rental',
       'pub_transit_veh_own', 'bev_concern', 'bev_concern_1',
       'bev_concern_2', 'bev_concern_3', 'bev_concern_7', 'bev_concern_6',
       'bev_concern_0', 'bev_factor', 'bev_factor_1', 'bev_factor_2',
       'bev_factor_3', 'bev_factor_4', 'bev_factor_5', 'bev_factor_6',
       'bev_factor_7',
       'Which of the following statements most closely reflects the potential for electric vehicle charging at your primary residence? - Selected Choice',
       'bev_dwell_1', 'bev_dwell_2', 'bev_dwell_3', 'bev_dwell_4',
       'bev_dwell_5', 'bev_dwell_6', 'bev_dwell_7', 'env_import',
       'air_rank', 'water_rank', 'soil_rank', 'xweather_rank',
       'biodiversity_rank', 'deforest_rank', 'plastic_rank', 'educ_rank',
       'health_rank', 'climate_rank', 'immigrate_rank', 'race_rank',
       'econ_rank', 'poverty_rank', 'gun_rank', 'poli_rank', 'crime_rank',
       'sp1', 'sp2', 'sp3', 'sp4', 'sp5', 'sp6', 'sp_set1', 'sp_set2',
       'sp_set3', 'sp_set4', 'sp_set5', 'sp_set6', 'spe1', 'spe3',
       'spe14', 'spe19', 'spe22', 'spe23', 'spe6', 'spe7', 'spe12',
       'spe16', 'spe20', 'spe24', 'spe4', 'spe5', 'spe8', 'spe10',
       'spe11', 'spe21', 'spe2', 'spe20.1', 'spe13', 'spe15', 'spe17',
       'spe18', 'gender', 'race', 'marital_status', 'license',
       'emp_status', 'occupation', 'educ', 'zipcode', 'latitude',
       'longitude', 'dwell_type', 'dwell_tenure', 'hh_size', 'hh_arrange',
       'hh_license', 'hh_ftw', 'hh_ptw', 'hh_students', 'hh_child',
       'hh_65plus', 'hh_income', 'CUID', 'person_weight', 'hh_weight',
       'comb_weight', 'veh_type', 'veh_pt', 'rp_code_1', 'veh_type_2',
       'veh_pt_2', 'rp_code_2', 'veh_type_3', 'veh_pt_3', 'rp_code_3',
       'veh_type_4', 'veh_pt_4', 'rp_code_4', 'veh_type_5', 'veh_pt_5',
       'rp_code_5', 'veh_type_6', 'veh_pt_6', 'rp_code_6', 'geometry']

questions_dict = {
    "person_age": "person_age",
    "survey_state_loc_details": {
        "survey_state_code": "survey_state_code",
        "state_name": "state_name",
        "county_name": "county_name",
        "geoid": "geoid",
        "county": ["county_IA", "county_KS", "county_MN", "county_MO", "county_NE", "county_ND", "county_SD"],
    },
    "definition_check": "definition_check",
    "curr_veh": {
        "curr_veh": "hh_veh_own", #does the household own a vehicle
        "curr_veh_det": {
            "veh_pt": ["veh_pt_1", "veh_pt_2", "veh_pt_3", "veh_pt_4", "veh_pt_5", "veh_pt_6"],
            "veh_type": ["veh_type_1", "veh_type_2", "veh_type_3", "veh_type_4", "veh_type_5", "veh_type_6"],
            "veh_make": ["veh_make_1", "veh_make_2", "veh_make_3", "veh_make_4", "veh_make_5", "veh_make_6"],
            "veh_year": ["veh_year_1", "veh_year_2", "veh_year_3", "veh_year_4", "veh_year_5", "veh_year_6"]
        },
    },
    "next_veh": {
        "next_veh_purchase_time": "next_veh", # when to get next vehicle
        "next_veh_new": "next_veh_new", # is it new/used/unsure
        "next_veh_det": {
            "veh_pt": ["next_veh_pt_1", "next_veh_pt_2", "next_veh_pt_3", "next_veh_pt_4", "next_veh_pt_5", "next_veh_pt_6"],
            "veh_type": ["next_veh_type_1", "next_veh_type_2", "next_veh_type_3", "next_veh_type_4", "next_veh_type_5", "next_veh_type_6"]
        },
    },
    "towing": {
        "veh_tow": "veh_tow", # tow other vehicle
        "tow_freq": "tow_freq", # how often tow other vehicle
    },
    "off_road": {
        "veh_off_road": "veh_off_road", # off road driving
        "off_road_freq": "off_road_freq", # how often off road driving
        "commute": {
            "ctrip_min": "ctrip_min", # commute trip minutes
            "ctrip_mode": "ctrip_mode", # commute trip mode
        },
    },
    "n-commute": {
        "nc_min": "nc_min", # non-commute trip minutes
        "trip_purp": "trip_purp", # non-commute trip purpose
        "trip_mode": "trip_mode" # non-commute trip mode
    },
    "long_drive": {
        "ld_trip_freq": "ld_trip_freq", # long distance trip frequency
        "ld_trip_mode": {
            "ld_75_nb_mode": "ld_75_nb_mode", # long distance trip mode for trips less than 75 miles
            "ld_b_75_mode": "ld_b_75_mode", # long distance trip mode for trips greater than 75 miles
            "ld_500_nb_mode": "ld_500_nb_mode", # long distance trip mode for trips less than 500 miles
            "ld_b_500_mode": "ld_b_500_mode" # long distance trip mode for trips greater than 500 miles
        },
        "ld_rental": "ld_rental" # long distance trip rental
    },
    "public_transit": "pub_transit_veh_own", # public transit usage if own vehicle
    "bev_concern": {
        "bev_concern": ["bev_concern_1", "bev_concern_2", "bev_concern_3", "bev_concern_7", "bev_concern_6", "bev_concern_0"], # concern about Battery electric vehicles
        "bev_factor": ["bev_factor_1", "bev_factor_2", "bev_factor_3", "bev_factor_4", "bev_factor_5", "bev_factor_6", "bev_factor_7"], # factor influencing bev purchase
        "bev_dwell": ["bev_dwell_1", "bev_dwell_2", "bev_dwell_3", "bev_dwell_4", "bev_dwell_5", "bev_dwell_6", "bev_dwell_7"] # dwelling type
    },
    "env_import": "env_import", # environmental import
    "env_rank": ["air_rank", "water_rank", "soil_rank", "xweather_rank", "biodiversity_rank", "deforest_rank", "plastic_rank"], # environmental rank
    "issue_rank": ['educ_rank', 'health_rank', 'climate_rank', 'immigrate_rank','race_rank','econ_rank', 'poverty_rank', 'gun_rank', 'poli_rank', 'crime_rank',], # issue rank
    'sp': ['sp1', 'sp2', 'sp3', 'sp4', 'sp5', 'sp6'], # stated preference
    'sp_set': ['sp_set1', 'sp_set2', 'sp_set3', 'sp_set4', 'sp_set5', 'sp_set6'], # stated preference set
    'spe': ['spe1', 'spe3', 'spe14', 'spe19', 'spe22', 'spe23', 'spe6', 'spe7', 'spe12', 'spe16', 'spe20', 'spe24', 'spe4', 'spe5', 'spe8', 'spe10', 'spe11', 'spe21', 'spe2', 'spe20.1', 'spe13', 'spe15', 'spe17', 'spe18'], # stated preference experiment
    'personal_details': ['gender', 'race', 'marital_status', 'license', 'emp_status', 'occupation', 'educ', 'zipcode','latitude', 'longitude',],
    'household_details': ['dwell_type', 'dwell_tenure', 'hh_size', 'hh_arrange'],
    'hh_people_details': {
        'hh_license': 'hh_license', # num people in household with license
        'hh_ftw': 'hh_ftw', # num people in household with full time work
        'hh_ptw': 'hh_ptw', # num people in household with part time work
        'hh_students': 'hh_students', # num people in household who are students
        'hh_child': 'hh_child', # num people in household who are children
        'hh_65plus': 'hh_65plus', # num people in household who are 65+
        'hh_income': 'hh_income', # household income
    },
    'additional_info': {
        'weights': {
            'person_weight': 'person_weight', # person weight
            'hh_weight': 'hh_weight', # household weight
            'comb_weight': 'comb_weight', # combined weight
        },
        'veh_type': 'veh_type', # vehicle type
        'veh_pt': 'veh_pt', # vehicle powertrain
        'rp_code': ['rp_code_1', 'rp_code_2', 'rp_code_3', 'rp_code_4', 'rp_code_5', 'rp_code_6'], # stated preference code
        'geometry': 'geometry' # geometry
    }
}

def get_geo_edf():
    '''
    It returns the csv data with correct code applied to corresponding values
    '''
    return geo_edf


def get_raw_data():
    '''
    Returns the data from csv without converting it to corresponding values
    '''
    edf = pd.read_csv("../data/ev_survey_data.csv")
    # filter out records where the respondent gave the same answer to all SP experiments AND they also don't own that vehicle type
    # print("edf rows before filter:", edf.shape[0])

    filt_edf = filter_edf(edf)
    # print("edf rows after filter:", filt_edf.shape[0])

    geo_edf = gpd.GeoDataFrame(filt_edf, 
        geometry = gpd.points_from_xy(filt_edf['longitude'], filt_edf['latitude']), 
        crs = 'EPSG:3857')
    
    return geo_edf


# add getters for all dictionaries
def get_hh_size_dict():
    return hh_size_dict

def get_next_veh_dict():
    return next_veh_dict

def get_occupation_dict():
    return occupation_dict

def get_off_road_freq_dict():
    return off_road_freq_dict

def get_parking_dict():
    '''
    It returns the dictionary for parking location available to a person
    '''
    return parking_dict

def get_questions_dict():
    '''
    This is my personal `reference` for dataset
    '''
    return questions_dict


def get_sp_dict():
    '''
    It returns the dictionary for stated preference
    '''
    return sp_dict