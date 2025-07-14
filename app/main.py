import os
import logging
import streamlit as st

from modules.javdb.javdb import JavDbUtil
from log import setup_logger
import streamlit as st

os.environ['LOG_LEVEL'] = "INFO"
os.environ["proxy"] = "http://192.168.3.65:7890"
logger = logging.getLogger(__name__)
setup_logger()


pages = {
    "JavDB": [
        st.Page(
            page="front_pages/actor_page.py",
            title="演员",
            icon=":material/person:"
        ),
        st.Page(
            page="front_pages/movie_page.py",
            title="影片",
            icon=":material/hangout_video:"
        ),
        
    ]
}
st.navigation(pages).run()
