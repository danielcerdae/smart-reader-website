from io import StringIO
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import datetime
import os
import time
import requests
import pandas as pd
from PIL import Image
import numpy as np

st.set_page_config(
    page_title="Smart-Reader",
    page_icon="smart-reader-logo.png",
    layout="wide",
)

URL = "http://localhost:8000"

with st.container():

    col1, col2 = st.columns([5, 20], gap='small')

    with col1:
        st.image("smart-reader-logo.png", width=150)

    with col2:
        st.title(
            " Engineering Drawings / Smart Reader \n ## Online tool to retrieve data from P&ID diagrams  🚀 "
        )
        st.markdown(
            """
        ### Automatically identifies piping elements inside drawings
        ##### ✅  Centrifugal Pumps ✅ Butterfly, Check & Gate Valves
        """
        )
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### Upload a file")
        uploaded_file = st.file_uploader("")

    with col2:
        st.markdown("#### Tune the Object Detection Model")
        confidence_threshold = st.slider(
            "Set the confidence threshold",
            min_value=0.1,
            max_value=0.9,
            step=0.1,
            value=0.6,
        )
        slicing = st.checkbox("Enhanced searching algorithm", value=True)

    st.markdown("---")

    if uploaded_file is not None:

        if st.button("Process File"):

            col1, col2 = st.columns(2, gap="medium")

            with col1:

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

            tab1, tab2 = st.tabs(["Prediction Visualization", "Original Image"])

            with tab1:
                st.image(response_body_2["predicted_image_url"])

            with tab2:
                st.image(response_body_2["original_image_url"])

            #st.write(round(float(response_headers_2["X-Process-Time"])))

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

                category_count_df=df.groupby(by=['Category'])['Score'].count().reset_index(name='Count')
                category_count_df['Percentage']=100*category_count_df['Count']/category_count_df['Count'].sum()

                st.markdown("---")
                st.markdown('### Results Summary 🔎 ')

                col1, col2 = st.columns(2, gap="large")

                with col1:
                    #Bar chart
                    fig=px.bar(
                        category_count_df,
                        x='Category',
                        y='Count',
                        text_auto='.2s',
                        color='Category'
                    )
                    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                    st.markdown(""" ##### **Elements found on Drawing**""")
                    st.plotly_chart(fig)

                with col2:
                #Pie chart
                    fig=go.Figure(
                        go.Pie(
                            labels=category_count_df['Category'],
                            values=(category_count_df['Percentage']),
                            hoverinfo='label+percent',
                        ))
                    fig.update_traces(textposition='inside', textinfo='percent')
                    st.markdown(""" ##### **Distribution of Elements (%)**""")
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
