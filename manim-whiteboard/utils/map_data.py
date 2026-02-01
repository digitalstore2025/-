"""
Geographic coordinate data for Palestinian territories.
Coordinates are normalized for Manim's coordinate system (-7 to 7 range).
"""

# Gaza Strip - Simplified polygon coordinates
# Normalized to fit Manim's default frame
GAZA_COORDINATES = [
    # Starting from Rafah (south) going clockwise
    (-0.8, -2.5, 0),   # Rafah - Southwest border
    (-0.3, -2.6, 0),   # Rafah crossing area
    (0.5, -2.3, 0),    # Kerem Shalom area
    (0.7, -1.5, 0),    # Eastern border south
    (0.8, -0.5, 0),    # Khan Yunis east
    (0.9, 0.5, 0),     # Central east
    (1.0, 1.5, 0),     # Gaza City east
    (0.8, 2.2, 0),     # Beit Hanoun area
    (0.3, 2.5, 0),     # Erez crossing
    (-0.5, 2.3, 0),    # Northern coast
    (-1.0, 1.5, 0),    # Beach camp area
    (-1.2, 0.5, 0),    # Gaza port
    (-1.3, -0.5, 0),   # Deir al-Balah coast
    (-1.2, -1.5, 0),   # Khan Yunis coast
    (-1.0, -2.3, 0),   # Rafah coast
]

# Key cities in Gaza (for labeling)
GAZA_CITIES = {
    'gaza_city': {'pos': (-0.2, 1.8, 0), 'name': 'Gaza City', 'name_ar': 'مدينة غزة'},
    'khan_yunis': {'pos': (-0.3, -1.2, 0), 'name': 'Khan Yunis', 'name_ar': 'خان يونس'},
    'rafah': {'pos': (-0.5, -2.3, 0), 'name': 'Rafah', 'name_ar': 'رفح'},
    'jabalia': {'pos': (0.2, 2.0, 0), 'name': 'Jabalia', 'name_ar': 'جباليا'},
    'deir_balah': {'pos': (-0.4, 0.0, 0), 'name': 'Deir al-Balah', 'name_ar': 'دير البلح'},
    'beit_hanoun': {'pos': (0.5, 2.3, 0), 'name': 'Beit Hanoun', 'name_ar': 'بيت حانون'},
}

# West Bank - Simplified coordinates
WEST_BANK_COORDINATES = [
    # Northern region
    (-1.5, 3.0, 0),    # Jenin area
    (0.5, 3.2, 0),     # Northeast
    (1.5, 2.0, 0),     # Jordan Valley north
    (2.0, 0.5, 0),     # Jordan Valley central
    (2.2, -1.0, 0),    # Dead Sea north
    (1.8, -2.5, 0),    # Dead Sea south
    (0.5, -3.0, 0),    # Hebron hills
    (-1.0, -2.5, 0),   # Southern tip
    (-1.5, -1.0, 0),   # Western border south
    (-2.0, 0.5, 0),    # Central west
    (-1.8, 2.0, 0),    # Tulkarm area
]

# Key cities in West Bank
WEST_BANK_CITIES = {
    'ramallah': {'pos': (-0.5, 0.8, 0), 'name': 'Ramallah', 'name_ar': 'رام الله'},
    'nablus': {'pos': (-0.3, 2.0, 0), 'name': 'Nablus', 'name_ar': 'نابلس'},
    'hebron': {'pos': (-0.2, -2.0, 0), 'name': 'Hebron', 'name_ar': 'الخليل'},
    'bethlehem': {'pos': (0.0, -0.5, 0), 'name': 'Bethlehem', 'name_ar': 'بيت لحم'},
    'jericho': {'pos': (1.5, 0.5, 0), 'name': 'Jericho', 'name_ar': 'أريحا'},
    'jenin': {'pos': (-0.5, 2.8, 0), 'name': 'Jenin', 'name_ar': 'جنين'},
}

# Sea boundaries for Mediterranean
MEDITERRANEAN_BOUNDS = {
    'x_range': (-7, -1.5),
    'y_range': (-4, 4),
}
