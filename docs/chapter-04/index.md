# An OIDC-Enabled License Service

## Introduction

Chapter 04 brings together the concepts from the previous chapters in one
integrated project: an OIDC-enabled license service. It builds on the
[PyGuard security middleware](../../projects/proj1_pyguard/README.md), which
was previously used to demonstrate virtual environments and Python wheels, and
the [License Service](../../projects/proj3_license_service/README.md), which
served as a practical example of `uv` workspaces and containerized Python
applications.

The final project extends this foundation with several additional components:
a small [Streamlit](https://streamlit.io/) frontend, an OIDC authentication workflow backed by a
[Keycloak](https://www.keycloak.org/) instance, and a comprehensive dev container containing the tools
needed to test the complete system. Docker Compose orchestrates these
components and connects them into one development environment.

Although the project continues to apply Python development practices, this
chapter places greater emphasis on system-level understanding. It shows how
applications, middleware, authentication, containers, development tools, and
orchestration work together to form a complete, testable system.

## Overview

Use the navigation on the left to move through the chapter's sections:

| Section | Summary | Project |
|---------|---------|---------|
| [Section 01](./section-01.md) | Frontend | OIDC License Service |
| [Section 02](./section-02.md) | Project Orchestration | OIDC License Service |
| [Section 03](./section-03.md) | OIDC | OIDC License Service |
| [Section 04](./section-04.md) | Dev Container | OIDC License Service |
| [Section 05](./section-05.md) | End-to-End Testing | OIDC License Service |
