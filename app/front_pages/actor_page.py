import streamlit as st
from itertools import cycle, count
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

@st.cache_data
def censored_actores(page: int = 1) -> list[JavActor]:
    jav_db = JavDbUtil(os.environ["proxy"])
    actors = jav_db.get_actors_by_type("censored", page)
    return actors

recommanded_tab, censored_tab = st.tabs(["推荐", "有码"])

with recommanded_tab:
    # st.balloons()
    actors = recommanded_acotrs()
    for types, actor_infos in actors.items():
        st.subheader(types, divider=True)
        col_cyc = cycle(st.columns(8))
        for actor_info in actor_infos:
            # logger.info(actor_info)
            with next(col_cyc).container(border=False):
                st.image(image=actor_info.avatar, use_container_width=True)
                if st.button(actor_info.name, key=f"{types}_{actor_info.id}", type="tertiary"):
                    st.session_state["current_actor_id"] = actor_info.id
                    st.session_state["current_actor_name"] = actor_info.name
                    if "actor_max_page" in st.session_state:
                        del st.session_state["actor_max_page"]
                    st.switch_page("front_pages/movie_page.py")

with censored_tab:
    # st.balloons()
    actors = censored_actores()
    for actor_info in actors:
        col_cyc_censored = cycle(st.columns(8))
        count_id = count()
        with next(col_cyc_censored).container(border=False):
            st.image(image=actor_info.avatar, use_container_width=True)
            if st.button(actor_info.name, key=f"{actor_info.id}_{count_id}", type="tertiary"):
                st.session_state["current_actor_id"] = actor_info.id
                st.session_state["current_actor_name"] = actor_info.name
                if "actor_max_page" in st.session_state:
                    del st.session_state["actor_max_page"]
                st.switch_page("front_pages/movie_page.py")
