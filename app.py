#from turtle import up
import streamlit as st
#import urllib2
import requests
import datetime
import os
import requests

st.markdown("""
    # Engineering Drawings Smart Reader

    ### A powerfull tool to retrieve data from engineering P&ID drawings

    **bold** or *italic* text with [links](http://github.com/streamlit) and:
    - bullet points
""")
URL = 'http://localhost:8000'

uploaded_file = st.file_uploader("Upload a file")


if uploaded_file:

    st.write("Filename: ", uploaded_file.name)

    if st.button('Send file'):
        # print is visible in the server output, not in the page
        print('button clicked!')
        response = requests.post(f'{URL}/upload', files={'file':uploaded_file}, verify=False)
        st.write(response)
        #st.write('Further clicks are not visible but are executed')
    else:
        st.write('I was not clicked 😞')
