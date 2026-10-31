# Server CLI

Server CLI is a Click-based command-line application. Its current commands demonstrate the interface; login and server requests are not implemented yet.

## Installation

### Configure Cloudsmith Repository

Replace `<CLOUDSMITH_REPOSITORY>` with your Cloudsmith repository slug. Add its signing key and APT source:

```bash
curl -fsSL "https://dl.cloudsmith.io/public/<CLOUDSMITH_REPOSITORY>/gpg.key" \
  | sudo gpg --dearmor -o /usr/share/keyrings/cloudsmith-repository.gpg

printf 'Types: deb\nURIs: https://dl.cloudsmith.io/public/<CLOUDSMITH_REPOSITORY>/deb/ubuntu\nSuites: noble\nComponents: main\nSigned-By: /usr/share/keyrings/cloudsmith-repository.gpg\n' \
  | sudo tee /etc/apt/sources.list.d/cloudsmith.sources

sudo apt update
```

### Install Server CLI

```bash
sudo apt install server-cli
```

## Usage

### Show Available Commands

```bash
server-cli --help
```

### Enter Login Details

```bash
server-cli login
```

The command prompts for missing values. Login is currently a placeholder and does not send credentials.

### Request a Token

```bash
server-cli get-token
```

This command is a placeholder and does not make a network request.
