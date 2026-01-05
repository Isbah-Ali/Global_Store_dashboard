import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(layout="wide")
main, space = st.columns([0.9, 0.1])

df = pd.read_csv("superstore_dataset.csv", encoding = "latin1")

with main:
    st.title("Global Store dashboard")

with space:
    csv_data = df.to_csv()
    st.download_button("Download Dataset", file_name="superstore_dataset.csv", data = csv_data.encode("latin1"))

st.markdown("""<br>""", unsafe_allow_html=True)


st.sidebar.markdown("**Filter The Data By your own choice:**")

region = st.sidebar.multiselect("Select Region", df["Region"].unique(), default = df["Region"].unique()) 
category = st.sidebar.multiselect("Select Category", df["Category"].unique(), default = df["Category"].unique()) 
sub_category = st.sidebar.multiselect("Select Sub-Category", df["Sub-Category"].unique(), default = df["Sub-Category"].unique()) 

df_filtered = df[(df["Region"].isin(region)) & (df["Category"].isin(category)) & (df["Sub-Category"].isin(sub_category))]

if not region and not category and not sub_category:
    df_filtered = df
elif not region and not category:
    df_filtered = df[df["Sub-Category"].isin(sub_category)]
elif not region and not sub_category:
    df_filtered = df[df["Category"].isin(category)]
elif not category and not sub_category:
    df_filtered = df[df["Region"].isin(region)] 
elif not region:
    df_filtered = df[df["Category"].isin(category) & df["Sub-Category"].isin(sub_category)]
elif not category:
    df_filtered = df[df["Region"].isin(region) & df["Sub-Category"].isin(sub_category)]
elif not sub_category:
    df_filtered = df[df["Region"].isin(region) & df["Category"].isin(category)]


total_sales = df_filtered["Sales"].sum()
total_profit = df_filtered["Profit"].sum()
top_5_cutomers = df_filtered.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(5)

col1, col2 = st.columns(2)
col1.metric("💰 Total Sales", f"${total_sales:,.2f}") # Adds a comma as a thousands seperator, .2f means rounding off to 2
col2.metric("📈 Total Profit", f"{total_profit:,.2f}")



col3, col4, col5 = st.columns([0.37, 0.25, 0.37])
# Sales By Region Chart
with col3:
    st.markdown("""<br>""", unsafe_allow_html=True)
    st.subheader("Which regions generate the most revenue?")
    Revenue_Per_Region = df_filtered.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    st.bar_chart(data = Revenue_Per_Region, color= "#068B37EE", width = 500, height =400, use_container_width=True)

# Which category has the most sales?
with col4:
    st.markdown("""<br>""", unsafe_allow_html=True)
    st.subheader("Which category has the most sales?")
    Sales_per_category = df_filtered.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    st.bar_chart(data = Sales_per_category, width = 450, height =400, color= "#055E3A", use_container_width=True)

# Which sub-category has the most sales?#046D43
with col5:
    st.markdown("""<br>""", unsafe_allow_html=True)
    st.subheader("Which sub-Category has the most sales?")
    Sales_per_subcategory = df_filtered.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False)
    st.bar_chart(data = Sales_per_subcategory, width = 500, height =400, color= "#068B37EE", horizontal=True, use_container_width=True)

st.subheader("Comparison Of Sales with Profit")
col6, col7 = st.columns([0.6, 0.4])

# REGION WISE
with col6:
    region_summary = (
        df_filtered.groupby("Region")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        region_summary,
        x="Region",
        y=["Sales", "Profit"],
        barmode="group",
        title="Sales vs Profit BY REGION",
        color_discrete_map={
        "Sales": "#1F4E79",   # Blue for Sales
        "Profit": "#2E8B57"   # Green for Profit
    }
    )

    st.plotly_chart(fig, use_container_width=True, key = "chart1")

# CATEGORY WISE
with col7:
    category_summary = (
        df_filtered.groupby("Category")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        category_summary,
        x="Category",
        y=["Sales", "Profit"],
        barmode="group",
        title="Sales vs Profit BY CATEGORY",
        color_discrete_map={
        "Sales": "#1F4E79",   # Blue for Sales
        "Profit": "#2E8B57"   # Green for Profit
    }
    )

    st.plotly_chart(fig, use_container_width=True, key = "chart2")

st.divider()

