import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid
from st_aggrid.shared import JsCode
import base64
import os
from google.oauth2 import service_account
from google.cloud import storage


st.set_page_config(
    page_title="Smart-Reader",
    page_icon="static/images/smart-reader-logo.png",
    layout="wide",
)


credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

URL = os.environ.get("BASE_URL")


with st.container():

    col1, col2 = st.columns([3, 14])

    with col1:
        st.image("static/images/smart-reader-logo.png", use_column_width="auto")

    with col2:
        st.markdown(
            """
                    ## P&ID Smart Reader
                    #### Tool to retrieve data from Piping and Instrumentation Diagrams 🚀
                    The model automatically detects piping elements from engineering drawings. It has been trained to identify **Centrifugal Pumps**, **Butterfly Valves**, **Check Valves** and **Gate Valves**.
                    """
        )

    url = "https://drive.google.com/drive/folders/1gKG3jGuJSsnw-GKD8yBgkjSSY1GZlghW?usp=sharing"
    st.info("Would like to try the tool? Use these [sample diagrams](%s)" % url)

    st.markdown("### Upload a file")

    uploaded_file = st.file_uploader(label="", label_visibility="collapsed", type="pdf")

    with st.expander("Model settings"):
        confidence_threshold = st.slider(
            "Confidence threshold: determines how likely it is that a detection is accurate",
            min_value=0.1,
            max_value=0.9,
            step=0.1,
            value=0.6,
        )
        slicing = st.checkbox("Use an optimized algorithm to process large images", value=True)

    if uploaded_file is not None:

        if st.button("Process File"):

            with st.spinner(text="Uploading file"):
                res = requests.post(f"{URL}/upload", files={"file": uploaded_file})

                response_body = res.json()

            if response_body["success"]:
                st.info("File succesfully uploaded")

                filename = response_body["filename"]

                with st.spinner(text="Processing file"):
                    res_2 = requests.get(
                        f"{URL}/predict?filename={filename}&slicing={slicing}&confidence_threshold={confidence_threshold}"
                    )
                    response_body_2 = res_2.json()

                if response_body_2["success"]:
                    st.info("File succesfully processed")

                    response_headers_2 = res_2.headers

            tab1, tab2 = st.tabs(["Prediction Visualization", "Original Image"])

            with tab1:
                st.image(response_body_2["predicted_image_url"])

            with tab2:
                st.image(response_body_2["original_image_url"])

            if response_body_2["data"]:

                df = pd.DataFrame.from_dict(response_body_2["data"])
                df.drop(
                    ["image_id", "category_id", "segmentation", "iscrowd", "area"],
                    inplace=True,
                    axis=1,
                )
                df = df.rename(
                    columns={
                        "score": "Precision",
                        "bbox": "Coordinates",
                        "category_name": "Elements",
                    }
                )

                category_count_df = (
                    df.groupby(by=["Elements"])["Precision"]
                    .count()
                    .reset_index(name="Count")
                )
                category_count_df["Percentage"] = (
                    100 * category_count_df["Count"] / category_count_df["Count"].sum()
                )

                categories = category_count_df["Elements"]
                categories_list = [category for category in categories]
                categories_list = set(categories_list)

                col1, col2, col3, col4, col5 = st.columns([5, 1, 7, 6, 2])

                with col1:
                    st.markdown("#")
                    st.markdown("### Results ready 🔎")
                    st.markdown("#")
                    st.markdown("###")

                    def ReadPictureFile(wch_fl):
                        try:
                            return base64.b64encode(open(wch_fl, "rb").read()).decode()

                        except:
                            return ""

                    category_dict = {
                        category: category_count_df.loc[
                            category_count_df["Elements"] == category, "Count"
                        ].values[0]
                        for category in categories
                    }

                    def ReadPictureFile(wch_fl):
                        try:
                            return base64.b64encode(open(wch_fl, "rb").read()).decode()
                        except:
                            return ""

                    ShowImage = JsCode(
                        """function (params) {
                                var element = document.createElement("span");
                                var imageElement = document.createElement("img");

                                if (params.data.ImgPath != '') {
                                    imageElement.src = params.data.ImgPath;
                                    imageElement.width="55";
                                } else { imageElement.src = ""; }
                                element.appendChild(imageElement);
                                element.appendChild(document.createTextNode(params.value));
                                return element;
                                }"""
                    )

                    table_df = pd.DataFrame(
                        {
                            "Elements": [
                                "  Butterfly Valve",
                                "  Check Valve",
                                "  Gate Valve",
                                "  Centrifugal Pump",
                            ],
                            "Count": [
                                str(category_dict.get("Butterfly-valve", 0)),
                                str(category_dict.get("Check-valve", 0)),
                                str(category_dict.get("Gate-valve", 0)),
                                str(category_dict.get("Centrifugal-pump", 0)),
                            ],
                            "ImgLocation": ["Local", "Local", "Local", "Local"],
                            "ImgPath": [
                                "static/images/butterfly.png",
                                "static/images/check.png",
                                "static/images/gate.png",
                                "static/images/pump.png",
                            ],
                        }
                    )

                    if table_df.shape[0] > 0:
                        for i, row in table_df.iterrows():
                            if row.ImgLocation == "Local":
                                imgExtn = row.ImgPath[-4:]
                                row.ImgPath = (
                                    f"data:image/{imgExtn};base64,"
                                    + ReadPictureFile(row.ImgPath)
                                )

                    gb = GridOptionsBuilder.from_dataframe(table_df)
                    gb.configure_column("Elements", cellRenderer=ShowImage)
                    gb.configure_column("ImgLocation", hide="True")
                    gb.configure_column("ImgPath", hide="True")

                    vgo = gb.build()
                    AgGrid(table_df, gridOptions=vgo, height=147, allow_unsafe_jscode=True)

                with col2:
                    pass

                with col3:
                    st.markdown("#")
                    st.markdown("#")
                    fig = px.bar(
                        category_count_df,
                        x="Elements",
                        y="Count",
                        color="Elements",
                        text_auto=".2s",
                        height=350,
                    )
                    fig.update_traces(textfont_size=12, textangle=0, cliponaxis=False)
                    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
                    st.plotly_chart(fig, use_container_width=True)

                with col4:
                    fig = go.Figure(
                        go.Pie(
                            #title="Distribution",
                            labels=category_count_df["Elements"],
                            values=(category_count_df["Percentage"]),
                            hoverinfo="label+percent",
                            hole=.3,
                        )
                    )
                    fig.update_traces(textposition="inside", textinfo="percent")
                    fig.update(layout_showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                with col5:
                    pass

                processing_time = round(float(response_headers_2["X-Process-Time"]), 2)
                st.info(f"Total processing time: {processing_time} seconds")

                image_filename = response_body_2["image_id"]

                bucket_name = os.environ.get("GOOGLE_CLOUD_BUCKET")
                source_blob_name = f"{image_filename}-predicted.png"
                destination_filename = f"static/downloads/{image_filename}.png"

                @st.cache
                def download_blob(bucket_name, source_blob_name, destination_filename):

                    storage_client = storage.Client(credentials=credentials)

                    bucket = storage_client.bucket(bucket_name)
                    blob = bucket.blob(source_blob_name)
                    blob.download_to_filename(destination_filename)

                    print(
                        "Downloaded storage object {} from bucket {} to local file {}.".format(
                            source_blob_name, bucket_name, destination_filename
                        )
                    )

                @st.cache
                def convert_df(df):
                    return df.to_csv().encode("utf-8")

                with st.spinner(text="Getting the data ready for download"):
                    download_blob(bucket_name, source_blob_name, destination_filename)
                    csv = convert_df(df)

                st.info("The results can be downloaded below")

                st.markdown("#####")

                col1, col2 = st.columns([2,16])

                with col1:
                    st.download_button(
                        label="Download Data as CSV",
                        data=csv,
                        file_name=f"{image_filename}.csv",
                        mime="text/csv",
                    )

                with col2:
                    with open(f"static/downloads/{image_filename}.png", "rb") as file:
                        btn = st.download_button(
                            label="Download Annotated Image",
                            data=file,
                            file_name=f"{image_filename}.png",
                            mime="image/png",
                        )

            else:
                st.info("No piping elements found")
