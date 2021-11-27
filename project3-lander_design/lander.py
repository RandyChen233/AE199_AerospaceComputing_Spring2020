# -*- coding: utf-8 -*-
"""
Functions for lander design.


"""

# YOUR IMPORT HERE


# YOUR CODE HERE
def drag(density, velocity, area, cd):
    """A function to estimate the drag force of a body.

    Parameters
    ----------
    density : float
        Free stream air density [kg/m^3].

    velocity : float
        Free stream velocity [m/s].

    area : float
        Wetted surface area [m^2].
        
    cd : float
        Drag coefficient for the body.

    Returns
    -------
    drag_force : float
        Drag force [N].

    """
    return 1/2 * cd * density *area * velocity**2


def weight(mass, gravitational_acceleration):
    """A function to estimate the weight of a body.

    Parameters
    ----------
    mass : float
        Body mass [kg].

    gravitational_acceleration : float
        Gravitational acceleration [m/s^2].

    Returns
    -------
    weight_force : float
        Weight force [N].

    """
    return mass * gravitational_acceleration

import pandas as pd
def thrust(time, efficiency, thruster_filepath):
    """A function to estimate the thrust from a thruster for a given time since ignition.
    
    Thrust is linearly interpolated between data points.

    Parameters
    ----------
    time : float
        Time since ignition [s].
        
    efficiency : float
        Fraction to thrust force actually produced after accounting for efficiency losses [N]. 0 <= efficiency <= 1.
    
    thruster_filepath : str
        Path to the thrust curve .csv file.

    Returns
    -------
    thrust_force : float
        Instantaneous thrust force [N]. Assume a linear thrust curve between data points.

    """
    force = 0
    df = pd.read_csv(thruster_filepath)
    df.columns = ['time','thrust']


    if time >=0 and time <= df.time.values[-1]:
        for i in df.time.index:
            if (time-df.time[i]) > 0 and (time-df.time[(i+1)])<0:
                force = (((df.loc[df.time==df.time[i+1]]['thrust'].values-df.loc[df.time==df.time[i]]['thrust'].values)/(df.time[i+1]-df.time[i]) * (time-df.time[i]) +df.loc[df.time==df.time[i]]['thrust'].values ) * efficiency)
            elif time == df.time[i]:
                force = df.loc[df.time==df.time[i]]['thrust'].values * efficiency
    else: 
        force == 0

            
        
    
    return float(force)




import numpy as np


def simulation(params):

    total_mass = params['body_mass']+params['fin_mass']*params['n_fins']
    total_area = np.pi/4 * params['body_diameter']**2 +params['n_fins']*params['fin_width']*params['fin_height'] 
    total_weight = weight(total_mass,params['g'])
    df = pd.DataFrame()
    velocity = params['velocity']
    thrust_force = 0
    drag_force = 0
    t_land = 0
    v_land = 0
    acceleration = params['acceleration']
    position = params['position']
    landed=False
    for i in np.arange(0,params['t_final']+params['t_step'],params['t_step']): 
        position =position+velocity*params['t_step']
        velocity = velocity+acceleration*params['t_step']
        
        
    
        drag_force= drag(params['density'],velocity,total_area,params['fin_cd'])
        
        thrust_force=thrust(i-params['t_ignition'],params['thruster_efficiency'],params['thrust_curve'])
        
        acceleration= (drag_force+thrust_force-total_weight)/total_mass
        
        
        
        
        data= {'acceleration':[acceleration],'velocity':[velocity],'thrust':[thrust_force],'drag':[drag_force],'position':[position],'weight':[total_weight]}
              
       
        data_frame = pd.DataFrame(data)
        df = df.append(data_frame)
        if position <0 and landed==False:
            t_land = i
            v_land = velocity 
            landed=True
    
    
    return df,t_land,v_land


def factorial_22(factors):
    """A function to create a 2^2 factorial experimental design.

    Parameters
    ----------
    factors : dict
        Dictionary where keys are factor names and values are lists of factor levels. Assumes there are two factors (i.e., two keys) and two levels for each factor (i.e., each value list is of length two).

    Returns
    -------
    df_exp : dataframe
        Dataframe of experimental design, with two columns (one for each factor) and one row for each design point in the experiment. Column names correspond to factor names.

    Examples
    --------
    # a 2^2 factorial where:
    # design point 1 is (factor1 = val1, factor2 = val3)
    # design point 2 is (factor1 = val2, factor2 = val4)
    >>> factors = {'factor1': [val1, val2],
                   'factor2': [val3, val4]
                  }
    >>> df = factorial_22(factors)
    >>> df.loc[0].values
    array([val1, val3], dtype=object)
    >>> df.shape()
    (2, 2)

    """
    df = pd.DataFrame()
    
    data_frame = pd.DataFrame(factors)
    df = df.append(data_frame)
    return df

