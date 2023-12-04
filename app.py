import streamlit as st
from PIL import Image
import torch
from torchvision import transforms
from transformers import MarianMTModel, MarianTokenizer

from pickle import load
from numpy import argmax
from keras.preprocessing.sequence import pad_sequences
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from keras.models import load_model


# Load the image captioning model
# Note: You need to replace 'your_image_caption_model_path' with the actual path to your trained model
# image_caption_model = torch.load('your_image_caption_model_path')
# image_caption_model.eval()

# Load the translation model for converting caption to speech
# mt_model_name = "Helsinki-NLP/opus-mt-en-de"
# mt_tokenizer = MarianTokenizer.from_pretrained(mt_model_name)
# mt_model = MarianMTModel.from_pretrained(mt_model_name)

def generate_caption(image_path):
        # extract features from each photo in the directory
        def extract_features(filename):
            # load the model
            model = VGG16()
            # re-structure the model
            model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
            # load the photo
            image = load_img(filename, target_size=(224, 224))
            # convert the image pixels to a numpy array
            image = img_to_array(image)
            # reshape data for the model
            image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
            # prepare the image for the VGG model
            image = preprocess_input(image)
            # get features
            feature = model.predict(image, verbose=0)
            return feature

        # map an integer to a word
        def word_for_id(integer, tokenizer):
            for word, index in tokenizer.word_index.items():
                if index == integer:
                    return word
            return None

        # generate a description for an image
        def generate_desc(model, tokenizer, photo, max_length):
            # seed the generation process
            in_text = 'startseq'
            # iterate over the whole length of the sequence
            for i in range(max_length):
                # integer encode input sequence
                sequence = tokenizer.texts_to_sequences([in_text])[0]
                # pad input
                sequence = pad_sequences([sequence], maxlen=max_length)
                # predict next word
                yhat = model.predict([photo,sequence], verbose=0)
                # convert probability to integer
                yhat = argmax(yhat)
                # map integer to word
                word = word_for_id(yhat, tokenizer)
                # stop if we cannot map the word
                if word is None:
                    break
                # append as input for generating the next word
                in_text += ' ' + word
                # stop if we predict the end of the sequence
                if word == 'endseq':
                    break
            return in_text

        # load the tokenizer
        tokenizer = load(open('./tokenizer30k.pkl', 'rb'))
        # pre-define the max sequence length (from training)
        max_length = 70
        # load the model
        model = load_model('./model_0.h5')
        # load and prepare the photograph
        photo = extract_features(image_path)
        # generate description
        description = generate_desc(model, tokenizer, photo, max_length)
        # print(description)

        def remove_start_end_seq(sentence):
            start_token = 'startseq'
            end_token = 'endseq'

            # Remove leading and trailing whitespaces
            sentence = sentence.strip()

            # Remove "startseq" and "endseq" if they exist
            if sentence.startswith(start_token):
                sentence = sentence[len(start_token):].lstrip()
            if sentence.endswith(end_token):
                sentence = sentence[:-len(end_token)].rstrip()

            return sentence

        # Example usage:
        original_sentence = description
        processed_sentence = remove_start_end_seq(original_sentence)
        print(processed_sentence)

        import pyttsx3

        def text_to_speech(text):
            # Initialize the text-to-speech engine
            engine = pyttsx3.init()

            # Set properties (optional)
            engine.setProperty('rate', 150)  # Speed of speech

            # Convert the text to speech
            engine.say(text)

            # Wait for the speech to finish
            engine.runAndWait()

        if __name__ == "__main__":
            text = processed_sentence
            text_to_speech(text)
            # Function to generate caption from the image
            # This is where you use your image captioning model
            # Replace the following line with your actual image captioning code
            caption = text

            return caption

# def translate_to_speech(text):
#     # Function to translate caption to speech
#     translation = mt_model.generate(**mt_tokenizer(text, return_tensors="pt", padding=True))
#     translated_text = mt_tokenizer.batch_decode(translation, skip_special_tokens=True)[0]
    
#     return translated_text

def main():
    st.title("Image Captioning Into Speech")
    st.write("This app takes an image as input, generates a caption, and converts it to speech.")

    uploaded_image = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_image is not None:
        # Display the selected image
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

        # Perform image captioning
        caption = generate_caption(uploaded_image)

        # Display the generated caption
        st.subheader("Generated Caption:")
        st.write(caption)

        # Convert caption to speech
        # speech_text = translate_to_speech(caption)/

        # Display the speech text
        # st.subheader("Speech Text:")
        # st.write(speech_text)

if __name__ == "__main__":
    main()
