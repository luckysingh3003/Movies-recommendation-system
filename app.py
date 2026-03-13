import html as _html
import pickle
import faiss
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_KEY = "04cc96b25f83484205af738e1a9b6282"

st.markdown(
    """
<link
  href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap"
  rel="stylesheet">

<style>

*, *::before, *::after {
    box-sizing: border-box;
    margin:     0;
    padding:    0;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.css-15zrgzn {
    display: none !important;
}
a[href^="#"] { display: none !important; }

::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: #090909; }
::-webkit-scrollbar-thumb { background: #E50914; border-radius: 3px; }

[data-testid="stAppViewContainer"] {
    background: #080808;
    background-image: radial-gradient(
        ellipse 80% 50% at 50% -10%,
        rgba(229,9,20,.18) 0%,
        transparent 60%
    );
    min-height:  100vh;
    font-family: 'DM Sans', sans-serif;
    color:       #f0f0f0;
}
[data-testid="stMain"]          { background: transparent !important; }
[data-testid="block-container"] {
    padding:   0 2.5rem 4rem !important;
    max-width: 1400px;
}
 
.search-label {
    font-size:      13px;
    font-weight:    600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color:          rgba(255,255,255,.85);
    margin-bottom:  14px;
}
 
[data-testid="stSelectbox"],
[data-testid="stSelectbox"] > div,
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] > div > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background:    #141414 !important;
    border-color:  rgba(255,255,255,.1) !important;
    color:         #f0f0f0 !important;
    font-family:   'DM Sans', sans-serif !important;
}

[data-testid="stSelectbox"] > div > div {
    border:           1px solid rgba(255,255,255,.1) !important;
    border-radius:    10px !important;
    font-size:        16px !important;
    padding:          10px 14px !important;
    min-height:       52px !important;
    height:           auto !important;
    line-height:      1.5 !important;
    overflow:         visible !important;
    background-color: #141414 !important;
    transition:       border-color .2s, box-shadow .2s !important;
}

[data-testid="stSelectbox"] > div > div:hover,
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #E50914 !important;
    box-shadow:   0 0 0 3px rgba(229,9,20,.15) !important;
}

 
[data-testid="stSelectbox"] * {
    color:                  #f0f0f0 !important;
    -webkit-text-fill-color: #f0f0f0 !important;
    background-color:       transparent !important;
}
[data-testid="stSelectbox"] > div > div {
    background-color: #141414 !important;
}
 
[data-testid="stSelectbox"] svg {
    fill:  rgba(255,255,255,.5) !important;
    color: rgba(255,255,255,.5) !important;
}
 
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background:    #141414 !important;
    border:        1px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] ul,
[role="option"] {
    background: #141414 !important;
    color:      #f0f0f0 !important;
}
[role="option"]:hover,
[data-testid="stSelectbox"] li:hover {
    background: rgba(229,9,20,.18) !important;
}
 
@keyframes pulseBorder {
    0%, 100% { box-shadow: 0 0 0 0   rgba(229,9,20,.4); }
    50%       { box-shadow: 0 0 0 8px rgba(229,9,20,0); }
}
 
.stButton > button {
    background:    linear-gradient(135deg, #E50914, #b30710) !important;
    color:         #fff !important;
    border:        none !important;
    border-radius: 10px !important;
    height:        50px !important;
    padding:       0 36px !important;
    font-family:   'DM Sans', sans-serif !important;
    font-size:     15px !important;
    font-weight:   600 !important;
    margin-top:    16px !important;
    transition:    all .25s ease !important;
    animation:     pulseBorder 2.5s infinite !important;
}
.stButton > button:hover {
    background:  linear-gradient(135deg, #ff1f2e, #E50914) !important;
    transform:   translateY(-2px) !important;
    box-shadow:  0 12px 32px rgba(229,9,20,.45) !important;
}
 
.section-title {
    font-family:    'Bebas Neue', cursive;
    font-size:      32px;
    letter-spacing: 2px;
    color:          #fff;
    margin-bottom:  28px;
}

</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_models():
    movies = pickle.load(open("movies.pkl", "rb"))
    embeddings = pickle.load(open("embeddings.pkl", "rb"))
    index = faiss.read_index("faiss_index.index")
    return movies, embeddings, index


movies, embeddings, index = load_models()


@st.cache_data(ttl=3600)
def fetch_details(movie_id):
    """Fetch poster, backdrop, rating, year, genres and overview from TMDB."""
    try:
        data = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}",
            timeout=5,
        ).json()

        poster = (
            "https://image.tmdb.org/t/p/w500" + data["poster_path"]
            if data.get("poster_path")
            else "https://dummyimage.com/500x750/111/fff&text=No+Poster"
        )
        backdrop = (
            "https://image.tmdb.org/t/p/original" + data["backdrop_path"]
            if data.get("backdrop_path")
            else "https://dummyimage.com/1280x720/111/fff&text=No+Image"
        )
        rating = round(float(data.get("vote_average", 0)), 1)
        year = data.get("release_date", "")[:4] or "N/A"
        genres = [g["name"] for g in data.get("genres", [])[:2]]
        overview = (
            (data.get("overview", "")[:120] + "...") if data.get("overview") else ""
        )

        return poster, backdrop, rating, year, genres, overview

    except Exception:
        return (
            "https://dummyimage.com/500x750/111/fff&text=No+Poster",
            "https://dummyimage.com/1280x720/111/fff&text=No+Image",
            0.0,
            "N/A",
            [],
            "",
        )


def recommend(movie):
    """Return 5 similar movies using FAISS vector search."""
    idx = movies[movies["title"] == movie].index[0]
    _, indices = index.search(embeddings[idx].reshape(1, -1), 6)

    results = []
    for i in indices[0][1:]:
        poster, _, rating, year, _, _ = fetch_details(movies.iloc[i].movie_id)
        results.append(
            {
                "title": movies.iloc[i].title,
                "poster": poster,
                "rating": rating,
                "year": year,
            }
        )
    return results


st.markdown(
    """
<div style="text-align:center; padding:32px 0 8px;">
    <div style="
        font-family: 'Bebas Neue', cursive;
        font-size:   58px;
        letter-spacing: 5px;
        background: linear-gradient(90deg, #fff, #E50914, #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;">
        Movies Recommendation System
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="search-label">&#127916; &nbsp; Choose your movie</div>',
    unsafe_allow_html=True,
)

selected_movie = st.selectbox(
    label="",
    options=sorted(movies["title"].values),
    label_visibility="collapsed",
)

with st.spinner("Loading..."):
    sel_id = movies[movies["title"] == selected_movie].iloc[0].movie_id
    _, hero_bg, hero_rating, hero_year, hero_genres, hero_overview = fetch_details(
        sel_id
    )

safe_title = _html.escape(selected_movie)
safe_overview = _html.escape(hero_overview)

meta = ' <span class="hero-dot">&#9679;</span> '.join(
    filter(
        None,
        [
            hero_year if hero_year != "N/A" else "",
            f"&#9733; {hero_rating}" if hero_rating else "",
        ],
    )
)

badges = " ".join(
    f'<span class="hero-badge">{_html.escape(g)}</span>' for g in hero_genres
)

components.html(
    f"""
<link
  href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap"
  rel="stylesheet">

<style>

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ margin: 0; padding: 0; background: transparent; }}

    @keyframes heroFadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero {{
        position:      relative;
        width:         100%;
        height:        480px;
        border-radius: 16px;
        overflow:      hidden;
        animation:     heroFadeIn .8s ease both;
    }}

    .hero-img {{
        width:            100%;
        height:           100%;
        object-fit:       cover;
        object-position:  center;
        display:          block;
        transition:       transform 8s ease;
    }}
    .hero:hover .hero-img {{ transform: scale(1.04); }}

    .hero-gradient {{
        position:   absolute;
        inset:      0;
        background:
            linear-gradient(to right,
                rgba(8,8,8,.97) 0%,
                rgba(8,8,8,.75) 35%,
                rgba(8,8,8,.15) 65%,
                rgba(8,8,8,.5)  100%
            ),
            linear-gradient(to top,
                rgba(8,8,8,.95) 0%,
                transparent     50%
            );
    }}

    .hero-content {{
        position:             absolute;
        bottom:               0;
        left:                 0;
        padding:              44px 48px;
        width:                60%;
        opacity:              0;
        animation:            heroFadeIn 1s .2s ease both;
        animation-fill-mode:  forwards;
    }}

    .hero-eyebrow {{
        font-family:    'DM Sans', sans-serif;
        font-size:      11px;
        font-weight:    500;
        letter-spacing: 4px;
        text-transform: uppercase;
        color:          #E50914;
        margin-bottom:  10px;
    }}

    .hero-title {{
        font-family:    'Bebas Neue', cursive;
        font-size:      72px;
        line-height:    .95;
        letter-spacing: 2px;
        color:          #fff;
        text-shadow:    0 4px 40px rgba(0,0,0,.8);
        margin-bottom:  16px;
    }}

    .hero-meta {{
        display:        flex;
        align-items:    center;
        gap:            16px;
        margin-bottom:  16px;
        font-family:    'DM Sans', sans-serif;
        font-size:      13px;
        font-weight:    300;
        color:          rgba(255,255,255,.55);
    }}
    .hero-dot {{ color: #E50914; font-size: 6px; }}

    .hero-badge {{
        display:        inline-block;
        padding:        3px 10px;
        border-radius:  4px;
        border:         1px solid rgba(229,9,20,.5);
        background:     rgba(229,9,20,.1);
        color:          #ff8080;
        font-family:    'DM Sans', sans-serif;
        font-size:      11px;
        font-weight:    500;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    .hero-sub {{
        font-family: 'DM Sans', sans-serif;
        font-size:   15px;
        font-weight: 300;
        line-height: 1.6;
        color:       rgba(255,255,255,.6);
        max-width:   420px;
    }}

</style>

<div class="hero">
    <img class="hero-img" src="{hero_bg}" alt="">
    <div class="hero-gradient"></div>
    <div class="hero-content">
        <div class="hero-eyebrow">Now Viewing</div>
        <div class="hero-title">{safe_title}</div>
        <div class="hero-meta">{meta}</div>
        <div style="margin-bottom:14px">{badges}</div>
        <div class="hero-sub">{safe_overview}</div>
    </div>
</div>
""",
    height=490,
    scrolling=False,
)

col_btn, _ = st.columns([1, 5])
with col_btn:
    clicked = st.button("Find Similar")

if clicked:
    with st.spinner("Curating your watchlist..."):
        results = recommend(selected_movie)

    st.markdown(
        '<div class="section-title">Recommended For You</div>',
        unsafe_allow_html=True,
    )

    for rank, (col, r) in enumerate(zip(st.columns(5), results), start=1):
        with col:
            safe_r_title = _html.escape(r["title"])

            components.html(
                f"""
<link
  href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;600&display=swap"
  rel="stylesheet">

<style>

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ margin: 0; background: transparent; }}

    @keyframes cardIn {{
        from {{ opacity: 0; transform: translateY(24px) scale(.97); }}
        to   {{ opacity: 1; transform: translateY(0)    scale(1);   }}
    }}

    .movie-card {{
        position:      relative;
        border-radius: 14px;
        overflow:      hidden;
        background:    #111;
        border:        1px solid rgba(255,255,255,.06);
        cursor:        pointer;
        animation:     cardIn .5s ease both;
        transition:
            transform    .35s cubic-bezier(.34,1.56,.64,1),
            box-shadow   .35s ease,
            border-color .35s ease;
    }}
    .movie-card:hover {{
        transform:    translateY(-6px) scale(1.02);
        box-shadow:   0 24px 60px rgba(0,0,0,.7), 0 0 0 1px rgba(229,9,20,.3);
        border-color: rgba(229,9,20,.3);
    }}

    .card-poster-wrap {{
        position: relative;
        width:    100%;
        height:   320px;
        overflow: hidden;
    }}
    .card-poster-wrap img {{
        width:      100%;
        height:     100%;
        object-fit: cover;
        display:    block;
        transition: transform .5s ease;
    }}
    .movie-card:hover .card-poster-wrap img {{ transform: scale(1.08); }}

    .card-overlay {{
        position:   absolute;
        inset:      0;
        background: linear-gradient(to top, rgba(8,8,8,.6) 0%, transparent 60%);
        opacity:    0;
        transition: opacity .35s ease;
    }}
    .movie-card:hover .card-overlay {{ opacity: 1; }}

    .rank-badge {{
        position:        absolute;
        top:             10px;
        left:            10px;
        width:           28px;
        height:          28px;
        background:      rgba(229,9,20,.9);
        backdrop-filter: blur(4px);
        border-radius:   6px;
        display:         flex;
        align-items:     center;
        justify-content: center;
        font-family:     'Bebas Neue', cursive;
        font-size:       16px;
        color:           #fff;
        z-index:         5;
    }}

    .card-info {{
        padding:    14px 14px 16px;
        border-top: 1px solid rgba(255,255,255,.05);
        background: #111;
    }}

    .card-title {{
        font-family:   'DM Sans', sans-serif;
        font-size:     14px;
        font-weight:   600;
        color:         #f0f0f0;
        line-height:   1.3;
        margin-bottom: 6px;
        white-space:   nowrap;
        overflow:      hidden;
        text-overflow: ellipsis;
    }}

    .card-rating-row {{
        display:         flex;
        align-items:     center;
        justify-content: space-between;
        font-family:     'DM Sans', sans-serif;
        font-size:       13px;
        margin-top:      4px;
    }}

    .rating-number {{ color: #FFD700; font-weight: 600; }}
    .card-year     {{ color: rgba(255,255,255,.4); font-weight: 300; }}

</style>

<div class="movie-card">
    <div class="card-poster-wrap">
        <img src="{r['poster']}" alt="">
        <div class="rank-badge">{rank}</div>
        <div class="card-overlay"></div>
    </div>
    <div class="card-info">
        <div class="card-title">{safe_r_title}</div>
        <div class="card-rating-row">
            <div class="rating-number">&#9733; {r['rating']}</div>
            <div class="card-year">{r['year']}</div>
        </div>
    </div>
</div>
""",
                height=390,
                scrolling=False,
            )
