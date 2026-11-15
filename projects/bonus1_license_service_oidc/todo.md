# 1 Protect the traffic between frontend and backend
For a demo, the simplest approach is TLS directly between the frontend and backend:

1. Choose a certificate approach. Use a demo/local certificate authority to issue the backend certificate. Avoid disabling certificate verification.

2. Create a backend certificate whose Subject Alternative Name includes the Compose service hostname, such as backend.

3. Configure the backend to serve HTTPS with that certificate and its private key.

4. Mount the certificate and key into the backend container as read-only files; don’t bake the private key into the image or commit it to source control.

5. Update the frontend’s API URL from http://backend:8080 to https://backend:<TLS-port>.

6. Make the frontend trust the issuing CA. Configure its HTTP client to use that CA certificate for verification. Keep verification enabled.

7. Adjust Compose networking and health checks to use the TLS port and HTTPS endpoint. Expose only ports needed for the demo.

8. Test the connection by confirming the frontend can call the API and that requests fail when the certificate is untrusted or the hostname doesn’t match.

9. Keep secrets and certificates separate. Protect the private key and replace demo certificates before any broader deployment.
