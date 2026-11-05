# IrisLab Streamlit Frontend

## Start

```bash
pip install streamlit requests
export IRIS_API_URL=http://localhost:8000
streamlit run app.py
```

Configure the existing Streamlit Keycloak provider in `.streamlit/secrets.toml`
or the deployment's Streamlit secrets configuration. The app uses
`st.login("keycloak")`, `st.user.tokens["access"]`, and `st.logout()`.

## Notes

- The sidebar remains visible and provides Dashboard, New Analysis, History,
  Reference Colors, Account settings, and Sign out.
- The API client sends the Keycloak access token as a Bearer token. The current
  iris_api files supplied for this project do not yet show authentication
  middleware, so sending the header does not itself enforce authorization.
- Analysis history is intentionally a placeholder because no persistence or
  history endpoint was present in the supplied backend.
- The result is displayed as returned JSON because the actual
  `schemas/analysis.py` definition was not among the supplied files.
- `IRIS_API_URL` defaults to `http://localhost:8000`.
