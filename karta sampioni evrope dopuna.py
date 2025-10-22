import folium
import pandas as pd
import base64
import os

# Putanje
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
csv_path = os.path.join(desktop, 'europe_champions1.csv')
logos_folder = os.path.join(desktop, 'logos')
output_html = os.path.join(desktop, 'europe_champions_map.html')

# Čitaj CSV
df = pd.read_csv(csv_path, encoding='cp1252', sep=';')
df.columns = df.columns.str.strip().str.lower()

# Konvertuj koordinate u float
df['club_lat'] = df['club_lat'].astype(float)
df['club_lon'] = df['club_lon'].astype(float)

# Kreiraj mapu
m = folium.Map(location=[50, 10], zoom_start=4, tiles='CartoDB positron')

# Grupisanje po klubu
clubs_grouped = df.groupby('champion')

for club, group in clubs_grouped:
    lat = group['club_lat'].iloc[0]
    lon = group['club_lon'].iloc[0]
    city = group['club_city'].iloc[0]

    # Kreiranje HTML sadržaja za popup (sve utakmice)
    rows_html = ""
    for _, row in group.iterrows():
        rows_html += f"""
        <b>Sezona:</b> {row['season']}<br>
        <b>Finale:</b> {row['final_score']} vs {row['opponent']}<br>
        <b>Stadion:</b> {row['final_stadium']}<br>
        <hr>
        """

    logo_file = f"{club.replace(' ', '')}.png"
    logo_path = os.path.join(logos_folder, logo_file)

    if os.path.exists(logo_path):
        encoded_logo = base64.b64encode(open(logo_path, 'rb').read()).decode()
        logo_html = f'<img src="data:image/png;base64,{encoded_logo}" width="80"><br>'
    else:
        logo_html = f'<b>{club}</b><br>'

    html = f"""
    <div style="text-align:center;">
        {logo_html}
        <i>{club}</i> ({city})<br>
        {rows_html}
    </div>
    """

    iframe = folium.IFrame(html=html, width=300, height=300)
    popup = folium.Popup(iframe, max_width=350)

    # Dodaj marker sa logotipom
    if os.path.exists(logo_path):
        icon = folium.CustomIcon(logo_path, icon_size=(35, 35))
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=club,
            icon=icon
        ).add_to(m)
    else:
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=club
        ).add_to(m)
     # --- Dodavanje teksta sa strane ---
from folium import Element

html_text = """
<div style="position: fixed; 
            top: 10px; right: 10px; width: 200px; 
            background-color: white; padding: 10px; 
            border: 2px solid grey; z-index:9999;">
<h4>Legenda / Info</h4>
<p>Karta prikazuje šampione Evrope.<br>
Klik na grb kluba prikazuje sve finalne utakmice.<br>
UEFA Liga šampiona (engl. UEFA Champions League), najjače i najprestižnije evropsko, klupsko fudbalsko takmičenje koje organizuje UEFA i u njemu učestvuju sve njene članice. Do sezone 1991/92. takmičenje se nazivalo Kup evropskih šampiona, Evropski kup šampiona, a od sezone 1992/93. dio se igra u grupama i mijenja naziv u UEFA Liga šampiona.</p>
</div>
"""

element = Element(html_text)
m.get_root().html.add_child(element)
   

# Sačuvaj mapu
m.save(output_html)
print("✅ Mapa sa svim grbovima i kompletnim popupom je uspješno napravljena:", output_html)
