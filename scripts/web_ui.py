import streamlit as st
import requests

def post_result(response):
    results = response.json()
    st.write(f"Found {results['count']} listings in {response.elapsed.total_seconds()} seconds")
    for listing in results['results']:
        st.subheader(listing[0]['L_Address'])
        st.write(f"Price: ${listing[0]['price']:,}")
        summary = requests.post("http://localhost:8000/summarize", params={'remarks': listing[0]['remarks']}).json()
        st.write(summary['summary'])
        with st.expander("Full description", icon=":material/keyboard_arrow_down:"):
            st.write(listing[0]['remarks'])
        st.write("---")

st.set_page_config(
    layout="wide",
)
st.title("🏡 Real Estate Intelligent Search")

query = st.text_input("What are you looking for?", "3 bed 2 bath under 700k in Irvine")
top_k = st.slider("Maximum number of results", 1, 10, 5)

col1_search, col2_compare = st.columns(2)

with col1_search:
    search = st.button("Search",type='primary')
    option = st.selectbox('Search type', ['Semantic', 'BM25'])
    filters = st.checkbox('Filters')

with col2_compare:
    compare = st.button("Compare Engines",type='primary')

if search:
    if (option == 'semantic'):
        response = requests.post("http://localhost:8000/semantic_search", json={"query": query, "top_k": top_k, "filters": filters})
    else:
        response = requests.post("http://localhost:8000/BM25_search", json={"query": query, "top_k": top_k, "filters": filters})

    st.write("---")
    post_result(response)

if compare:
    semantic_results = requests.post("http://localhost:8000/semantic_search", json={"query": query, "top_k": top_k, "filters": False})
    semantic_results_filtered = requests.post("http://localhost:8000/semantic_search", json={"query": query, "top_k": top_k, "filters": True})
    BM25_results = requests.post("http://localhost:8000/BM25_search", json={"query": query, "top_k": top_k, "filters": False})
    BM25_results_filtered = requests.post("http://localhost:8000/BM25_search", json={"query": query, "top_k": top_k, "filters": True})

    st.write("---")

    sem, bm25, sem_filtered, bm25_filtered = st.columns(4, border=True)

    with sem:
        st.header("semantic")
        post_result(semantic_results)

    with sem_filtered:
        st.header("semantic + filters")
        post_result(semantic_results_filtered)

    with bm25:
        st.header("bm25")
        post_result(BM25_results)

    with bm25_filtered:
        st.header("bm25 + filters")
        post_result(BM25_results_filtered)

        