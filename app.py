from io import StringIO
import streamlit as st

import datetime
import os
import requests

from PIL import Image

'''
# Engineering Drawings Smart Reader

This front queries the Le Wagon [taxi fare model API]
'''

URL = "http://localhost:8000"

uploaded_file = st.file_uploader("Choose a file")


if uploaded_file is not None:

    if st.button('Process File'):

        res = requests.post(f'{URL}/upload', files={"file": uploaded_file})
        response_body = res.json()

        if res.status_code == 200:
            st.write(response_body['message'])
            filename = response_body['filename']

            res_2 = requests.get(f'{URL}/predict?filename={filename}')
            response_body_2 = res_2.json()
            st.write(response_body['data'])
