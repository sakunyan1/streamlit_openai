import streamlit as st
import openai
import requests
import json
from datetime import datetime
import zipfile


class ImageGenerator:
    def __init__(self, api_key):
        # set up api_key
        openai.api_key = api_key
        self.api_key = api_key


    def write_files(self, image_url, prompt):
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get the image
        response = requests.get(image_url)

        # Check if the request is successful
        if response.status_code == 200:
            # Download the image and save it as a JPG file
            image_file = f"{timestamp}.jpg"
            with open(image_file, 'wb') as f:
                f.write(response.content)

            # Save the prompt as a text file
            text_file = f"{timestamp}.txt"
            with open(text_file, "w") as txt_file:
                txt_file.write(prompt)

            # Return the file names
            return image_file, text_file, image_url


    def display_image(self, image_url):
        # Display the generated image
        st.image(image_url)

        # Make image accessible via the link retrieved from OpenAI API
        with st.expander("Access your image via link:"):
            st.code(image_url)
            st.caption("Note: This link expires after 1 hour.")


    def download_files(self, image_file, text_file):
        # Check if both files are not None
        if image_file is not None and text_file is not None:
            # Create a ZipFile object
            with zipfile.ZipFile('files.zip', 'w') as zipf:
                # Add multiple files to the zip
                zipf.write(image_file)
                zipf.write(text_file)

            # Provide download for the zip file
            with open('files.zip', 'rb') as f:
                st.write('')
               
                st.download_button(
                    label='Download Files',
                    data=f.read(),
                    file_name='files.zip',
                    mime='application/zip',
                    help = 'WARNING: Page will reset upon clicking this button. If your device cannot download zip files, please save image from the link above.'
                )
                st.session_state['download_button_clicked'] = True



    def generating_images(self, prompt, image_size):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model":"dall-e-3",
            "prompt": prompt,
            "size": image_size,
            "quality": "standard",
            "n": 1
        }

        # Make the API request
        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            image_url = response_data["data"][0]["url"]
            st.session_state['prompts'].append(prompt)
            st.session_state['image_url'].append(image_url)
            image_file, text_file, image_url = self.write_files(image_url, prompt)
            print("Generated image URL:", image_url)

        else:
            st.error(f"Failed to generate image: {str(response.text)}")
            image_file, text_file = None, None

        return image_file, text_file, image_url


    

    

            
class DallE3_App:
    # The initializer method gets executed when a new object of ChatApp is created
    def __init__(self):
        # set page config
        st.set_page_config(page_title="DALL·E 3 Image Generator",
                            page_icon=":art:",
                            layout='centered',
                            initial_sidebar_state="auto")
        
       # for image storing
        if 'prompts' not in st.session_state:
            st.session_state['prompts'] = []
        if 'image_url' not in st.session_state:
            st.session_state['image_url'] = []
        if 'download_button_clicked' not in st.session_state: 
            st.session_state['download_button_clicked'] = False 


    # Run the Chatbot application
    def run(self):

        st.title('Welcome to the DALL·E 3 Image Generator')
        st.subheader("Experience The Magic Of OpenAI's DALL·E 3 Image Generator Bot: Describe, Create, Amaze! :art: ")

        # Enter API Key
        col1, col2 = st.columns([1, 1])
        KEY = col1.text_input("Please paste your API key and hit the 'Enter' key", type="password",
                           help = "To create and collect an API key, visit https://platform.openai.com/account/api-keys, \
                           click on 'API Key', then select 'Create new secret key' and click 'Copy'. \
                           Note: Please be mindful of the number of requests you've sent to DALL·E 3, \
                           as exceeding the free credits limit may result in additional fees.\
                           To check your usage, visit https://platform.openai.com/account/api-keys and click on 'Usage'.")

        st.markdown("***")

        # If API key is entered
        if KEY != '':
            # initialize the bot
            bot = ImageGenerator(KEY)

        
            # text area for prompt
            prompt = st.text_area("Got a picture in mind? Drop a prompt and let’s bring it to life!",
                                    placeholder = "Provide a detailed description here",
                                    value = '')

            col1, col2, col3 = st.columns([1, 0.3, 1])

            # select box for image size
            image_size = col1.selectbox('Select the size of image', ("1024x1024", "1024x1792", "1792x1024"))

            # submit button
            col3.write('')
            col3.write('')
            if prompt == '':
                col3.button('Submit and Generate', help = 'Please ensure all fields have been completed.', disabled = True)
            else:
                if col3.button('Submit and Generate', disabled = False): 
                        image_file, text_file, image_url = bot.generating_images(prompt, image_size)
                        bot.display_image(image_url)

                        if image_file == None :
                            st.error(f'Failed to retrieve images from server.')
                        else:
                            
                            bot.download_files(image_file, text_file)
                            

            st.text('')

            # If API key is not entered
        else:
            st.error('Please enter your API key to generate images!')



# Check if the module is being executed as the main module
if __name__ == '__main__':
    # Create an instance of DallE3_App class
    imggen_app  =  DallE3_App()
    # Call run() method to start the image generator application
    imggen_app.run()
