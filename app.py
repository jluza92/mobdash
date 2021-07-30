import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import datetime

pio.templates.default = "seaborn"

def welcome_text():
    return """
        #### ¡Hola!
        Este proyecto está hecho para facilitar el acceso y análisis de los datos de movilidad públicos de Facebook y Google.
        
        El dashboard está hecho con Python y Streamlit. Los datos se obtienen de [Movement Range Maps](https://data.humdata.org/dataset/movement-range-maps?) y de [Google Mobility Reports](https://www.google.com/covid19/mobility/).

        Para usar la herramienta solamente tenes que elegir las opciones deseadas en la **barra lateral**.

        A las gráficas se les puede hacer zoom, ocultar trazos, etc. Revisá todo lo que podés hacer [acá](https://plotly.com/chart-studio-help/zoom-pan-hover-controls/).
        
        Podés encontrar el código de Streamlit en mi **[Github](https://github.com/jluza92)**.
        
        ¡Espero que te sirva!
        ### [Jerónimo Luza](https://www.linkedin.com/in/jluza/)
        """

def instructions_text():
    return """
### Barra lateral
- Seleccioná localidades a visualizar y comparar
- Seleccioná la métrica de Movement Range Maps (click [acá](https://dataforgood.fb.com/tools/movement-range-maps/#:~:text=The%20Change%20in%20Movement%20metric,home%20for%20an%20entire%20day.) para información de las variables)
    > **Change in Movement**: The Change in Movement metric looks at how much people are moving around and compares it to a baseline period that predates most social distancing measures.
    >
    > **Stay Put**: The Stay Put metric looks at the fraction of the population that appears to stay within a small area surrounding their home for an entire day.
- Seleccioná la métrica de Google Mobility Reports (más información [acá](https://www.google.com/covid19/mobility/?hl=en))
    > The reports chart movement trends over time by geography, across different categories of places such as retail and recreation, groceries and pharmacies, parks, transit stations, workplaces, and residential.        

- Podés elegir las fechas usando el último widget de la barra lateral o también podes hacer zoom sobre los gráficos.
        """



vars_dict = {'all_day_bing_tiles_visited_relative_change':'Change in Movement',
 'all_day_ratio_single_tile_users':'Stay Put',
 'retail_and_recreation_percent_change_from_baseline':'Retail and recreation change',
 'grocery_and_pharmacy_percent_change_from_baseline':'Grocery and pharmacy change',
 'parks_percent_change_from_baseline':'Parks change',
 'transit_stations_percent_change_from_baseline':'Transit stations change',
 'workplaces_percent_change_from_baseline':'Workplaces change',
 'residential_percent_change_from_baseline':'Residential change',
 'strindex':'Oxford Stringency Index'}

fb_vars = [vars_dict[x] for x in vars_dict][:2]
g_vars = [vars_dict[x] for x in vars_dict][2:-1]
ox_vars = [vars_dict[x] for x in vars_dict][-1]

st.title('Mobility Reports Dashboard')

DATE_COLUMN = 'Fecha'
DATA_PATH = 'buenosaires.csv'

@st.cache
def load_data():
    data = pd.read_csv(DATA_PATH, index_col = 0)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN], format = '%Y-%m-%d')
    data[g_vars] = data[g_vars].astype(float).div(100)
    return data

data = load_data()
#data[g_vars] = data[g_vars].div(100)

max_date = data[DATE_COLUMN].max()
min_date = data[DATE_COLUMN].min()

st.sidebar.title('Opciones')
st.sidebar.subheader('Seleccioná una localidad')

data = data.sort_values(['Provincia','Partido/Departamento','Fecha'])

data = data.rename(columns = {'marker':'Localidades'})
localidades = data['Localidades'].unique().tolist()
selected_zones = st.sidebar.multiselect("Localidades", localidades, default = ['Mercedes, Buenos Aires','Distrito Federal, Ciudad de Buenos Aires'])


#partidos = data[data['Provincia'].isin(selected_zones1)]['Partido/Departamento'].sort_values().unique().tolist()
#selected_zones2 = st.sidebar.multiselect("Partidos Municipales", partidos, default = ['Mercedes','Distrito Federal'])

st.sidebar.subheader("Movement Range Maps")
f_vars_selected = st.sidebar.selectbox('Movement Range Maps variables', fb_vars)

st.sidebar.subheader("Google Mobility Reports")
g_vars_selected = st.sidebar.selectbox('Google Mobility Reports variables', g_vars)

start_date, end_date = st.sidebar.date_input('Fechas', max_value=max_date, min_value=min_date, value=(min_date, max_date))

plot_data = data[data['Localidades'].isin(selected_zones)]

#plot_data = data[(data['Provincia'].isin(selected_zones1))&(data['Partido/Departamento'].isin(selected_zones2))]
plot_data = plot_data[(plot_data['Fecha'] > pd.to_datetime(start_date))&(plot_data['Fecha'] < pd.to_datetime(end_date))]


oxford_plot_data = plot_data[['Fecha','Oxford Stringency Index']]

# Welcome message
welcome = st.beta_expander(label="Bienvenida", expanded=True)
with welcome:
    st.write(welcome_text())
    st.write("")

# Instructions message
instructions = st.beta_expander(label="Instrucciones", expanded=False)
with instructions:
    st.write(instructions_text())

if st.checkbox('Mostrar datos en tabla'):
    st.subheader('Últimas fechas')
    st.write(plot_data.tail())

st.write('Los números mostrados están en cambios porcentuales con respecto a una fecha base, es decir, si el número es 0, no hay diferencias con la fecha base. Si el número es -0.45, el cambio es una caida en la variable de casi la mitad.')
st.subheader('Gráfico 1')

st.write('- **Change in Movement** nos dice cuanta gente que no vive en la región está de visita.')
st.write('- **Stay Put** nos dice cuanta gente que vive en la región se quedo todo el día en su casa,')
fig1 = px.line(plot_data,
                x='Fecha',
                y=f_vars_selected,
                color= 'Localidades',
                title= f_vars_selected, width=800, height=600)



st.plotly_chart(fig1)

st.subheader('Gráfico 2')
fig2 = px.line(plot_data,
                x='Fecha',
                y=g_vars_selected,
                color= 'Localidades',
                title= g_vars_selected, width=800, height=600)

st.plotly_chart(fig2)
