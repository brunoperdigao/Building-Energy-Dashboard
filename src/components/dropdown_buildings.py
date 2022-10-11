import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

### Hardcoded list based on previous test. 
### Some buildings don't have a good response from de API, so it onlyt lists the ones that are working, to avoid confusion
names_positive_response = ['1513 Psykiatrinen poliklinikka',
 '1526 Annantalo',
 '1540 Virastotalo, Dagmarinkatu 6 (disabled)',
 '1575 Nuorisoasiainkeskus, Lpk Leppäsuo',
 '1580 Kruununmakasiini',
 '1620 Tulli- ja pakkahuone, K 11',
 '1689 Asunnottomien palvelukeskus (disabled)',
 '1716 Töölön virastotalo',
 '4225 Nervanderinkatu väestönsuoja',
 '1761 K30, Leijonakortteli',
 '1764 K31, Sarvikuono kortteli',
 '1769 K32, Kluuvin virastotalo',
 '1862 Kallion virastotalo',
 '1838 Lp Piika',
 '2194 Lp Isonneva',
 '2259 Tuomarinkylän ns. piirikeskus',
 '2287 Lpk Lasten Kartano/Malminkartanon nuorisotalo, 67659 Päiväkotirakennus',
 '2355 Lpk Immola, Dh Staffan, Pukinmäenkaaren pk ja Lp, 68090 Rak 001, Lpk Immola ja Lp Tervapääsky',
 '4048 Läntinen sosiaalikeskus',
 '4353 Suomenlinnan ala-aste, 40886 koulurakennus ',
 '4354 Suursuon virastotalo (suvi)',
 '4460 Arhotien väestönsuoja, 41180 väestönsuoja ',
 '4461 Roihupelto väestönsuoja',
 '4480 Lpk ja Lp Tuorinniemi',
 '4075 Lp Jalopeura',
 '2239 Väistötila Kaisaniemen aa',
 '6760 Kaupunkiympäristön toimiala, 44572 Kaupunkiympäristön toimitalo (disabled)',
 '6829 Helsingin Kalasataman Kymppi Koy, 66440 Kymp-talo rak 001',
 '4145 Botby grundskola']

def render(app: Dash, buildings_info: list) -> list:
    # names_list = [x[0] for x in buildings_info]
    names_list = names_positive_response
    names_edit = []
    print("#", names_list[:5])
    print("@", names_positive_response[:5])
    for name in names_list:
        if len(name) > 35:
            edited_name = name[:35] + '...'
            names_edit.append(edited_name)
        else:
            names_edit.append(name)
    return dcc.Dropdown(names_edit, names_edit[1], id='dd-buildings')
