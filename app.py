from flask import Flask, render_template, request, redirect, url_for, jsonify
import folium
import requests
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
import os
import googlemaps
from user_agents import parse  
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("MY_API_KEY")






app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/restaurants.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)
    link = db.Column(db.String(1000), nullable=False)  
    pure = db.Column(db.Boolean, default=False)
    cuisines = db.Column(db.JSON)
    description = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    user_agent = parse(request.headers.get('User-Agent'))
    if user_agent.is_mobile:
        template = 'index_mobile.html'
    else:
        template = 'index.html'
    
    start_coords = (37.0902, -95.7129)
    folium_map = folium.Map(location=start_coords, zoom_start=6)
    folium_map.save('templates/map.html')
    return render_template(template)

@app.route('/add_restaurant')
def add_restaurant():
    user_agent = parse(request.headers.get('User-Agent'))
    if user_agent.is_mobile:
        template = 'add_restaurantMobile.html'
    else:
        template = 'add_restaurant.html'
    success = request.args.get('success')
    return render_template(template, success=success)

@app.route('/your_form_endpoint', methods=['POST'])
def handle_form():
    user_input = request.json.get('userInput')
    gmaps = googlemaps.Client(key=API_KEY)
    geocode_result = gmaps.geocode(user_input)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return jsonify(status='success', lat=location['lat'], lng=location['lng'])
    return jsonify(status='failure')

