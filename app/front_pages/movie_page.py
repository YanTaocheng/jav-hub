import streamlit as st
from itertools import cycle, count
import logging
import os

from modules.javdb.javdb import JavDbUtil

logger = logging.getLogger(__name__)


if "current_actor_name" in st.session_state:
    actor_name = st.session_state["current_actor_name"]
else:
    actor_name = ""
if "current_actor_id" in st.session_state:
    actor_id = st.session_state["current_actor_id"]
else:
    actor_id = ""

if actor_name and actor_id:
    jav_db = JavDbUtil(os.environ["proxy"])
    if "actor_max_page" not in st.session_state: 
        code, max_page = jav_db.get_max_page(jav_db.base_url_actor+actor_id+"?page=1")
        st.session_state.actor_current_page = 1
        st.session_state.actor_max_page = max_page if max_page else 1

    movie_tab = st.tabs([actor_name])[0]

    with movie_tab:
        code, movies = jav_db.get_id_details_by_star_id(actor_id, st.session_state.actor_current_page)
        col_cyc = cycle(st.columns(4))
        count_cyc = count()
        for movie in movies:
            # logger.info(movie)
            with next(col_cyc).container(border=True):
                with st.container(border=False):
                    st.image(image=movie.get("img"), caption=f'{movie.get("id")} {movie.get("title")}', use_container_width=True)
                if "磁鏈" in movie.get("tag", ""):
                    disabled = False
                    tag =  movie.get("tag", "")
                else:
                    disabled = True
                    tag = "无磁链"
                if st.button(label=tag, key=next(count_cyc), type="tertiary", disabled=disabled):
                    code, magent_info = jav_db.get_av_by_javdb_id(movie.get("jav_id"), True, True)
                    # logger.info(magent_info)
                    if magent:=magent_info.get("magnets"):
                        st.success(magent[0]["link"])
                    else:
                        st.warning("未获取到磁链")
        _, pre_page, current_page, next_page, __ = st.columns([1,1,1,1,1])
        with pre_page:
            if st.button("上一页") and st.session_state.actor_current_page > 1:
                st.session_state.actor_current_page -= 1
                st.rerun()
        with next_page:
            if st.button("下一页") and st.session_state.actor_current_page < st.session_state.actor_max_page:
                st.session_state.actor_current_page += 1
                st.rerun()
        with current_page:
            st.write(f"第 {st.session_state.actor_current_page} 页 / 共 {st.session_state.actor_max_page} 页")

