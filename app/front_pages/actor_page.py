import streamlit as st
from streamlit_card import card
from st_card_component import card_component
from itertools import cycle
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

# @st.cache_data
# def censored_actores(page: int = 1) -> list[JavActor]:
#     jav_db = JavDB("https://javdb.com", "http://192.168.3.65:7890")
#     actors = jav_db.get_actors_by_type("censored", page)
#     return actors

recommanded_tab, censored_tab = st.tabs(["推荐", "有码"])

with recommanded_tab:
    # st.balloons()
    actors = recommanded_acotrs()
    for types, actor_infos in actors.items():
        st.subheader(types, divider=True)
        col_cyc = cycle(st.columns(6, border=True))
        for actor_info in actor_infos:
            # logger.info(actor_info)
            with next(col_cyc):
                st.image(image=actor_info.avatar, use_container_width=True)
                if st.button(actor_info.name, key=f"{types}_{actor_info.id}", type="tertiary"):
                    st.session_state["current_actor_id"] = actor_info.id
                    st.session_state["current_actor_name"] = actor_info.name
                    if "actor_max_page" in st.session_state:
                        del st.session_state["actor_max_page"]
                    st.switch_page("front_pages/movie_page.py")
