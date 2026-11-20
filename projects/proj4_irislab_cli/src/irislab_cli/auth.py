"""Browser-based authorization-code flow with PKCE for Keycloak."""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

import click
import requests

CALLBACK_HOST = "127.0.0.1"
CALLBACK_PATH = "/callback"
DEFAULT_CALLBACK_PORT = 8765
OIDC_TIMEOUT = 15


class OIDCError(RuntimeError):
    """Raised when interactive OIDC authentication fails."""


def _callback_port_from_environment() -> int:
    value = os.getenv("IRIS_CLI_CALLBACK_PORT", str(DEFAULT_CALLBACK_PORT))
    try:
        port = int(value)
    except ValueError as error:
        message = "IRIS_CLI_CALLBACK_PORT must be an integer port number."
        raise OIDCError(message) from error
    if not 1 <= port <= 65535:
        raise OIDCError("IRIS_CLI_CALLBACK_PORT must be between 1 and 65535.")
    return port


def _validate_callback(params: dict[str, list[str]], expected_state: str) -> str:
    """Validate state and return the authorization code from callback params."""
    
    if params.get("state", [None])[0] != expected_state:
        message = "OIDC callback state did not match; refusing the login response."
        raise OIDCError(message)
    
    if params.get("error"):
        raise OIDCError(f"Keycloak rejected the login: {params['error'][0]}")
    
    code = params.get("code", [None])[0]
    if not code:
        raise OIDCError("Keycloak callback did not contain an authorization code.")
    
    return code


def _pkce_pair() -> tuple[str, str]:
    # Generate a PKCE code verifier and its corresponding S256 challenge.
    verifier  = secrets.token_urlsafe(64)
    digest    = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    return verifier, challenge


def _issuer_from_environment() -> str:
    # Determine the OIDC issuer URL from environment variables and validate it.
    issuer = os.getenv("IRIS_OIDC_ISSUER", os.getenv("OIDC_ISSUER_URL")).rstrip("/")
    if not _is_secure_endpoint(issuer):
        raise OIDCError(
            "Use HTTPS for the OIDC issuer except on localhost during development."
        )
    return issuer


def _is_secure_endpoint(url: str) -> bool:
    # Determine if the given URL is a secure OIDC endpoint (HTTPS or localhost HTTP).
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    
    # Accept HTTPS everywhere and HTTP only for localhost development.
    hostname = parsed.hostname
    is_local = hostname and (
        hostname in {"localhost", "127.0.0.1"} or hostname.endswith(".localhost")
    )
    is_https = parsed.scheme == "https"
    is_local_http = parsed.scheme == "http" and is_local

    return bool(hostname and (is_https or is_local_http))


