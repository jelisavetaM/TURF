# requirements
import pandas as pd
import streamlit as st
import altair as alt

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

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

@st.cache 
def readData(df):
    originalTURF = pd.read_csv(df)
    return originalTURF

@st.cache
def defineTurfdata(df, ch):
	if ch == "Auto Channel":
		df = df.query('CHANNEL == "AUTO"')  
		df = df.loc[:, 'USERID':'Armor All Freshfx Smoke Destroyer Vent Clip Air Freshener 3 24']
		brand_list = ["Refresh Your Car","Little Trees","Febreze","California Scents","Yankee Candle","AXE","Arm Hammer","Ozium","Scent Bomb","Scents","Driven","Armor All","Chemical Guys","Stoner","Jelly Belly","Type S","Keystone","Lethal Threat","Oxi Clean","Paradise","Blessed","Mothers"]
	elif ch == "Walmart":
		df = df.query('CHANNEL == "WALMART"')
		df = df.drop(df.loc[:, 'Arm Hammer Hidden Cabana Breeze car air freshener 2 5 oz 4 99':'Yankee Candle Vent Stick Pink Sands 6 49'].columns,axis = 1)
		brand_list = ["Armor All ","AXE","California Scents","Citrus Magic","Driven","Febreze","Funkaway","Jelly Belly","Little Trees","Ozium","Refresh Your Car","Scent Bomb","Yankee"]
	return [df, brand_list]
@st.cache
def designDF(df):
	df = pd.DataFrame(res.items(), columns=['SKU','Reach'])
	df = df.sort_values(by=['Reach'])
	df['Increment'] = df['Reach'].diff()
	df['Reach %'] = pd.Series(["{0:.1f}%".format(val * 100) for val in df['Reach']], index = df.index)
	df['Increment'] = pd.Series(["{0:.1f}%".format(val * 100) for val in df['Increment']], index = df.index)
	df['Increment'][0] = "baseline"
	df.reset_index(drop = True)
	dr_plot = df[['SKU', 'Reach']]
	df = df.drop('Reach', axis = 1)
	df = df[['SKU','Reach %','Increment']]
	df.drop(df[df['SKU'] == "USERID"].index, inplace = True)	
	return 	[df, dr_plot]

@st.cache(suppress_st_warning=True)
def login():
	holderPass = st.empty()
	holder = st.empty()
	password = holderPass.text_input("Enter a password:", type="password")	
	if password == "ENR TURF":
		holderPass.empty()
		originalTURF_temp = holder.file_uploader("Upload a TURF CSV file", accept_multiple_files=False)
		if originalTURF_temp is not None:
			originalTURF = readData(originalTURF_temp)
			holder.empty()
		else:
			st.error("Please upload TURF data file.")
			originalTURF = 0
	elif password == "":
		password = "error"
		st.error("Please enter the password.")
		st.stop()
	elif password != "ENR TURF":
		password = "error"
		st.error("Password is not correct.")
		st.stop()
	return originalTURF
	
with st.sidebar:
    st.markdown("<div style='color:#ff4b4b; font-size:30px; position:absolute; top: -8vh;'>EyeSee TURF simulator<br><p style='color:white'>Air Freshener Product Optimization project</p></div>", unsafe_allow_html=True)
with st.container():
    originalTURF_temp = login()
    with st.sidebar:
        st.markdown("#")
        st.markdown("#")
        st.caption("<p style='color: white, font-family: Source Sans Pro, sans-serif'>Select channel:</p>", unsafe_allow_html=True)
        channel = st.radio("Select channel:", ('Auto Channel', 'Walmart'))
        [originalTURF,brand_list] = defineTurfdata(originalTURF_temp, channel)
        st.caption("")
	
    allColumns = list(originalTURF.columns)
    del allColumns[0:2]

	# Choose target SKUs
	# Multiselect for SKU per SKU principle
    SKUs = st.multiselect(
		 'Which SKUs would you like to include in this scenario? Choose from the list or type in SKU names.',
		 allColumns,
		 help = "Choose brands by clicking on the input. You can type in SKU name as well.")

	# Multiselect for agregated levels (Brand, Example_1, Example_2, etc.)
    Brands = st.multiselect(
		 'Which BRAND would you like to include in this scenario? Choose from the list or type in brand names.',
		 brand_list,
		 help = "Choose brands by clicking on the input. You can type in brand name as well.")

    allSKUs = st.checkbox('Include all SKUs in the stimulation')

    if allSKUs:
        finalTarget = list(originalTURF.columns)
    else:
        if len(SKUs) > 0:
            targetProductsSKU = [col for col in originalTURF.columns if col in SKUs]  
        else:
            targetProductsSKU = []

        if len(Brands) > 0:
            targetProductsBrand = []
            for Brand in Brands:
                targetProductsBrand = targetProductsBrand + ([col for col in allColumns if Brand.lower() in col.lower()])
        else:
            targetProductsBrand = []

        finalTarget = targetProductsSKU + targetProductsBrand

    finalTarget = list(set(finalTarget))
    if len(finalTarget) == 0:
        st.error('Please choose SKU and/or BRAND level to run stimulation.')
        st.stop()
    if len(finalTarget) == 1:
        st.error('TURF cannot be run on one item, please add at least one more.')
        st.stop()


    if 'CHANNEL' in originalTURF.columns:
        originalTURF = originalTURF.drop('CHANNEL', axis=1)
    if 'CHANNEL' in finalTarget:
        finalTarget.remove('CHANNEL')

    calc = st.button('✈ Calculate')
    st.markdown('#')

    if calc:
        finalTarget.append('USERID')
        originalTURF = originalTURF[[col for col in finalTarget]]
        sets = make_id_sets(originalTURF)
        order, percentages = calculate_order_percentages(sets,125,originalTURF,originalTURF.columns.get_loc(originalTURF.drop(['USERID'], axis=1).sum().idxmax()))
		
        res = {order[i]: percentages[i] for i in range(len(order))}
        [resToDF, resToDFplot] = designDF(originalTURF)
        st.table(resToDF)

        st.download_button(
			label="Download TURF data to CSV",
			data=resToDF.to_csv().encode('utf-8'),
			file_name="ENR_TURF_data.csv",
			mime="text/csv"
		)
        st.markdown('------------------------------')
        st.markdown('                                                              Selected SKUs reaches')
		

        c = alt.Chart(resToDFplot).mark_bar().encode(
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
		height=580
	)

		# (c + text).properties(height=900)

        st.altair_chart(c, use_container_width=True)
