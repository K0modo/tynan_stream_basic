import streamlit as st
from functions.data_app_calculations import ClaimData, ICDGroupData, SpecialtyGroupData, ICDData
from functions import graphs_app as graphs
import functions.data_settings as ds

st.set_page_config(
    page_title="Tynan Member Dashboard",
    page_icon=':bar_chart:',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>

.st-emotion-cache-434r0z {
    padding-top:2rem;
    padding-bottom:2rem;
}

.st-emotion-cache-wyrmhr {
    padding-top:0;
    padding-bottom:0;
}

</style>
""", unsafe_allow_html=True)


# DATA LOADER
#######################################################################################

conn = st.connection('test_database', type='sql')


@st.cache_data
def fetch_claim_data():
    db_query = "Select * from claim_data"
    result = conn.query(db_query)

    return result


@st.cache_data
def fetch_annual_member_count():
    db_query = "Select Count(DISTINCT mem_acct_id) from group_table"
    result = conn.query(db_query)

    return result


@st.cache_data
def fetch_period_member_count():
    db_query = "Select * from period_member_count"
    result = conn.query(db_query)
    result = result.set_index('period')

    return result


@st.cache_data
def fetch_icd_racing():
    db_query = "Select * from icd_racing"
    result = conn.query(db_query)
    table_title = 'Injury_Disease'
    figure = graphs.make_icd_racing_chart(result, table_title)

    return figure


@st.cache_data
def fetch_specialty_racing():
    db_query = "Select * from specialty_racing"
    result = conn.query(db_query)
    table_title = 'Provider Specialty'
    figure = graphs.make_icd_racing_chart(result, table_title)

    return figure


@st.cache_data
def fetch_group_table():
    db_query = "Select * from group_table"
    result = conn.query(db_query)

    return result


@st.cache_data
def fetch_heatmap_data():
    heatmap_data = fetch_group_table()
    heatmap_data = heatmap_data[heatmap_data['specialty_id'] != 209]
    figure = graphs.make_icd_spec_heatmap(heatmap_data)

    return figure


# LAYOUT SECTION
#######################################################################################

col = st.columns((1,3,1))
with col[1]:
    st.markdown("<header style='text-align: center; font-family:verdana; font-size:26px; color:white; "
                "border:2px solid gray; border-top-left-radius:35px; border-top-right-radius:35px; "
                "background-color:#007bc0'>James C. "
                "Mattingly</header>",
                unsafe_allow_html=True)

col = st.columns((1,3,1))
with col[1]:
    st.markdown("<header style='text-align: center; font-family:verdana; font-size:26px; color:white; "
                "border:2px solid gray; border-bottom-left-radius:35px; border-bottom-right-radius:35px;"
                "background-color:#007bc0'>Tynan Analytics Dashboard</header>",
                unsafe_allow_html=True)
#F7F00C Yellow  #007bc0 Blue
st.markdown("")
st.markdown("")
st.markdown("<h2 style='text-align: center'>Summary of Healthcare Insurance Claims</h2>", unsafe_allow_html=True)
st.markdown("")

# ROW
#######################################################################################

col = st.columns((2, 2, 2, 2, 2))

with col[0]:
    annual_stats = fetch_claim_data()
    annual_data = ClaimData(annual_stats, ds.CURRENT_PERIOD)

    st.markdown("Metric:")
    st.markdown("YTD:")
    st.markdown("")

with col[1]:
    st.markdown("Claims Processed")
    st.markdown(f'{annual_data.a_claims:,}')
    st.markdown("")

with col[2]:
    st.markdown("Claim Charges")
    st.markdown(f'$ {annual_data.a_paid:,.0f}')
    st.markdown("")

with col[3]:
    st.markdown("Average Charges")
    st.markdown(f'$ {annual_data.a_ave_per_claim:,.2f}')
    st.markdown("")

with col[4]:
    a_members = fetch_annual_member_count()

    st.markdown("Members")
    st.markdown(f'{a_members.iloc[0, 0]:,}')
    st.markdown("")

st.markdown("")
st.markdown("")

# ROW
#######################################################################################

col = st.columns(8)

with col[0]:
    select_period = st.selectbox("Select Period:", ds.PERIOD_LIST)

# ROW
#######################################################################################

col = st.columns((2, 2, 2, 2, 2))

with col[0]:
    st.markdown("Current Period:")
    st.markdown(f'Select Period: {select_period}')
    st.markdown("Difference")

with col[1]:
    p_claims = annual_data.get_select_claims(select_period)
    fig = graphs.claims_indicator(annual_data.c_claims, p_claims)

    st.markdown(f'{annual_data.c_claims:,}')
    st.markdown(f'{p_claims:,}')
    st.plotly_chart(fig, use_container_width=False)

with col[2]:
    p_paid = annual_data.get_select_paid(select_period)
    fig = graphs.paid_indicator(annual_data.c_paid, p_paid)

    st.markdown(f'$ {annual_data.c_paid:,.0f}')
    st.markdown(f'$ {p_paid:,.0f}')
    st.plotly_chart(fig, use_container_width=False)

with col[3]:
    p_average = p_paid / p_claims
    fig = graphs.average_indicator(annual_data.c_ave_per_claim, p_average)

    st.markdown(f'$ {annual_data.c_ave_per_claim:,.2f}')
    st.markdown(f'$ {p_average:,.2f}')
    st.plotly_chart(fig, use_container_width=False)

with col[4]:
    a_members = fetch_annual_member_count()
    member_stats = fetch_period_member_count()
    c_member = member_stats.loc[ds.CURRENT_PERIOD, 'daily_member_sum']
    p_member = member_stats.loc[select_period, 'daily_member_sum']
    fig = graphs.member_indicator(c_member, p_member)

    st.markdown(f'{c_member}')
    st.markdown(f'{p_member}')
    st.plotly_chart(fig, use_container_width=False)

st.markdown("---")
st.markdown("")
st.markdown("<h3 style='text-align: center'>Insurance Claim Charts & Tables</h3>", unsafe_allow_html=True)
st.markdown("")

# ROW
#######################################################################################

###  RACING CHARTS

with st.expander("TOP 10 CLAIMS PROCESSED"):

    col = st.columns((4, 0.5, 4))

    with col[0]:
        icd_racing_chart = fetch_icd_racing()
        st.plotly_chart(icd_racing_chart, use_container_width=True)

    with col[2]:
        specialty_racing_chart = fetch_specialty_racing()
        st.plotly_chart(specialty_racing_chart, use_container_width=True)

st.markdown("")

### ICD Table

with st.expander("INJURY/DISEASE TABLE (Sort Columns)"):
    col = st.columns([2, 7, 1])

    with col[1]:
        main_query = fetch_group_table()

        query_group = ICDGroupData(main_query)

        query_final = query_group.build_icd_table()

        st.dataframe(query_final,
                     column_config={
                         'icd_name': "Injury or Disease",
                         'Average': st.column_config.NumberColumn(format="%.2f"),

                         'icd_chart_data': st.column_config.BarChartColumn(
                             "Prior Periods",
                             y_min=0,
                             y_max=200
                         )
                     },
                     hide_index=True)

st.markdown("")

# ROW
#######################################################################################

### SPECIALTY Table

with st.expander("PROVIDER SPECIALTY TABLE (Sort Columns)"):
    col = st.columns([2, 7, 1])
    query_group = SpecialtyGroupData(main_query)

    with col[1]:

        query_final = query_group.build_specialty_table()

        st.dataframe(query_final,
                     column_config={
                         'specialty_name': "Provider Specialty",
                         'Average': st.column_config.NumberColumn(format="%.2f"),
                         'specialty_chart_data': st.column_config.BarChartColumn(
                             "Prior Periods",
                             y_min=0,
                             y_max=200
                         )
                     },
                     hide_index=True)

st.markdown("")

# ROW
#######################################################################################

with st.expander("HEATMAP"):
    col = st.columns([1, 7, 1])

    with col[1]:
        heatmap_chart = fetch_heatmap_data()
        st.plotly_chart(heatmap_chart, use_container_width=True)

st.markdown("")

# ROW
#######################################################################################

with st.expander("INJURY/DISEASE SELECTION"):

    icd_options = main_query['icd_name'].drop_duplicates().sort_values()

    col = st.columns(5)

    with col[0]:
        choice = st.selectbox('Select an Injury or Disease', icd_options)
        st.markdown("")

        icd_stats = ICDData(main_query, choice)

    col = st.columns((2, 2, 2, 2, 2))

    with col[0]:
        st.markdown("Selection")
        st.markdown(choice)

    with col[1]:
        st.markdown("Claims Processed")
        st.markdown(f'{icd_stats.claims:,}')

    with col[2]:
        st.markdown("Claim Charges")
        st.markdown(f'$ {icd_stats.charges:,.0f}')

    with col[3]:
        st.markdown("Average Charges")
        st.markdown(f'$ {icd_stats.average:,.2f}')

    with col[4]:
        st.markdown("Members")
        st.markdown(f'{icd_stats.get_member_count()}')

    st.markdown("")

    col = st.columns((3, 1, 4))

    with col[0]:
        icd_choices = icd_stats.get_period_claim_count()
        fig = graphs.make_icd_period_bar_chart(icd_choices, choice)
        st.plotly_chart(fig, use_container_width=True)

    with col[2]:
        choice_from_icd_choice = icd_stats.get_specialty_claims()
        fig = graphs.make_icd_specialty_bar_chart(choice_from_icd_choice, choice)
        st.plotly_chart(fig, use_container_width=True)
