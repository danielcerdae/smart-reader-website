from io import StringIO
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime
import os
import time
import requests
import pandas as pd
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Smart-Reader",
    page_icon="✅",
    layout="wide",
)

# st.markdown(
#     "<style>h1{color: lightblue;} h5{font-weight:400} h3{border-top: 0.5px solid;padding-top: 2rem;margin-top:2rem}</style>",
#     unsafe_allow_html=True,
# )

URL = "http://localhost:8000"

with st.container():

    col1, col2 = st.columns([5, 20])

    with col1:
        st.image("logo.png", width=150)

    with col2:
        st.title(
            " Engineering Drawings Smart Reader \n #### Online tool to retrieve data from P&ID diagrams  🚀 "
        )
        st.markdown(
            """
        ###### **Automatically identifies piping elements**
        ▶️ Valves : Ball, Butterfly, Check, Gate
        ▶️ Centrifugal Pumps
        """
        )


    st.header("Upload a file")

    col1, col2 = st.columns(2, gap="large")

    with col1:

        uploaded_file = st.file_uploader("")

    with col2:
        confidence_threshold = st.slider(
            "Select confidence threshold",
            min_value=0.1,
            max_value=0.9,
            step=0.1,
            value=0.6,
        )

    col1, col2 = st.columns(2, gap="large")

    with col2:
        slicing = st.checkbox("Process image with slicing", value=True)

    if uploaded_file is not None:

        if st.button("Process File"):

            with st.spinner(text="Uploading file"):
                res = requests.post(f"{URL}/upload", files={"file": uploaded_file})

                response_body = res.json()

            if response_body["success"]:
                st.success("File succesfully uploaded")

                filename = response_body["filename"]

                with st.spinner(text="Processing file"):
                    res_2 = requests.get(
                        f"{URL}/predict?filename={filename}&slicing={slicing}&confidence_threshold={confidence_threshold}"
                    )
                    response_body_2 = res_2.json()

                if response_body_2["success"]:
                    st.success("File succesfully processed")

                    response_headers_2 = res_2.headers

                    tab1, tab2 = st.tabs(["Predicted Image", "Original Image"])

                    with tab1:
                        st.image(response_body_2["predicted_image_url"])

                    with tab2:
                        st.image(response_body_2["original_image_url"])

                    st.write(round(float(response_headers_2["X-Process-Time"])))

                    if response_body_2["data"]:

                        df = pd.DataFrame.from_dict(response_body_2["data"])
                        df.drop(
                            ["image_id", "bbox", "segmentation", "iscrowd", "area"],
                            inplace=True,
                            axis=1,
                        )
                        df = df.rename(
                            columns={
                                "score": "Score",
                                "category_id": "Id",
                                "category_name": "Category",
                            }
                        ).set_index("Id")

                        st.dataframe(df)

                        category_count_df=df.groupby(by=['Category'])['Score'].count().reset_index(name='Count')
                        category_count_df['Percentage']=100*category_count_df['Count']/category_count_df['Count'].sum()
                        #Grafico Donuts
                        fig = px.pie(
                            hole=0.2,
                            labels=category_count_df['Category'],
                            names=category_count_df['Percentage'],
                            title='Elements found Drawing'
                        )
                        st.plotly_chart(fig)


                        col1, col2 = st.columns(2, gap="large")

                        with col1:

                            @st.cache
                            def convert_df(df):
                                return df.to_csv().encode("utf-8")

                            csv = convert_df(df)

                            st.download_button(
                                label="Download data as CSV",
                                data=csv,
                                file_name="large_df.csv",
                                mime="text/csv",
                            )

                        with col2:
                            pass



                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.image("https://static.streamlit.io/examples/cat.jpg")

                    with col2:
                        st.image("https://static.streamlit.io/examples/dog.jpg")


col4, col5, col6, col7 = st.columns([1, 20, 1, 1])

# with col7:
#   st.markdown("""
##### Automatically identifies piping elements:

##### - Centrifugal Pumps
##### - Valves : Ball, Butterfly, Check, Gate
#   """)
