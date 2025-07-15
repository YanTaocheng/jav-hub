import streamlit as st
from itertools import cycle, count
from streamlit_option_menu import option_menu
from streamlit_image_coordinates import streamlit_image_coordinates
import logging
import os

from modules.javdb.javdb import JavDbUtil
from schemas.javdb import JavActor

logger = logging.getLogger(__name__)

@st.cache_data
def recommanded_acotrs() -> dict[str, list[JavActor]]:
    jav_db = JavDbUtil(os.environ["proxy"])
    actors = jav_db.get_recommanded_actors()
    return actors

actor_type_map = {
    "有码": "censored",
    "无码": "uncensored",
    "欧美":  "western"
}
@st.cache_data
def get_sorted_actors(actor_type: str, page: int = 1) -> list[JavActor]:
    jav_db = JavDbUtil(os.environ["proxy"])
    actors = jav_db.get_actors_by_type(actor_type_map.get(actor_type), page)
    return actors

@st.cache_data
def search_actors(search_content: str) -> list[JavActor]:
    jav_db = JavDbUtil(os.environ["proxy"])
    actors = jav_db.fuzzy_search_stars(search_content)
    return actors

def switch_movie_page(actor_info: JavActor):
    st.session_state["current_actor_id"] = actor_info.id
    st.session_state["current_actor_name"] = actor_info.name
    if "movie_current_page" in st.session_state:
        del st.session_state["movie_current_page"]
    st.switch_page("front_pages/movie_page.py")

def on_select_change(key):
    selection = st.session_state[key]
    st.session_state.actor_menu_cache = selection


st.subheader("KK的学习教室", divider=True)

actor_tabs = ["推荐", "有码", "无码", "欧美", "搜索"]
selected = option_menu(None, actor_tabs, actor_tabs.index(st.session_state.actor_menu_cache) if st.session_state.get("actor_menu_cache", "") else 0,
                        icons=['hearts', 'airplane-fill', "airplane", 'airplane-engines', "search"],
                        on_change=on_select_change, key='actor_menu', orientation="horizontal")

os.environ["current_actor_id"] = ""
os.environ["current_actor_name"] = ""
count_id = count(1)

if selected == "推荐":
    actors = recommanded_acotrs()
    for types, actor_infos in actors.items():
        st.subheader(types, divider=True)
        col_cyc = cycle(st.columns(8))
        for actor_info in actor_infos:
            with next(col_cyc).container(border=False):
                # st.image(image=actor_info.avatar, use_container_width=True)
                is_click = streamlit_image_coordinates(source=actor_info.avatar, key=f"{types}_{actor_info.id}_{next(count_id)}", use_column_width=True)
                if is_click:
                    switch_movie_page(actor_info)
                if st.button(actor_info.name, key=f"{types}_{actor_info.id}", type="tertiary"):
                    switch_movie_page(actor_info)

elif selected in ["有码", "无码", "欧美"]:
    if not st.session_state.get("actor_current_page"):
        st.session_state.actor_current_page = 1

    actors = get_sorted_actors(selected, st.session_state.actor_current_page)
    col_cyc_censored = cycle(st.columns(8))
    for actor_info in actors:
        with next(col_cyc_censored).container(border=False):
            is_click = streamlit_image_coordinates(source=actor_info.avatar, key=f"{actor_info.id}_{next(count_id)}", use_column_width=True)
            if is_click:
                switch_movie_page(actor_info)
            if st.button(actor_info.name, key=f"{actor_info.id}_{next(count_id)}", type="tertiary"):
                switch_movie_page(actor_info)

    _, pre_page, current_page, next_page, __ = st.columns([1,1,1,1,1])
    with pre_page:
        if st.button("上一页") and st.session_state.actor_current_page > 1:
            st.session_state.actor_current_page -= 1
            st.rerun()
    with next_page:
        if st.button("下一页"):
            st.session_state.actor_current_page += 1
            st.rerun()
    with current_page:
        st.write(f"当前第 {st.session_state.actor_current_page} 页")

elif selected == "搜索":
    left, center, right = st.columns(3)
    with center:
        search_content = st.text_input(label="", value=st.session_state.get("actor_search_content", ""), key="actor_search_input", placeholder="输入老师名字开始搜索")

    left, center, right = st.columns([1,2,1])
    with center:
        if search_content:
            # st.session_state.is_actor_search = False
            actors = search_actors(search_content)
            if actors:
                col_cyc = cycle(st.columns(4))
                for actor_info in actors:
                    count_id = count()
                    with next(col_cyc).container(border=False):
                        is_click = streamlit_image_coordinates(source=actor_info.avatar, key=f"{actor_info.id}_{next(count_id)}", use_column_width=True)
                        if is_click:
                            switch_movie_page(actor_info)
                        if st.button(actor_info.name, type="tertiary"):
                            switch_movie_page(actor_info)
    
