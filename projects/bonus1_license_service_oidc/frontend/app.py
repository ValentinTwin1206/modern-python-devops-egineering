import logging

import requests
import streamlit as st

from api import check_license, get_license

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("license-service")


# =====================0=========================
# License Service Frontend

st.title("🔑 License Service")

if not st.user.is_logged_in:
    st.write("You are not logged in.")

    if st.button("Log in with Keycloak"):
        st.login("keycloak")

    st.stop()

authenticated_user = st.user
user_name = authenticated_user.get("preferred_username", authenticated_user.name)
access_token = authenticated_user.tokens["access"]

st.write(f"Signed in as: {user_name}")
st.write(f"Email: {authenticated_user.get('email', 'N/A')}")

if st.button("Log out"):
    st.logout()

st.header("Get license")

if st.button("Get license"):
    try:
        result = get_license(access_token)
        st.session_state["license_token"] = result["cloudsmith_token"]
        st.session_state["license_expires_at"] = result["cloudsmith_expires_at"]
        st.success("License retrieved")
    except requests.RequestException as e:
        logger.error("License retrieval failed: %s", e)
        st.error(f"License retrieval failed: {e}")

st.text_input(
    "License token",
    value=st.session_state.get("license_token", ""),
    disabled=True,
)

if st.session_state.get("license_expires_at"):
    st.caption(f"Expires at: {st.session_state['license_expires_at']}")


st.header("Check license")

license_key = st.text_input("License Key")

if st.button("Check license") and license_key:
    result = check_license(license_key)

    if result["valid"]:
        st.success(
            f"Valid for {result['user']}"
        )
    else:
        st.error("Invalid license")