def login() -> str:
    """Authenticate in the browser and return an access token in memory."""
    
    issuer = _issuer_from_environment()
    client_id = os.getenv("IRIS_CLI_CLIENT_ID")
    callback_port = _callback_port_from_environment()
    redirect_uri = f"http://{CALLBACK_HOST}:{callback_port}{CALLBACK_PATH}"

    # Load the OIDC discovery metadata from the issuer's well-known endpoint.
    try:
        discovery_response = requests.get(
            f"{issuer}/.well-known/openid-configuration", timeout=OIDC_TIMEOUT
        )
        discovery_response.raise_for_status()
        metadata = discovery_response.json()
    except (requests.RequestException, ValueError) as error:
        message = f"Could not load OIDC discovery metadata from {issuer}: {error}"
        raise OIDCError(message) from error

    # Validate the discovery metadata and extract the authorization and token endpoints.
    if not isinstance(metadata, dict):
        raise OIDCError("OIDC discovery metadata must be a JSON object.")
    
    # Validate that the discovered issuer matches the configured issuer and that the 
    # required endpoints are present and secure.
    discovered_issuer = metadata.get("issuer")
    if (
        not isinstance(discovered_issuer, str)
        or discovered_issuer.rstrip("/") != issuer
    ):
        raise OIDCError("OIDC discovery issuer does not match the configured issuer.")

    # Validate that the authorization and token endpoints are present and secure.
    authorization_endpoint = metadata.get("authorization_endpoint")
    token_endpoint = metadata.get("token_endpoint")
    if (
        not isinstance(authorization_endpoint, str)
        or not isinstance(token_endpoint, str)
        or not _is_secure_endpoint(authorization_endpoint)
        or not _is_secure_endpoint(token_endpoint)
    ):
        raise OIDCError("OIDC discovery metadata is missing required endpoints.")

    # Generate a random state and PKCE pair, then build the authorization URL and 
    # start a local HTTP server to handle the callback.
    state = secrets.token_urlsafe(32)
    verifier, challenge = _pkce_pair()
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid profile",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    callback: dict[str, str | None] = {"code": None, "error": None}


    class CallbackHandler(BaseHTTPRequestHandler):
        # Handle the OIDC callback request and extract the authorization code or error.

        def do_GET(self) -> None:
            # Validate the callback request path and query parameters, then respond 
            # with a success or error message.
            request_url = urlsplit(self.path)
            if request_url.path != CALLBACK_PATH:
                self.send_error(404)
                return
            
            # Validate the callback query parameters and extract the authorization 
            # code or error.
            try:
                params = parse_qs(request_url.query)
                callback["code"] = _validate_callback(params, state)
            except OIDCError as error:
                callback["error"] = str(error)
                self.send_response(400)
                message = b"Login failed. Return to the terminal for details."
            else:
                self.send_response(200)
                message = b"Login complete. Return to the IrisLab CLI."

            # Send the HTTP response with the appropriate status code and message.
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)

        def log_message(self, format: str, *args: object) -> None:
            return

    # ==============================================================
    # Start the local HTTP server
    # ==============================================================

    # Listen for the OIDC callback and open the authorization URL in the browser.
    # Wait for the callback to be received or an error to occur,
    # then exchange the authorization code for an access token.
    try:
        server = HTTPServer((CALLBACK_HOST, callback_port), CallbackHandler)
    except OSError as error:
        message = f"Cannot listen on the OIDC callback {redirect_uri}: {error}"
        raise OIDCError(message) from error

    server.timeout = 1
    separator = "&" if "?" in authorization_endpoint else "?"
    authorization_url = f"{authorization_endpoint}{separator}{query}"

    # Open the authorization URL in the user's default web browser, 
    # or print it if the browser cannot be opened. 
    # Wait for the callback to be received or an error to occur, 
    # then exchange the authorization code for an access token.
    try:
        click.echo("Opening Keycloak login in your browser...")
        try:
            browser_opened = webbrowser.open(authorization_url, new=1)
        except (OSError, webbrowser.Error):
            browser_opened = False
        if not browser_opened:
            click.echo(f"Open this URL to sign in:\n{authorization_url}")
        while callback["code"] is None and callback["error"] is None:
            server.handle_request()
    except KeyboardInterrupt:
        raise OIDCError("Login interrupted.") from None
    finally:
        server.server_close()

    if callback["error"]:
        raise OIDCError(str(callback["error"]))

    # Exchange the authorization code for an access token at the token endpoint.
    try:
        response = requests.post(
            token_endpoint,
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "code": callback["code"],
                "redirect_uri": redirect_uri,
                "code_verifier": verifier,
            },
            timeout=OIDC_TIMEOUT,
        )
        response.raise_for_status()
        token_data = response.json()
    except (requests.RequestException, ValueError) as error:
        message = f"Could not exchange the authorization code: {error}"
        raise OIDCError(message) from error

    # Validate the token response and extract the access token.
    if not isinstance(token_data, dict):
        raise OIDCError("Keycloak token response must be a JSON object.")
    
    # Validate that the token response contains an access token 
    # and that it is a string.
    access_token = token_data.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise OIDCError("Keycloak token response did not contain an access token.")
    
    # Validate that the token type is "Bearer" and return the access token.
    token_type = token_data.get("token_type", "Bearer")
    if not isinstance(token_type, str) or token_type.lower() != "bearer":
        raise OIDCError("Keycloak returned an unsupported token type.")
    return access_token