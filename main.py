import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium import TileLayer
import base64
from collections import defaultdict

# Read the data
data = pd.read_csv('pines-upd.csv')

# Create a map centered on the mean coordinates
geolocator = Nominatim(user_agent='my_geocoder')
map_center = [data['latitude'].mean(), data['longitude'].mean()]
mymap = folium.Map(location=map_center, zoom_start=11)

# Add tile layers
TileLayer('openstreetmap', name='Street View').add_to(mymap)
TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite View'
).add_to(mymap)

# Read the tree icon
with open('pine-tree.png', 'rb') as img:
    tree_base64 = base64.b64encode(img.read()).decode()

# Group trees by their coordinates
tree_locations = defaultdict(list)
for index, row in data.iterrows():
    if row['latitude'] and row['longitude']:
        # Use tuple of coordinates as key
        coord_key = (row['latitude'], row['longitude'])
        tree_locations[coord_key].append(row['age'])

def create_cluster_icon(ages):
   tree_count = len(ages)
   ages_int = [int(age) for age in ages]
   avg_age = round(sum(ages_int) / len(ages_int))
   
   icon_html = f'''
   <div style="position: relative; text-align: center;">
       <img src="data:image/png;base64,{tree_base64}" 
            style="width: 40px; height: 40px; position: relative; z-index: 2;">
       <div style="position: absolute; bottom: -20px; left: 50%; 
                   transform: translateX(-50%);
                   background-color: green; color: white; 
                   border-radius: 12px; padding: 2px 6px; 
                   font-size: 10pt; display: flex; align-items: center; gap: 6px;">
           Age:{avg_age}
           <span style="background-color: #8B4513; border-radius: 50%; 
                      width: 18px; height: 18px; display: flex; 
                      align-items: center; justify-content: center; 
                      font-size: 8pt;">
               {tree_count}
           </span>
       </div>
   </div>'''
   
   return folium.DivIcon(html=icon_html)

# Add markers for each location
for coords, ages in tree_locations.items():
    folium.Marker(
        coords,
        icon=create_cluster_icon(ages)
    ).add_to(mymap)
    
mymap.get_root().html.add_child(folium.Element("""
   <script>
       var lastHighlightedMarker = null;
       
       document.addEventListener('click', function(e) {
           var markerDiv = e.target.closest('.leaflet-marker-icon');
           if (markerDiv) {
               if (lastHighlightedMarker && lastHighlightedMarker !== markerDiv) {
                   lastHighlightedMarker.style.zIndex = '';
               }
               markerDiv.style.zIndex = '1000';
               lastHighlightedMarker = markerDiv;
           } else {
               if (lastHighlightedMarker) {
                   lastHighlightedMarker.style.zIndex = '';
                   lastHighlightedMarker = null;
               }
           }
       });
   </script>
"""))

# Add layer control and save
folium.LayerControl().add_to(mymap)
mymap.save("maps/pines-map.html")