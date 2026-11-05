"""IrisLab Streamlit frontend."""

import logging

import streamlit as st

from api.client import IrisAPIClient, IrisAPIError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("irislab-frontend")

st.set_page_config(
    page_title="IrisLab | Analysis Portal",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      :root {
        --iris-bg: #f3f4f6;
        --iris-ink: #111827;
        --iris-muted: #6b7280;
        --iris-sidebar: #111827;
        --iris-accent: #38bdf8;
        --iris-border: #e5e7eb;
      }
      .stApp { background: var(--iris-bg); }
      [data-testid="stSidebar"] {
        background: var(--iris-sidebar);
        border-right: 1px solid #263449;
      }
      [data-testid="stSidebar"] * { color: #e5e7eb; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #cbd5e1;
      }
      [data-testid="stSidebar"] button[kind="secondary"] {
        border-color: #374151;
      }
      .iris-brand {
        display: flex; align-items: center; gap: 12px;
        padding: 8px 4px 22px 4px;
      }
      .iris-brand-mark {
        width: 42px; height: 42px; display: grid; place-items: center;
        border-radius: 13px; background: #263449; color: #7dd3fc;
        font-size: 24px;
      }
      .iris-brand-name { color: white; font-weight: 800; letter-spacing: 2px; }
      .iris-brand-sub { color: #9ca3af; font-size: 11px; letter-spacing: 1.2px; }
      .iris-eyebrow {
        color: #0284c7; font-size: 11px; font-weight: 800;
        letter-spacing: 1.6px; text-transform: uppercase;
      }
      .iris-muted { color: #6b7280; }
      .iris-card {
        background: white; border: 1px solid #e5e7eb; border-radius: 16px;
        padding: 20px; height: 100%;
      }
      .iris-hero {
        background: linear-gradient(120deg, #172638 0%, #243b53 100%);
        border-radius: 20px; padding: 30px; color: white;
        border: 1px solid #334b63;
      }
      .iris-hero h2 { color: white; margin: 8px 0; }
      .iris-hero p { color: #cbd5e1; }
      .iris-status-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        background: #22c55e; margin-right: 7px;
      }
      div.stButton > button[kind="primary"] {
        background: #38bdf8; color: #082f49; border: 0;
        font-weight: 700; border-radius: 10px;
      }
      div.stButton > button[kind="primary"]:hover {
        background: #7dd3fc; color: #082f49;
      }
      [data-testid="stFileUploader"] {
        background: white; border: 1px dashed #94a3b8;
        border-radius: 14px; padding: 12px;
      }
      h1, h2, h3 { color: #111827; }
      section[data-testid="stSidebar"] .stRadio label { padding: 5px 0; }
      .block-container { padding-top: 2.1rem; padding-bottom: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def get_authenticated_user():
    if not st.user.is_logged_in:
        st.markdown(
            """
            <div class="iris-hero">
              <div class="iris-eyebrow">IrisLab Analysis Platform</div>
              <h2>Understand the details of the iris.</h2>
              <p>Sign in with your organization account to access the analysis workspace.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        left, center, right = st.columns([1, 1.2, 1])
        with center:
            st.subheader("Sign in")
            st.caption("Authentication is handled by Keycloak.")
            if st.button("Continue with Keycloak", type="primary", width="stretch"):
                st.login("keycloak")
        st.stop()

    user = st.user
    try:
        access_token = user.tokens["access"]
    except (KeyError, TypeError):
        st.error("Keycloak session is active, but no access token is available.")
        st.stop()

    return user, access_token


user, access_token = get_authenticated_user()
username = user.get("preferred_username", None) or getattr(user, "name", "User")
email = user.get("email", "Not provided")

api = IrisAPIClient(access_token=access_token)


# ---------------------------------------------------------------------------
# Shared UI helpers
# ---------------------------------------------------------------------------
def page_heading(title: str, subtitle: str):
    st.markdown(f'<div class="iris-eyebrow">IRISLAB WORKSPACE</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def render_dashboard():
    page_heading("Dashboard", "Your IrisLab workspace.")

    st.markdown(
        """
        <div class="iris-hero">
          <div class="iris-eyebrow">IRIS ANALYSIS</div>
          <h2>Discover the details of the iris.</h2>
          <p>Upload an image to start a new IrisLab analysis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button(
        "＋  Start a new analysis",
        type="primary",
        width="stretch",
    ):
        st.session_state["page"] = "New Analysis"
        st.rerun()


def render_analysis():
    page_heading("New Analysis", "Upload a PNG or JPEG image to start an iris analysis.")

    st.markdown(
        """
        <div class="iris-card">
          <div class="iris-eyebrow">STEP 1 · IMAGE UPLOAD</div>
          <h3>Choose an image</h3>
          <p style="color:#6b7280;margin-bottom:0">
            Supported formats: PNG and JPEG · Maximum file size: 10 MiB ·
            Maximum resolution: 20 megapixels.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Select portrait image",
        type=["png", "jpg", "jpeg"],
        help="The API validates file format, size and image dimensions.",
        key="analysis_upload",
    )

    if uploaded:
        image_col, details_col = st.columns([1.2, 1])
        with image_col:
            st.image(uploaded, caption=uploaded.name, width="stretch")
        with details_col:
            st.subheader("Image details")
            st.write(f"**Filename:** {uploaded.name}")
            st.write(f"**Size:** {uploaded.size / (1024 * 1024):.2f} MiB")
            st.write(f"**Type:** {uploaded.type or 'Unknown'}")
            if uploaded.size > 10 * 1024 * 1024:
                st.error("The file exceeds the 10 MiB upload limit.")
            else:
                st.success("File size is within the configured limit.")

        if st.button("Run iris analysis", type="primary", disabled=uploaded.size > 10 * 1024 * 1024):
            try:
                with st.spinner("Analyzing image…"):
                    result = api.analyze_image(
                        filename=uploaded.name,
                        content=uploaded.getvalue(),
                        content_type=uploaded.type or "application/octet-stream",
                    )
                st.session_state["latest_analysis"] = result
                st.session_state["latest_analysis_filename"] = uploaded.name
                st.success("Analysis completed.")
            except IrisAPIError as exc:
                logger.warning("Analysis request failed: %s", exc)
                st.error(f"Analysis could not be completed: {exc}")

    result = st.session_state.get("latest_analysis")
    if result:
        st.divider()
        st.subheader("Analysis result")
        st.caption(st.session_state.get("latest_analysis_filename", ""))
        st.json(result, expanded=True)


def render_reference_colors():
    page_heading("Reference Colors", "Reference color definitions provided by the IrisLab API.")
    try:
        colors = api.get_reference_colors()
    except IrisAPIError as exc:
        st.error(f"Could not load reference colors: {exc}")
        return

    if not colors:
        st.info("The API did not return any reference colors.")
        return

    st.caption(f"{len(colors)} reference color entr{'y' if len(colors) == 1 else 'ies'}")
    # Display the API payload without assuming schema fields that were not supplied.
    for start in range(0, len(colors), 3):
        columns = st.columns(3)
        for column, item in zip(columns, colors[start : start + 3]):
            with column:
                st.markdown('<div class="iris-card">', unsafe_allow_html=True)
                if isinstance(item, dict):
                    label = item.get("name") or item.get("label") or item.get("id") or "Reference color"
                    st.subheader(str(label))
                    st.json(item, expanded=False)
                else:
                    st.write(item)
                st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Persistent sidebar navigation and top-right user menu
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="iris-brand">
          <div class="iris-brand-mark">◉</div>
          <div>
            <div class="iris-brand-name">IRISLAB</div>
            <div class="iris-brand-sub">ANALYSIS PLATFORM</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("##### WORKSPACE")

    pages = ["Dashboard", "New Analysis", "Reference Colors"]
    current_page = st.session_state.get("page", "Dashboard")
    if current_page not in pages:
        current_page = "Dashboard"

    selected_page = st.radio(
        "Navigation",
        pages,
        index=pages.index(current_page),
        label_visibility="collapsed",
        format_func=lambda value: {
            "Dashboard": "▦   Dashboard",
            "New Analysis": "◎   New Analysis",
            "Reference Colors": "◈   Reference Colors",
        }[value],
    )
    st.session_state["page"] = selected_page

    st.markdown("---")
    st.caption("IRISLAB · Analysis Portal")

# Signed-in user appears at the top-right. Sign-out is inside the small popover.
header_left, header_spacer, header_user = st.columns([5, 2, 2])
with header_user:
    st.markdown(
        f"""
        <div style="text-align:right; padding-top:8px; color:#374151;">
          <span style="font-weight:700;">{username}</span><br>
          <span style="font-size:12px; color:#6b7280;">{email}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.popover("Account", width="stretch"):
        st.write(f"**{username}**")
        st.caption(email)
        if st.button("Sign out", width="stretch"):
            st.logout()

if st.session_state["page"] == "Dashboard":
    render_dashboard()
elif st.session_state["page"] == "New Analysis":
    render_analysis()
elif st.session_state["page"] == "Reference Colors":
    render_reference_colors()