# Top 5 customers:
col8, col9 = st.columns(2)
with col8:
    st.subheader("Top 5 Customers")
    st.bar_chart(top_5_cutomers, color= "#068B37EE", width = 450)
 
    option = st.selectbox("Select how many customer's details you want to know ", ("Top 5 Customers", "All Customers") )
    expander = st.expander(" Customers: Names and Sales")
    expander_details = df_filtered[["Customer Name", "Sales"]].groupby("Customer Name")["Sales"].sum().sort_values(ascending=False)
    if option == "Top 5 Customers":
        expander.write(expander_details.head(5))
    if option == "All Customers":
        expander.write(expander_details)
#with col9:
    

st.divider()

# Shipping Delay Plotting
df["Order Date"] = pd.to_datetime(df["Order Date"], format = "mixed", dayfirst = True)
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format = "mixed", dayfirst = True)
df["Shipping Delay"] =  (df["Ship Date"] - df["Order Date"]).dt.days

print(df.groupby("Ship Mode")["Shipping Delay"].agg({max, min}))

st.subheader("Average Delivery Time By Shipping Mode")
col10, col11, col12 = st.columns([0.5,0.1, 0.3])

with col10:
    fig1, ax1 = plt.subplots(figsize = (8,5))
    sns.scatterplot(x = df["Ship Mode"], y = df["Shipping Delay"], ax = ax1)
    st.pyplot(fig1)

with col12:
    delivery_time= df.groupby("Ship Mode")["Shipping Delay"].agg({max, min}).reset_index()
    fig_delivery_time = px.bar(
        delivery_time,
        x="Ship Mode",
        y=["max", "min"],
        barmode="group",
        title="MAX AND MIN DAYS FOR EACH SHIPPING MODE",
        color_discrete_map={
        "max": "#1F4E79",   # Blue for Sales
        "min": "#2E8B57"   # Green for Profit
    }
    )
    st.plotly_chart(fig_delivery_time, use_container_width=True, key = "delivery_time")
   

col13, space_col, col14 = st.columns([0.4, 0.2, 0.4])
with col13:
    st.subheader("Shipping Mode And Their Average Costs")
    shipping_cost_avg = df.groupby("Ship Mode")["Shipping Cost"].mean()
    st.bar_chart(
        data = shipping_cost_avg, 
        width = 250, height =400, 
        color = "#00008B", 
        x_label="Shipping Mode",
        y_label="Shipping Cost Average",        
        use_container_width=True
        )
    
with col14:
    shipping_profit = (
    df_filtered.groupby("Ship Mode")["Profit"]
    .sum()
    .reset_index()
    )

    fig = px.pie(
        shipping_profit,
        names="Ship Mode",
        values="Profit",
        hole=0.5,
        title="💰 PROFIT CONTRIBUTION BY SHIPPING MODE"
    )

    fig.update_traces(
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Profit: %{value:,.0f}<br>Share: %{percent}"
    )

    st.plotly_chart(fig, use_container_width=True)

# Average Shipping Delay By Month

df["Order Month"] = df["Order Date"].dt.to_period("M").astype(str)
df["Month"] = df["Order Date"].dt.month
df["Year"] = df["Order Date"].dt.year
print(df["Year"])
print(df["Year"].nunique())

col15, col16 = st.columns([0.8, 0.2])

with col16:
    year = st.multiselect("Select Year", df["Year"].unique(), default = df["Year"].unique())
    df_year = df[df["Year"].isin(year)]
    if not year: 
        df_year = df

with col15:
    avg_delay_month = df_year.groupby("Month")["Shipping Delay"].mean().reset_index()
    fig_delay  = px.line(avg_delay_month, x = "Month", y = "Shipping Delay", markers=True, title="AVERAGE SHIPPING DELAY BY MONTH" )

    fig_delay.update_traces(
    line=dict(color="rgba(6,139,55,0.93)", width=3),
    marker=dict(color="rgba(255, 0, 0, 1)", size=8)
    )       
    fig_delay.update_layout(
        xaxis_title = "Month",
        yaxis_title = "Shipping days"
    )

    max_delay = df_year.groupby("Month")["Shipping Delay"].mean().sort_values(ascending=False).reset_index()
    month_max_delayed = max_delay.iloc[0,0]

    st.plotly_chart(fig_delay, width="stretch", key = "avg_delay_month")
    st.caption(f"The above graph shows most of the delivery delays are in :red[Month {month_max_delayed}]")
