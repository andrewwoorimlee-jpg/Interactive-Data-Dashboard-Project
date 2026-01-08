import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Page Layout and Theme
st.set_page_config(
    page_title="StatSnap",
    layout="wide"
)

def set_background(image_file):
    """
    Sets a full-screen background image with a semi-transparent overlay for readability.
    """
    # Read and encode the image
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    
    # Inject CSS
    st.markdown(
        f"""
        <style>
        /* Make Streamlit app fill the full viewport */
        .stApp {{
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Optional overlay to keep text readable */
        .stApp::before {{
            content: "";
            position: absolute;
            top:0;
            left:0;
            width:100%;
            height:100%;
            background-color: rgba(255,255,255,0.5); /* adjust opacity as needed */
            z-index: -1;
        }}

        /* Remove Streamlit default padding/margin that causes white bars */
        .block-container {{
            padding: 2rem !important;
            margin: 0 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# CSS for spacing
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Apply the background image
set_background("Marble_Background.jpeg") 

# Title & Description
st.title("📊 Interactive Data Analysis Dashboard")
st.markdown(
    "Upload a CSV dataset to explore numeric and categorical features, "
    "filter data interactively, visualize distributions and correlations, "
    "and export cleaned data."
)

st.divider()

# File Uploader
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)


    # Dataset Overview
    st.subheader("Dataset Overview")
    st.write(f"**Rows:** {df.shape[0]}  |  **Columns:** {df.shape[1]}")

    with st.expander("Preview Data"):
        n_rows = st.slider(
            "Number of rows to preview",
            min_value=5,
            max_value=min(100, df.shape[0]),
            value=10
        )
        st.dataframe(df.head(n_rows), use_container_width=True)

    st.divider()


    # Sidebar Controls
    st.sidebar.title("Controls")

    # Numeric columns
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        st.sidebar.header("Numeric Analysis")
        num_column = st.sidebar.selectbox("Select numeric column", numeric_cols)
        min_val = float(df[num_column].min())
        max_val = float(df[num_column].max())
        selected_range = st.sidebar.slider(
            f"Filter {num_column} range",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )

        # Filtered data
        filtered_df = df[
            (df[num_column] >= selected_range[0]) &
            (df[num_column] <= selected_range[1])
        ]
        st.write(f"Filtered rows: {filtered_df.shape[0]}")
    else:
        filtered_df = df.copy()
        st.sidebar.warning("No numeric columns found for filtering.")

    # Categorical columns
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
    if len(cat_cols) > 0:
        st.sidebar.header("Categorical Analysis")
        cat_column = st.sidebar.selectbox("Select categorical column", cat_cols)
    else:
        cat_column = None
        st.sidebar.info("No categorical columns found.")

    st.divider()

    # Numeric Visualizations
    if len(numeric_cols) > 0:
        st.subheader(f"Numeric Analysis: {num_column}")

        col1, col2 = st.columns(2)
        with col1:
            fig_hist = px.histogram(
                filtered_df,
                x=num_column,
                title=f"Histogram of {num_column}"
            )
            fig_hist.update_layout(title_x=0.5, bargap=0.1)
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            fig_box = px.box(
                filtered_df,
                y=num_column,
                title=f"Boxplot of {num_column}"
            )
            fig_box.update_layout(title_x=0.5)
            st.plotly_chart(fig_box, use_container_width=True)

        st.caption(
            "Use the slider in the sidebar to filter the numeric column. "
            "Charts update dynamically based on your selection."
        )

        st.divider()

        # Correlation heatmap
        if len(numeric_cols) >= 2:
            st.subheader("Correlation Heatmap (Numeric Columns)")
            corr_matrix = filtered_df[numeric_cols].corr()
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                title="Correlation Matrix"
            )
            fig_corr.update_layout(title_x=0.5)
            st.plotly_chart(fig_corr, use_container_width=True)
            st.caption("Values closer to ±1 indicate stronger linear relationships.")
        else:
            st.info("At least two numeric columns are required for correlation analysis.")

    # Categorical Analysis
    if cat_column is not None:
        st.subheader(f"Categorical Analysis: {cat_column}")
        value_counts = filtered_df[cat_column].value_counts().reset_index()
        value_counts.columns = [cat_column, "Count"]
        st.dataframe(value_counts, use_container_width=True)

        fig_bar = px.bar(
            value_counts,
            x=cat_column,
            y="Count",
            title=f"Distribution of {cat_column}"
        )
        fig_bar.update_layout(title_x=0.5)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("Displays the frequency of each category.")

    # Download Filtered Data
    st.subheader("Download Filtered Data")
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered dataset as CSV",
        data=csv_data,
        file_name="filtered_data.csv",
        mime="text/csv"
    )

    # About Section
    with st.expander("About this App"):
        st.write(
            "This dashboard is built using Python, pandas, and Streamlit to "
            "support interactive exploratory data analysis. Users can upload "
            "CSV datasets, filter numeric columns, analyze distributions, "
            "explore correlations, and export cleaned data."
        )

else:
    st.info("Please upload a CSV file to begin.")
