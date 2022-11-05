from io import StringIO
import streamlit as st
import plotly.express as px
import datetime
import os
import time
import requests
import pandas as pd
from PIL import Image

st.set_page_config(
    page_title="Smart-Reader",
    page_icon="✅",
    layout="wide",
)

st.markdown('<style>h1{color: lightblue;} h5{font-weight:400} h3{border-top: 0.5px solid;padding-top: 2rem;margin-top:2rem}</style>', unsafe_allow_html=True)

# -- Create three columns
col1, col2, col3 = st.columns([1, 5, 20])
# -- Put the image in the middle column
with col2:
    st.image("logo.png", width=150)
# -- Put the title in the last column
with col3:
    st.title(" Engineering Drawings Smart Reader \n #### Online tool to retrieve data from P&ID diagrams  🚀 ")
    st.markdown("""
    ##
    ##### **Automatically identifies piping elements**

    ##### ▶️ Centrifugal Pumps
    ##### ▶️ Valves : Ball, Butterfly, Check, Gate
    """)


col4, col5, col6, col7 = st.columns([1, 20, 1, 1])

with col5:
    st.markdown('### Choose a file in pdf format')
    uploaded_file = st.file_uploader('')

#with col7:
 #   st.markdown("""
    ##### Automatically identifies piping elements:

    ##### - Centrifugal Pumps
    ##### - Valves : Ball, Butterfly, Check, Gate
 #   """)

st.markdown('#')

URL = "http://localhost:8000"


if uploaded_file is not None:

    col8, col9, col10, col11 = st.columns([2, 10, 2, 10])
    with col9:
        if st.button('Process File'):

            res = requests.post(f'{URL}/upload', files={"file": uploaded_file})
            response_body = res.json()

            if res.status_code == 200:
                #st.write(response_body['message'])
                filename = response_body['filename']
                #with col11:
                    #st.markdown('** Analyzing data / searching objects 🔍 **')
                with st.spinner('Analyzing data / searching objects 🔍 ...'):
                    time.sleep(15)
                    st.success('Done!')
                    #my_bar = st.progress(0)
                    #for percent_complete in range(100):
                    #    time.sleep(0.1)
                    #    my_bar.progress(percent_complete + 1)
                res_2 = requests.get(f'{URL}/predict?filename={filename}')
                response_body_2 = res_2.json()
                df = pd.DataFrame.from_dict(response_body_2['data'])
                df.drop(['image_id','bbox','segmentation','iscrowd','area'], inplace=True, axis=1)

                #st.markdown('## Detailed Table')
                #st.dataframe(df)

                res_3 = requests.get(f'{URL}/processed_image?filename={filename}')
                #st.image(res_3.content)
