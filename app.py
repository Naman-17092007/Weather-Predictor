from flask import Flask, render_template, request, make_response
from weatherpredictor import get_coordinates, get_weather, get_weather_description

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    weather_data = None
    error_message = None
    
    city = request.args.get('city')
    if city:
        coords = get_coordinates(city)
        if coords:
            lat, lon, city_name, country = coords
            current_weather, daily_forecast = get_weather(lat, lon)
            
            if current_weather and daily_forecast:
                # Enrich current weather with description
                weathercode = current_weather.get('weathercode', 0)
                current_weather['description'] = get_weather_description(weathercode)
                
                # Process daily forecast for the template
                forecast_list = []
                if 'time' in daily_forecast:
                    for i in range(len(daily_forecast['time'])):
                        day = daily_forecast['time'][i]
                        max_t = daily_forecast['temperature_2m_max'][i]
                        min_t = daily_forecast['temperature_2m_min'][i]
                        code = daily_forecast['weathercode'][i]
                        cond = get_weather_description(code)
                        
                        forecast_list.append({
                            'date': day,
                            'max_temp': max_t,
                            'min_temp': min_t,
                            'condition': cond
                        })
                
                weather_data = {
                    'city': city_name,
                    'country': country,
                    'current': current_weather,
                    'forecast': forecast_list
                }
            else:
                error_message = "Could not retrieve weather data from the API."
        else:
            error_message = f"Could not find coordinates for city '{city}'."
            
    response = make_response(render_template('index.html', weather=weather_data, error=error_message))
    
    # Optimize for Vercel Edge Caching (cache for 30 minutes)
    if weather_data:
        response.headers['Cache-Control'] = 'public, s-maxage=1800, stale-while-revalidate=600'
    else:
        response.headers['Cache-Control'] = 'public, max-age=3600'
        
    return response

if __name__ == '__main__':
    app.run(debug=True)
