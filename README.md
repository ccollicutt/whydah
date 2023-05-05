# whydah

>NOTE: A whydah is a kind of bird.

This is a simple Python configuration server. It will pull a git repository 
and look for `config.json` files in one level of directories, where it's assumed
the service that is using this server will be named after the directory.

It will then serve the configuration files as JSON, with the service name as the 
key.

## Configuration

The server is configured using environment variables.

| Variable | Description | Required |
| -------- | ----------- | -------- |
| `GIT_REPO_URL ` | The URL to the git repository to pull. | Yes   
| `GIT_TOKEN` | The token to use when pulling the git repository. | No

## Routes

### GET /config

Return a list of services.

### GET /config/{service}

Returns the configuration for the given service as JSON.

### POST /config/{service}/{config}

Change a setting.

### POST /config/refresh

Pulls the git repository and reloads the configuration.