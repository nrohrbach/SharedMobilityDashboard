import requests
import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# Providers.json abfragen
url = 'https://www.sharedmobility.ch/providers.json'
data = requests.get(url).json()
provider_id = [s['provider_id'] for s in data['data']['providers']] 
vehicle_type = [s['vehicle_type'] for s in data['data']['providers']]
last_updated = [s['last_updated'] for s in data['data']['providers']]
name = [s['name'] for s in data['data']['providers']]

# Create Dataframe providers
header = ['provider_id', 'vehicle_type','name','last_updated']
providers = pd.DataFrame(list(zip(provider_id, vehicle_type, name, last_updated)),columns =['provider_id', 'Type','Name','last_updated'])

# Dataframe mit Aktualisierungsstand vorbereiten
# LastUpdated als Zeitobjekt
providers['last_updated'] = pd.to_datetime(providers['last_updated'],unit='s')
# Der jetztige Zeitstand in UTC
now = dt.datetime.utcnow()
# Berechnen wie lange seit letztem Update
providers['delay'] = now - providers['last_updated']
# Delay in Minuten
providers['DelayMinutes'] = round(providers['delay']/np.timedelta64(1,'m'),2)
#Sortiere nach DelayMinutes
providers = providers.sort_values('DelayMinutes', ascending=False)
providers_Cleaned = providers[['provider_id', 'Type', 'DelayMinutes']]

# Funktion welche Zellen farblich hervorhebt.
def colorcells(val):
    color = 'green' 
    if val > 15:
        color = 'red'
    elif val > 5:
        color = 'orange'
    else: 
        color = 'green'
    
    
    return 'background-color: %s' % color

providers_Cleaned = providers_Cleaned.style.applymap(colorcells, subset = ['DelayMinutes'])



# Free_bikes_status.json abfragen

url = 'https://www.sharedmobility.ch/free_bike_status.json'
data = requests.get(url).json()
num_bikes = '1'
location_id = [s['bike_id'] for s in data['data']['bikes']] 
provider_id = [s['provider_id'] for s in data['data']['bikes']]
lat = [s['lat'] for s in data['data']['bikes']]
lon = [s['lon'] for s in data['data']['bikes']]
num_bikes_available = [num_bikes for s in data['data']['bikes']]

# Create Dataframe Free_bikes
header = ['location_id', 'provider_id','lat', 'lon','num_bikes_available']
free_bikes = pd.DataFrame(list(zip(location_id, provider_id, lat, lon, num_bikes_available,)),columns =['location_id', 'provider_id', 'lat', 'lon','num_bikes_available'])


# In[34]:


#free_bikes


# In[36]:


#free_bikes['provider_id'].value_counts().reset_index()


# In[37]:


# Station_information.json abfragen
url = 'https://www.sharedmobility.ch/station_information.json'
data = requests.get(url).json()
location_id = [s['station_id'] for s in data['data']['stations']] 
provider_id = [s['provider_id'] for s in data['data']['stations']]
lat = [s['lat'] for s in data['data']['stations']]
lon = [s['lon'] for s in data['data']['stations']]

# Create Dataframe Station_information
header = ['location_id', 'provider_id', 'lat', 'lon']
station_information = pd.DataFrame(list(zip(location_id, provider_id, lat, lon)),columns =['location_id', 'provider_id', 'lat', 'lon'])

# Station_status.json abfragen
url = 'https://www.sharedmobility.ch/station_status.json'
data = requests.get(url).json()
location_id = [s['station_id'] for s in data['data']['stations']] 
num_bikes_available = [s['num_bikes_available'] for s in data['data']['stations']]

# Create Dataframe Station_status
header = ['location_id', 'num_bikes_available']
station_status = pd.DataFrame(list(zip(location_id, num_bikes_available)),columns =['location_id', 'num_bikes_available'])

#DataFrames zusammenführen
#join with station_information.json with station_status.json
stations = pd.merge(station_information, station_status, on="location_id")
location = pd.concat([stations, free_bikes])
#join with station_information.json with station_status.json
locations = pd.merge(location, providers, on="provider_id")


# In[38]:


locations['num_bikes_available'] = locations['num_bikes_available'].astype(int)
#locations


# In[84]:


ProviderAssets = locations.groupby(['provider_id'])['num_bikes_available'].sum().reset_index()
ProviderAssets = ProviderAssets.sort_values('num_bikes_available', ascending=False)
#ProviderAssets


# In[85]:


st.title('Shared Mobility Dashboard')
st.markdown('''Dieses Dashboard zeigt die Verfügbarkeit und Aktualität der Daten der Shared Mobility Provider auf sharedmobility.ch''')


# In[86]:


st.header('Übersicht der Datenaktualität')
st.dataframe(providers_Cleaned)


# In[87]:


st.header('Naechstes Kapitel')


# In[88]:


barProviderAssets = px.bar(ProviderAssets,x='provider_id', y='num_bikes_available')


# In[89]:


st.plotly_chart(barProviderAssets)


# In[ ]:




