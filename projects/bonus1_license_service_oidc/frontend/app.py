import streamlit as st
import logging

from api import create_license, check_license

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("license-service")


# =====================0=========================
# License Service Frontend

st.title("🔑 License Service")
st.header("License erzeugen")

user = st.text_input("Benutzer")

if st.button("License erzeugen"):
    if user:
        try:
            result = create_license(user)

            st.success("License erzeugt")
            st.code(result["license_key"])
        except Exception as e:
            logger.error(f"Fehler beim Erzeugen der License: {e}")
            st.error(f"Fehler beim Erzeugen der License: {e}")


st.header("License überprüfen")

license_key = st.text_input("License Key")

if st.button("Überprüfen"):
    if license_key:
        result = check_license(license_key)

        if result["valid"]:
            st.success(
                f"Gültig für {result['user']}"
            )
        else:
            st.error("Ungültige License")