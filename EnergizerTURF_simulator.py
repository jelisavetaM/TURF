# requirements
import pandas as pd
import streamlit as st
import altair as alt

@st.cache 
def make_id_sets(dataframe):
    sets = []
    for (column_name,data) in dataframe.iteritems():
        to_set = set(dataframe.index[data == 1])
        sets.append(to_set)
    return sets

@st.cache 	
def calculate_order_percentages(sets,upper_range_loop,dataframe,starting_feature_index):
    percentages, order = reach_percentage_and_order(sets,starting_feature_index,dataframe)
    new_reach = sets[starting_feature_index]

    for i in range(0,upper_range_loop):
        diff=0
        for each_set in sets:
            if len(each_set.difference(new_reach)) > diff:
                diff = len(each_set.difference(new_reach))
                set_to_add = sets.index(each_set)
        order.append(dataframe.columns[set_to_add])
        new_reach = set.union(new_reach,sets[set_to_add])
        percentages.append(len(new_reach)/len(dataframe))
    return order,percentages

@st.cache 
def reach_percentage_and_order(sets,starting_feature_index,dataframe):
    """Initaties two lists, unduplicated reach and feature order  using starting index value and DF"""
    return [((len(sets[starting_feature_index]))/(len(dataframe)))], [dataframe.columns[starting_feature_index]]

# import data
originalTURF = pd.read_csv('Merged.csv')

# Add filters for respondents
with st.sidebar:

    st.markdown("<div style='color:red; font-size:30px; position:absolute; top:-8vh;'>EyeSee TURF simulator</div>", unsafe_allow_html=True)
    st.markdown("#")
    st.markdown("#")
    st.caption("<p style='color: white, font-family: Source Sans Pro, sans-serif'>Select channel:</p>", unsafe_allow_html=True)
    AutoChannel = st.checkbox('Auto Channel', 1)
    Walmart = st.checkbox('Walmart')

    if AutoChannel and not Walmart:
        originalTURF = originalTURF.query('CHANNEL == "AUTO"')
    elif not AutoChannel and Walmart:
        originalTURF = originalTURF.query('CHANNEL == "WALMART"')
    elif not AutoChannel and not Walmart:
        st.error('Please choose at least one channel')
        st.stop()

    st.caption("")

    filters = st.selectbox(
        'Select filter:',
        ('None (Total data)', 'Gender', 'Age'))
    if filters != 'None (Total data)':
        if filters == 'Gender':
            genderFilter = st.radio('Please select gender filter:',('Female', 'Male'))            
            originalTURF = originalTURF.query('GENDER == "' + genderFilter + '"')
        if filters == 'Age':
            ageFilter = st.radio('Please select age filter:',('18-35', '36+'))
            originalTURF = originalTURF.query('AGE == "' + ageFilter + '"')
    st.markdown('#')
    st.markdown('#')
    with st.expander('Instructions'):
        st.markdown("test",unsafe_allow_html = True)
        
allColumns = list(originalTURF.columns)
del allColumns[0:4]

# Choose target SKUs
# Multiselect for SKU per SKU principle
SKUs = st.multiselect(
     'Which SKUs would you like to include in this scenario?',
     allColumns,
     help = "Choose brands by clicking on the input. You can type in SKU name as well.")

# Multiselect for agregated levels (Brand, Example_1, Example_2, etc.)
Brands = st.multiselect(
     'Which BRAND would you like to include in this scenario?',
     ['AXE', 'California Scents', 'Refresh Your Car', 'Jelly Belly', 'Armor All', 'Driven'],
     help = "Choose brands by clicking on the input. You can type in brand name as well.")

if len(SKUs) > 0:
    targetProductsSKU = [col for col in originalTURF.columns if col in SKUs]  
else:
    targetProductsSKU = []

if len(Brands) > 0:
    targetProductsBrand = []
    for Brand in Brands:
        targetProductsBrand = targetProductsBrand + ([col for col in allColumns if Brand in col])
else:
    targetProductsBrand = []

finalTarget = targetProductsSKU + targetProductsBrand

if len(finalTarget) == 0:
    st.error('Please choose SKU and/or BRAND level to run stimulation.')
    st.stop()

calc = st.button('✈ Calculate')

st.markdown('#')

if calc:
    finalTarget.append('USERID')
    originalTURF = originalTURF[[col for col in finalTarget]]
    sets = make_id_sets(originalTURF)
    order, percentages = calculate_order_percentages(sets,44,originalTURF,originalTURF.columns.get_loc(originalTURF.drop(['USERID'], axis=1).sum().idxmax()))

    res = {order[i]: percentages[i] for i in range(len(order))}
    resToDF = pd.DataFrame(res.items(), columns=['SKU','Reach'])
    resToDF = resToDF.sort_values(by=['Reach'])
    resToDF['Increment'] = resToDF['Reach'].diff()
    resToDF['Reach %'] = pd.Series(["{0:.1f}%".format(val * 100) for val in resToDF['Reach']], index = resToDF.index)
    resToDF['Increment'] = pd.Series(["{0:.1f}%".format(val * 100) for val in resToDF['Increment']], index = resToDF.index)
    resToDF['Increment'][0] = "baseline"
    resToDF.reset_index(drop = True)
    resToDFplot = resToDF[['SKU', 'Reach']]
    resToDF = resToDF.drop('Reach', axis = 1)
    resToDF = resToDF[['SKU','Reach %','Increment']]
    # st.write(resToDF.astype(str))
    st.table(resToDF)

    st.markdown('------------------------------')
    st.markdown('#')

    c = alt.Chart(resToDFplot).mark_bar(size=10).encode(
    alt.X('SKU', sort=list(resToDFplot['SKU']), axis=alt.Axis(labelAngle=-75, labelOverlap=False)),
    alt.Y('Reach'),
).configure_mark(
    opacity=0.4,
    color='blue'
).configure_axis(
    grid=False
).configure_view(
    strokeWidth=0
).properties(
    width=800,
    height=600,
    title='Selected SKUs reaches'
)

    # (c + text).properties(height=900)

    st.altair_chart(c, use_container_width=True)
