import streamlit as st
import requests 

API_KEY = "d6f70eff33972f7f689341bfd7011b05"

st.title("MyOutfit")
st.write("Tell me your city")

result_box = st.empty()

#city first
city = st.text_input("City name")

if city:
    st.write("You entered:", city)


    region = st.selectbox("Which person should the recommendations be optimized for?",
    ["Indian", "Global"]
    )

    generate = st.button("Recommend an Outfit",disabled =not(city and region))
    
    if generate:
        result_box.empty()

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

        response = requests.get(url, params=params)
        
        if response.status_code == 200 and response.text:
            data = response.json()   
            temp = round(data["main"]["temp"])
            humidity = data["main"]["humidity"]
            weather_main = data["weather"][0]["main"]

            with result_box.container():
                st.success(f"Temperature in {city}: {temp} °C")
                st.write(f"Humidity:{humidity}%")
                st.write(f"Weather:{weather_main}")
        #humidity
            advice = []
            
            if weather_main == "Rain":
                advice.append("Carry an Umbrella, or rain coat")
                advice.append("avoid cloth, fancy footwear")
                advice.append("take care of your hair")
            if humidity >= 70:
                advice.append("high humidity - definitely take care of your hair, wear breathable fabric")



        #outfit logic
            #india
            if region == "Indian":
                if temp < -1 :
                    outfit = "Freezing temperatures\nTry to stay at home or in rooms with heater\nwear fleece or wool and snow boots\nStay warm."
                elif -1 < temp < 12:
                    outfit = "Chilly weather\nwear warmers, 3 layers, heavy jacket, closed shoes"
                elif 11 < temp < 18:
                    outfit = "It's gonna be cold\ntwo layers is enough, long sleeves\nDont forget to wear a jacket"
                elif 19 < temp < 28 :
                    outfit = "Pretty warm\none layer works, cotton, sleeves or tshirts"
                elif 29 < temp < 35:
                    outfit = "Hot\nloose cotton clothes and breathable wear\nstay comfy"
                elif temp >= 35 :
                    outfit = "Heat wave\nstay hydrated\nwear sunscreen\navoid dark colours, wear light breathable fabric"
                else:
                    outfit = "Stay cool\nLight cotton clothes"
            
                st.caption("Optimised for Indians")

            #global
            else:
                if temp < -1:
                    outfit = "Freezing temperatures\nTry to stay at home or in rooms with heater\nwear fleece or wool\nStay warm."
                elif -1 < temp < 5:
                    outfit = "Chilly weather\nHeavy winter coat, thermal wear, closed shoes(or snow boots)"
                elif 6 < temp < 15:
                    outfit = "Slightly Cold\nWear a jacket or sweater, closed shoes"
                elif 16 < temp < 25:
                    outfit = "Slightly warm \nlight comfortable clothes"
                else:
                    outfit = "Hot\n wear light, comfortable clothing"

                st.caption("Using global comfort standards")

            st.subheader("Outfit Recommendation")
            st.info(outfit)

            if advice:
                st.subheader("If its raining:")
                for tip in advice:
                    st.write(" " + tip)
    
        else:
            st.error("Failed to fetch weather data")    




   