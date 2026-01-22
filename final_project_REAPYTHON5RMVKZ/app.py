import streamlit as st 
import pandas as pd
import os
import math

# ===============================
# OOP: CLASS
# ===============================
class MovieRecommender:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

    def get_genres(self):
        genres = set()
        for g in self.df['Genre']:
            for genre in g.split(','):
                genres.add(genre.strip())
        return sorted(genres)

    def filter_movies(self, genres, rating, search_query):
        data = self.df.copy()

        # Filter genre
        selected_genres = [g for g in genres if g != "All"]
        if selected_genres:
            pattern = "|".join(selected_genres)
            data = data[data["Genre"].str.contains(pattern, case=False, na=False)]

        # Filter rating
        if rating > 0:
            data = data[
                (data["Rating"] >= rating) &
                (data["Rating"] < rating + 1)
            ]

        # Filter search 
        if search_query:
            data = data[data["Title"].str.lower().str.contains(search_query.lower(), na=False)]

        return data.sort_values(
            by=["Year", "Rating"],
            ascending=[False, False]
        )


# ===============================
# STREAMLIT UI
# ===============================
def main():
    st.set_page_config("Movie Recommendation App", layout="wide")

    st.title("🎬 Sistem Rekomendasi Film Interaktif")
    st.write(
        "Jelajahi 1000 film berdasarkan **genre**, **rating**, dan **judul**"
    )

    BASE_DIR = os.path.dirname(__file__)
    CSV_PATH = os.path.join(BASE_DIR, "assets", "movies.csv")

    try:
        recommender = MovieRecommender(CSV_PATH)
    except FileNotFoundError:
        st.error("⚠️ File 'movies.csv' tidak ditemukan di folder assets. Pastikan file sudah diunggah!")
        st.stop() # Menghentikan aplikasi agar tidak error di baris bawahnya

    

    # ===============================
    # SESSION STATE INIT
    # ===============================
    if "results" not in st.session_state:
        st.session_state.results = recommender.df
        st.session_state.page = 1
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    # ===============================
    # FUNCTION APPLY FILTER 
    # ===============================
    def apply_filter():
        selected_genres = st.session_state.selected_genres
        
        st.session_state.results = recommender.filter_movies(
            genres=selected_genres,
            rating=-1,  
            search_query=st.session_state.get("search_query", "")
        )
        st.session_state.page = 1

    # ===============================
    # SIDEBAR
    # ===============================
    st.sidebar.header("🎯 Preferensi")

    genres = st.sidebar.multiselect(
        "Pilih Genre",
        ["All"] + recommender.get_genres(),
        default=["All"],
        key="selected_genres",
        on_change=apply_filter  
    )

    rating = st.sidebar.slider(
        "Rating Target ⭐",
        min_value=1,
        max_value=10,
        value=7,
        key="rating"
    )

    if st.sidebar.button("🎬 Rekomendasikan"):
        st.session_state.results = recommender.filter_movies(
            genres=st.session_state.selected_genres,
            rating=rating,
            search_query=st.session_state.get("search_query", "")
        )
        st.session_state.page = 1

    st.sidebar.caption(
        "💡 Filter genre otomatis. Klik **Rekomendasikan** untuk terapkan rating"
    )

    # ===============================
    # SEARCH (HALAMAN UTAMA)
    # ===============================
    st.subheader("🔍 Cari Film")
    search_query = st.text_input(
        "Ketik judul film",
        placeholder="Contoh: Avengers, Batman, Zootopia...",
        key="search_query"
    )

    # Jika ada query pencarian, lakukan filter
    if search_query:
        st.session_state.results = recommender.filter_movies(
            genres=st.session_state.selected_genres,
            rating=-1,
            search_query=search_query
        )
        st.session_state.page = 1

    results = st.session_state.results

    if results.empty:
        st.warning("❌ Film tidak ditemukan.")
        return

    # ===============================
    # PAGINATION
    # ===============================
    per_page = 12
    total_pages = math.ceil(len(results) / per_page)

    page = st.number_input(
        "Halaman",
        min_value=1,
        max_value=total_pages,
        value=st.session_state.page
    )

    st.session_state.page = page

    start = (page - 1) * per_page
    end = start + per_page
    page_data = results.iloc[start:end]

    st.caption(f"🎞️ Total film ditemukan: {len(results)}")

    # ===============================
    # Tampilan card film
    # ===============================
    cols = st.columns(3)
    for idx, (_, row) in enumerate(page_data.iterrows()):
        with cols[idx % 3]:
            st.markdown(
                f"""
<div style="
    background:#111;
    color:#EBD3B0;
    border:2px solid #EBD3B0;
    border-radius:16px;
    padding:18px;
    margin-bottom:20px;
    min-height:260px;
">
    <h4>🎬 {row['Title']}</h4>
    <small>
        📅 {row['Year']} | ⭐ {row['Rating']} | ⏱️ {row['Runtime (Minutes)']} Minutes
    </small>
    <p><b>Genre:</b> {row['Genre']}</p>
    <p><b>Director:</b> {row['Director']}</p>
    <p style="font-size:13px;">
        {str(row['Description'])[:140]}...
    </p>
</div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