def addFlag(restaurant, folium_map):
    markerHTMLTemplate = """
    <div style="position: relative; width: 18.75px; height: 30.75px; text-align: center;">
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 30px; height: 30px; background-color: #fff; border: 2px solid black; border-radius: 50%;">
            <img src="static/{image}" alt="{alt}" style="width: 100%; height: 100%; border-radius: 50%;" />
        </div>
        <div style="position: absolute; top: 32px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 6.75px solid transparent; border-right: 6.75px solid transparent; border-top: 12.75px solid black;"></div>
    </div>
    """

    indianHTML = markerHTMLTemplate.format(image="indian.png", alt="indian")
    italianHTML = """
    <div style="position: relative; width: 18.75px; height: 30.75px; text-align: center;">
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 30px; height: 30px; background: linear-gradient(to right, #009246 33%, #FFFFFF 33%, #FFFFFF 66%, #CE2B37 66%); border: 2px solid black; border-radius: 50%;"></div>
        <div style="position: absolute; top: 32px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 6.75px solid transparent; border-right: 6.75px solid transparent; border-top: 12.75px solid black;"></div>
    </div>
    """
    mexicanHTML = markerHTMLTemplate.format(image="mexican.png", alt="mexican")
    thaiHTML = """
    <div style="position: relative; width: 18.75px; height: 30.75px; text-align: center;">
        <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 30px; height: 30px; background: linear-gradient(to bottom, #A51931 20%, #F4F5F8 20%, #F4F5F8 40%, #2D2A4A 40%, #2D2A4A 60%, #F4F5F8 60%, #F4F5F8 80%, #A51931 80%); border: 2px solid black; border-radius: 50%;"></div>
        <div style="position: absolute; top: 32px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 6.75px solid transparent; border-right: 6.75px solid transparent; border-top: 12.75px solid black;"></div>
    </div>
    """
    sushiHTML = markerHTMLTemplate.format(image="sushi.jpeg", alt="Sushi")
    mediterraneanHTML = markerHTMLTemplate.format(image="mediterranean.jpeg", alt="mediterranean")
    americanHTML = markerHTMLTemplate.format(image="american.png", alt="american")
    asianHTML = markerHTMLTemplate.format(image="asian.jpeg", alt="asian")
    dessertHTML = markerHTMLTemplate.format(image="dessert.jpeg", alt="dessert")
    beveragesHTML = markerHTMLTemplate.format(image="beverages.jpeg", alt="beverages")

    restaurantType = restaurant.cuisines[0].lower()
    if restaurantType == "indian": Icon = folium.DivIcon(html=indianHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "italian": Icon = folium.DivIcon(html=italianHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "mexican": Icon = folium.DivIcon(html=mexicanHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "thai": Icon = folium.DivIcon(html=thaiHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "sushi": Icon = folium.DivIcon(html=sushiHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "mediterranean": Icon = folium.DivIcon(html=mediterraneanHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "asian": Icon = folium.DivIcon(html=asianHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "american": Icon = folium.DivIcon(html=americanHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "dessert": Icon = folium.DivIcon(html=dessertHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    elif restaurantType == "beverages": Icon = folium.DivIcon(html=beveragesHTML, icon_size=(30, 42.75), icon_anchor=(15, 42.75))
    else: Icon = folium.DivIcon(icon_size=(30, 42.75), icon_anchor=(15, 42.75))

    place = "Restaurant"
    if "dessert" in restaurant.cuisines or "beverages" in restaurant.cuisines:
        place = "Place"

    message = f"<b>{restaurant.name.title()}</b>: "
    if len(restaurant.cuisines) > 1:
        for i in range(len(restaurant.cuisines) - 1):
            message += restaurant.cuisines[i].capitalize() + " and "
        message += restaurant.cuisines[-1].capitalize() + " " + place + "."
    else:
        message += restaurant.cuisines[0].capitalize() + " " + place + "."
    message += "<br>"
    if restaurant.pure:
        message += "Pure Veg/Vegan: Yes"
    else:
        message += "Pure Veg/Vegan: No"
    if restaurant.description.strip() != "":
        message += "<br>" + "Notes and Entrees: " + restaurant.description 
    message += "<br>" + f'<a href="{restaurant.link}" target="_blank">More Information and Directions</a>'
    
    folium.Marker(
        location=(restaurant.lat, restaurant.long),
        popup=folium.Popup(f"""<div style="width: 175px;">{message}</div>""", max_width=300),
        icon=Icon,
        tooltip=restaurant.name.title() + ": "+ restaurantType.title()+" "+ place
    ).add_to(folium_map)


@app.route('/update_map', methods=['GET'])
def update_map():
    lat = request.args.get('lat', default=None, type=float)
    lng = request.args.get('lng', default=None, type=float)
    zoom = request.args.get('zoom', default=12, type=int)
    cuisines = request.args.get('cuisines', default="", type=str).split(',')

    if lat is not None and lng is not None:
        start_coords = (lat, lng)
        zoom_level = 11
    else:
        start_coords = (37.0902, -95.7129)
        zoom_level = 4

    folium_map = folium.Map(location=start_coords, zoom_start=zoom_level)
    if lat is not None and lng is not None:
        folium.Circle(location=start_coords, radius=8046.72, color='blue', fill=True, fill_color='blue').add_to(folium_map)

    query = Restaurant.query
    restaurants = query.all()
    
    for restaurant in restaurants:
        if cuisines != ['']:
            if "pure" in cuisines: 
                if restaurant.pure == True:
                    if len(cuisines) == 1:
                        addFlag(restaurant, folium_map)
                    else:
                        if any(cuisine.lower() in [c.lower() for c in restaurant.cuisines] for cuisine in cuisines):
                            addFlag(restaurant, folium_map)
            elif "pure" not in cuisines and any(cuisine.lower() in [c.lower() for c in restaurant.cuisines] for cuisine in cuisines):
                addFlag(restaurant, folium_map)
        else:
            addFlag(restaurant, folium_map)

    folium_map.save('templates/map.html')
    return folium_map._repr_html_()

@app.route('/delete_restaurant', methods=['GET', 'POST'])
def delete_restaurant():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name').strip()
        restaurant = Restaurant.query.filter_by(name=name).first()

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return jsonify(status='success')
        else:
            return jsonify(status='failure')

    return render_template('delete_restaurant.html')



@app.route('/jain_diet')
def jain_diet():
    user_agent = parse(request.headers.get('User-Agent'))
    if user_agent.is_mobile:
        template = 'jain_dietMobile.html'
    else:
        template = 'jain_diet.html'
    return render_template(template)

@app.route('/tithi')
def tithi():
    user_agent = parse(request.headers.get('User-Agent'))
    if user_agent.is_mobile:
        template = 'tithiMobile.html'
    else:
        template = 'tithi.html'
    return render_template(template)

def getAddress(location):
    gmaps = googlemaps.Client(key=API_KEY)
    isRestaurant = False
    url = "https://www.google.com/search?q=" + location.strip()
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div')
        for div in divs:
            if "restaurant" in (div.get_text().strip()):
                isRestaurant = True
                break
        if isRestaurant:
            geocode_result = gmaps.geocode(location)
            dictFull = geocode_result[0]['geometry']['location']
            return (dictFull['lat'], dictFull['lng'])
        
        return [0,0]
    except requests.exceptions.RequestException as e:
        return [0,0]
    except Exception:
        return [0,0]



@app.route('/feedback')
def feedback():
    user_agent = parse(request.headers.get('User-Agent'))
    if user_agent.is_mobile:
        template = 'feedbackMobile.html'
    else:
        template = 'feedback.html'
    return render_template(template)

@app.route('/submit_restaurant', methods=['POST'])
def submit_restaurant():
    name = request.form.get('name').strip()
    city = request.form.get('city').strip()
    state = request.form.get('state').strip()
    country = request.form.get('country').strip()

    address = ", ".join([component for component in [name, city, state, country] if component])
    location = getAddress(address)
    latitude = location[0]
    longitude = location[1]
    cuisines = request.form.getlist('cuisine')
    if not cuisines:
        cuisines = [request.form.get('other_cuisine')]
    else:
        if request.form.get('other_cuisine'):
            cuisines.append(request.form.get('other_cuisine'))

    if location and location[0] != 0 and location[1] != 0:
        existing_restaurant = Restaurant.query.filter_by(lat=location[0], long=location[1]).first()
        if existing_restaurant:
            return redirect(url_for('add_restaurant', success="duplicate"))

        new_restaurant = Restaurant(
            name=name, 
            lat=latitude, 
            long=longitude, 
            link="https://www.google.com/search?q=" + name + " " + city + " " + state + " " + country,
            pure='pure' in request.form,
            cuisines=cuisines,
            description=request.form.get('description')
        )

        db.session.add(new_restaurant)
        db.session.commit()
        
        script_url = 'https://script.google.com/macros/s/AKfycbwXIgf0HjOeCB7Ebz83OUwiEvz0pHxy4083uWvjcBZUpt8J-w_O8NNoS42EeOgxwwPr/exec'
        form_data = {
            'name': name,
            'city': city,
            'state': state,
            'country': country,
            'cuisine': ", ".join(cuisines),
            'pure': 'Yes' if 'pure' in request.form else 'No',
            'description': request.form.get('description')
        }
        requests.post(script_url, data=form_data)
        
        return redirect(url_for('add_restaurant', success=True))
    else:
        return redirect(url_for('add_restaurant', success=False))

@app.route('/debug/restaurants')
def debug_restaurants():
    restaurants = Restaurant.query.all()
    for restaurant in restaurants:
        print(type(restaurant.cuisines))
    return "Check your console for the list of restaurants"

if __name__ == '__main__':
    app.run(debug=True)