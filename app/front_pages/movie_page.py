from turtle import right
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from itertools import cycle, count
import logging
import os

from modules.javdb.javdb import JavDbUtil

logger = logging.getLogger(__name__)


if "current_actor_name" in st.session_state:
    actor_name = st.session_state["current_actor_name"]
else:
    actor_name = os.getenv("current_actor_name")

if "current_actor_id" in st.session_state:
    actor_id = st.session_state["current_actor_id"]
else:
    actor_id = os.getenv("current_actor_id")

if actor_name and actor_id:
    os.environ["current_actor_id"] = actor_id
    os.environ["current_actor_name"] = actor_name
    jav_db = JavDbUtil(os.environ["proxy"])
    if "movie_current_page" not in st.session_state:
        st.session_state.movie_current_page = 1

    movie_tab = st.tabs([f"KK最爱的 {actor_name} 老师"])[0]

    with movie_tab:
        code, movies = jav_db.get_id_details_by_star_id(actor_id, st.session_state.movie_current_page)
        col_cyc = cycle(st.columns(4))
        count_cyc = count()
        for movie in movies:
            # logger.info(movie)
            with next(col_cyc).container(border=True):
                magent = ""
                with st.container(border=False):
                    is_clicked = streamlit_image_coordinates(source=movie.get("img"), use_column_width=True)

                if is_clicked and "磁鏈" in movie.get("tag", ""):
                    code, magent_info = jav_db.get_av_by_javdb_id(movie.get("jav_id"), True, True)
                    if magent_result:=magent_info.get("magnets"):
                        magent = magent_result[0]["link"]

                st.markdown(
                    f':blue[**{movie.get("id")}** {movie.get("title")}]',
                    width="content"
                )
                left, center, right , _ = st.columns([1,1,1,1])
                with left:
                    st.markdown(f'**{movie.get("date")}**')
                with center:
                    st.markdown(f':orange[评分: {movie.get("score", "")}]')
                with right:
                    if movie.get("tag", ""):
                        st.markdown(f':green-background[{movie.get("tag", "")}]')
                if magent:
                    st.markdown(f':green[{magent}]')

        _, pre_page, current_page, next_page, __ = st.columns([1,1,1,1,1])
        with pre_page:
            if st.button("上一页", key="movie_pre_button", disabled=True if st.session_state.movie_current_page==1 else False):
                st.session_state.movie_current_page -= 1
                st.rerun()
        with next_page:
            if st.button("下一页", key="movie_next_button", disabled=True if len(movies)!=40 else False):
                st.session_state.movie_current_page += 1
                st.rerun()
        with current_page:
            st.write(f"当前第 {st.session_state.movie_current_page} 页")

