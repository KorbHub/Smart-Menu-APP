import easyocr as ocr  #OCR
import streamlit as st  #Web App
from PIL import Image #Image Processing
import numpy as np #Image Processing 
import spacy #Naturl language Processing 
import ja_ginza
nlp = spacy.load('ja_ginza')
import requests
from io import BytesIO #Image showing library 
from googletrans import Translator, constants #translation system 
# init the Google API translator
translator = Translator()
# using to show the dataframe
import pandas as pd 

#title
st.title("Smart Menu")

#subtitle
st.markdown("## Optical Character Recognition & Name Entity Recognition & WEB_API")

#image uploader
image = st.file_uploader(label = "Upload your menu image here",type=['png','jpg','jpeg'])
selected_language = st.selectbox('Select a language for scaning',('en','ja','ko','nl','th','zh-CN','zh-TW','ru','es','de'))
translated_language = st.selectbox('Select a language for translation',('en','ja','ko','nl','th','zh-CN','zh-TW','ru','es','de'))
health_labels = ['ALCOHOL-FREE', 'CELERY-FREE', 'CRUSTACEAN-FREE', 'DAIRY-FREE', 'EGG-FREE', 'FISH-FREE', 'GLUTEN-FREE', 'KIDNEY-FRIENDLY', 'KOSHER', 'LOWPOTASSIUM', 'LOW-SUGAR', 'LUPINE-FREE', 'MUSTARD-FREE', 'LOW-FAT-ABS', 'NO OIL ADDED', 'NO-SUGAR', 'PALEO', 'PEANUT-FREE', 'PESCATARIAN', 'PORK-FREE', 'RED-MEAT-FREE', 'SESAME-FREE', 'SHELLFISH-FREE', 'SOY-FREE', 'SUGAR-CONSCIOUS', 'TREE-NUT-FREE', 'VEGAN', 'VEGETARIAN', 'WHEAT-FREE']
selected_healthlabel = st.multiselect('What are your food choices',health_labels)
list_selected_heatlhlabel = []
for option in selected_healthlabel:
    list_selected_heatlhlabel.append(option)

@st.cache
# def load_model
def load_model(): 
    reader = ocr.Reader([selected_language],model_storage_directory='.')
    return reader 

# def searching menu 
def menu_search(menu):
    from serpapi import GoogleSearch
    params = {
      "q": menu,
      "tbm": "isch",
      "ijn": "0",
      "api_key": "27a09ade93df9a769bb31dfc384b482962938e193db3932e1615699eadfeb2b9"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = results["images_results"]
    url = images_results[0]['original']

    return url
def nutrient_search(menu):
    import requests
    
    # Define the endpoint and parameters for the API request
    endpoint = 'https://api.edamam.com/api/nutrition-data'
    params = {
        'app_id': '742dfbb0',
        'app_key': '86d612a8156f10f9332196b6f9a4d208',
        'ingr': menu
    }

    # Send a GET request to the API and parse the JSON response
    response = requests.get(endpoint, params=params)
    data = response.json()

    # Extract the nutrient and allergy information from the response
    Health_label = data['healthLabels']
    
    return Health_label 
def translation(text,lang):
    translation = translator.translate(text, dest=lang)
    return translation.text
# Define a function to load the image from a URL and convert to bytes
def url_to_image_bytes(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return st.image(img,use_column_width=True)

def ingredients(name):
    # Define your API credentials
    app_id = 'e9d94a94'
    app_key = 'c30395caf6e9bfb3031ff8eeb7fc408e	'

    # Define the base URL for the Edamam Recipe Search API
    base_url = 'https://api.edamam.com/search'

    # Define the menu name to search for
    menu_name = name

    # Define the parameters for the API request
    params = {
        'q': menu_name,
        'app_id': app_id,
        'app_key': app_key,
    }

    # Make the API request
    response = requests.get(base_url, params=params)

    # Parse the response to extract the recipe information
    if response.status_code == 200:
        # Extract the recipe details from the response
        recipe_results = response.json()['hits']
        if recipe_results: 
            # For this example, we'll just use the first recipe returned in the search results
            first_recipe = recipe_results[0]['recipe']
            # Extract the ingredient names into a list
            ingredient_names = first_recipe['ingredientLines']
            return  ingredient_names
        else:
            return ['No information']

reader = load_model() #load model

st.write(selected_healthlabel)
st.write(list_selected_heatlhlabel)


if image is not None:

    input_image = Image.open(image) #read image
    st.image(input_image) #display image

    with st.spinner("🤖 AI is at Work! "):
        

        result = reader.readtext(np.array(input_image))
        columns = ['Original_menu_name', 'Translated_menu_name', 'Image', 'Ingredient_name','Health_label']
        rows = []
        for text in result:
            doc = nlp(text[1])
            for ent in doc.ents:
                k = []
                if ent.label_ in ["Dish", "Food_Other"]:
                    translated_ent = translation(ent.text,translated_language)
                    img_byte = menu_search(ent.text)
                    search_ent = translation(ent.text,'en')
                    Health_label = nutrient_search(search_ent) 
                    ingredient_list = ingredients(search_ent)
                    k.append(ent.text)
                    k.append(translated_ent)
                    k.append(img_byte)
                    k.append(ingredient_list)
                    k.append(Health_label)
                    rows.append(k)
        df = pd.DataFrame(rows, columns=columns)
        # Adding the recommendation features
        recommend_menu = []
        check_menu = []
        for i in range(len(df['Health_label'])):
            check_health_label = df.iloc[i, 4]
            if all(elem in check_health_label for elem in list_selected_heatlhlabel):
                recommend_menu.append((df.iloc[i,0],df.iloc[i,1]))
                check_menu.append(df.iloc[i,0])
        selected_rows = df[df['Original_menu_name'].isin(check_menu)]
       
        

        
       
    #st.success("Here you go!")
    st.dataframe(df, width=900, height=400, use_container_width=False)
    st.write('recommend_menu')
    st.write(recommend_menu)
    for i in range(len(selected_rows['Original_menu_name'])):
        st.write(selected_rows.iloc[i,0])
        st.write(selected_rows.iloc[i,1])
        url_to_image_bytes(selected_rows.iloc[i,2])
    st.balloons()
else:
    st.write("Upload an Image")

st.caption("Made with korbboon")