def factorial_MN(factors):
    df = pd.DataFrame()
    for i in factors['thrust_curve']:
        for j in factors['t_ignition']:
            data = {'thrust_curve':[i],'t_ignition':[j]}
            data_frame = pd.DataFrame(data)
            df = df.append(data_frame)
    return df

    
    
def experiment(df_exp, params):
    """A function to run an experiment simulating landing with different parameter values.

    Parameters
    ----------
    df_exp : dataframe
        Dataframe of experimental design, with two columns (one for each factor) and one row for each case in the experiment. Column names correspond to factor names.

    params : dict
        Dictionary of all simulation parameters (default values).

    Returns
    -------
    df_results : dataframe
        Dataframe of experiment results with one column for each factor in df_exp and the following response columns: t_land, v_land.

    """
    
    
    
    
   
    

    landing_time = []
    landing_speed = []
    for index, row in df_exp.iterrows():
        params['thrust_curve'],params['t_ignition']=row['thrust_curve'],row['t_ignition']
        df,t_land,v_land = simulation(params)
        landing_time.append(t_land)
        landing_speed.append(v_land)
    df_exp['T_land'] = landing_time
    df_exp['V_land'] = landing_speed
    
    return df_exp

def factorial_env(factors):
    df = pd.DataFrame()
    for i in factors['body_mass']:
        for j in factors['position']:
            data = {'body_mass':[i],'position':[j]}
            data_frame = pd.DataFrame(data)
            df = df.append(data_frame)
    return df



def experiment_env(df_exp, params):
    """A function to run an experiment simulating landing with different parameter values.

    Parameters
    ----------
    df_exp : dataframe
        Dataframe of experimental design, with two columns (one for each factor) and one row for each case in the experiment. Column names correspond to factor names.

    params : dict
        Dictionary of all simulation parameters (default values).

    Returns
    -------
    df_results : dataframe
        Dataframe of experiment results with one column for each factor in df_exp and the following response columns: t_land, v_land.

    """
    
    
    
    
   
    

    landing_time = []
    landing_speed = []
    for index, row in df_exp.iterrows():
        params['body_mass'],params['position']=row['body_mass'],row['position']
        df,t_land,v_land = simulation(params)
        landing_time.append(t_land)
        landing_speed.append(v_land)
    df_exp['T_land'] = landing_time
    df_exp['V_land'] = landing_speed
    
    return df_exp

def experiment_env2(df_exp, params):
    """A function to run an experiment simulating landing with different parameter values.

    Parameters
    ----------
    df_exp : dataframe
        Dataframe of experimental design, with two columns (one for each factor) and one row for each case in the experiment. Column names correspond to factor names.

    params : dict
        Dictionary of all simulation parameters (default values).

    Returns
    -------
    df_results : dataframe
        Dataframe of experiment results with one column for each factor in df_exp and the following response columns: t_land, v_land.

    """
    
    
    
    
   
    

    landing_time = []
    landing_speed = []
    for index, row in df_exp.iterrows():
        params['g'],params['density']=row['g'],row['density']
        df,t_land,v_land = simulation(params)
        landing_time.append(t_land)
        landing_speed.append(v_land)
    df_exp['T_land'] = landing_time
    df_exp['V_land'] = landing_speed


    
def pivot_df(df, idx, cols, vals):
    """A function to pivot a dataframe.

    Parameters
    ----------
    df : dataframe
        Dataframe to pivot.

    idx : str
        Name of the column in df to use as indexes in the pivoted dataframe.
        
    cols : str
        Name of the column in df to use for the columns in the pivoted dataframe.
        
    vals : str
        Name of the column in df to use for the values in the pivoted dataframe.

    Returns
    -------
    df_pivoted : dataframe
        Pivoted dataframe.

    """
    df_pivoted = df.pivot(index =idx,columns = cols,values = vals)
    return df_pivoted



import matplotlib.pyplot as plt

def pivoted2contourf(df_pivoted):
    """A function to create a contour plot from a pivoted dataframe.

    Parameters
    ----------
    df_pivoted : dataframe
        Pivoted dataframe. The indexes will be used as the y-values and the columns as x-values, with the values used for coloring.

    Returns
    -------
    """
    x,y = np.meshgrid(df_pivoted.columns.values,df_pivoted.index.values)
    
    plot = plt.contourf(x,y,df_pivoted);
    
    plt.colorbar()
    return plot


