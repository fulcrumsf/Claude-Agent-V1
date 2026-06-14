---
title: "Canva CLI Canva Apps SDK Documentation"
type: "api-doc"
category: "app-dev"
tags:
  - app-dev
  - canva
  - cli
  - sdk
  - documentation
created: 2026-05-12
source: local
---

Developer resources

[Canva CLI](https://www.canva.dev/docs/apps/canva-cli/) [Dev MCP server](https://www.canva.dev/docs/apps/mcp-server/)

Examples

Intents

[Overview](https://www.canva.dev/docs/apps/intents/)

Content Publisher

Data Connector

Design Editor

URL Expander

Designing apps

App UI Kit

Design guidelines

App components

[Figma resource](https://www.canva.dev/docs/apps/figma-resource/)

Developing apps

App configuration

Authenticating users

Creating elements

Working with elements

Localization

Security

Design interaction

[Using design IDs](https://www.canva.dev/docs/apps/using-design-ids/) [Exporting designs](https://www.canva.dev/docs/apps/exporting-designs/)

Testing

Monetizing apps

[Overview](https://www.canva.dev/docs/apps/monetization/) [App Adoption Awards](https://www.canva.dev/docs/apps/app-adoption-awards/) [External payment links](https://www.canva.dev/docs/apps/accepting-payments/)

Premium Apps Program

[Set up payout details](https://www.canva.dev/docs/apps/payout-details/)

Distributing apps

## Canva CLI

## Introduction

`@canva/cli` is a command line tool designed for creating and managing Canva Apps. Use `@canva/cli` to get started creating and testing your app. The Canva CLI allows you to create apps from the command line, and to use Canva's recommended development tools and templates.

## Requirements

Before using the CLI, make sure that you have the following:

- Node.js `v24`
- npm `v11`
- A [Canva account⁠(opens in a new tab or window)](https://www.canva.com/developers).
	If you are using a version manager such as nvm, run the `nvm install 24` command to make sure you have the correct Node.js version.

## Quickstart

The following commands create a new Canva app using the Canva CLI.

```shell
npm install -g @canva/cli@latest
canva login
canva apps create "My New App" --template="hello_world" --distribution="public" --git --installDependencies
cd my-new-app
npm start
```

## Use the Canva CLI

### Step 1: Install and log in

Installing the Canva CLI allows you to create new apps from the command line.

To get started:

1. Install the Canva CLI globally.
	```shell
	npm install -g @canva/cli@latest
	```
2. Log in to the Canva CLI. The Canva CLI then opens an access request page in your browser.
	```shell
	canva login
	```
3. In your browser, click **Allow** to grant the Canva CLI access to create and edit apps on your behalf. When you grant access, the Canva CLI generates an auth token and stores it locally. For more information on the auth token, read the following section on [auth token storage and removal](https://www.canva.dev/docs/apps/canva-cli/#log-out-auth-token-storage-and-removal).
4. Copy the confirmation code shown in your browser, and paste it into the Canva CLI input.

### Step 2: Create your app

After you log in to the Canva CLI and authorize it, you can create your app.

To create a new app:

1. Run the `canva apps create` command. The flags in the following code snippet are optional, and you can instead configure these settings during the apps creation process. See the [CLI Reference](https://www.canva.dev/docs/apps/canva-cli/#cli-reference) for more information on each flag.
	```shell
	canva apps create "My New App" --template="hello_world" --distribution="public" --git --installDependencies
	```
	You can't change the distribution type after creating an app.

### Step 3: Preview your app

When your new app is ready, the Canva CLI automatically opens the [Developer Portal⁠(opens in a new tab or window)](https://www.canva.com/developers/apps) to your new app's configuration page in your browser. You can then continue to preview and manage your new app.

To preview your app:

1. Change into your new app's folder.
	```shell
	cd my-new-app
	```
2. Run the following command to start your app.
	```shell
	npm start
	```
3. The preview URL will be generated and opened automatically in your browser.
4. If this is the first time previewing your app, click **Open** to preview your new app.

### Step 4: Run a health check on your app

After creating your app, you can diagnose potential issues using:

```shell
canva apps doctor
```

This checks for missing dependencies, outdated packages, and other issues.

## Log out, auth token storage, and removal

When you log in to the Canva CLI using the `canva login` command, and then grant the Canva CLI access to manage apps in your Canva account, an auth token is encrypted and stored locally on your machine. The token provides authentication for future requests so you don't need to grant the Canva CLI access each time it sends a request.

When you log out of the Canva CLI with the `canva logout` command, the auth token is revoked, and deleted.

### Token Location

The auth token is located in your home directory under the `.canva-cli` folder.

### Removing the Token

To delete the token, there are two options. However, only the `canva logout` command revokes and deletes the token. If there's a copy of the token, it's possible to reconnect the Canva CLI to your account's apps using the token.

#### Log out

1. Use the `canva logout` command to revoke access and delete the stored token.
	```shell
	canva logout
	```

#### Delete the file manually

1. Locate the `credentials` file, which is stored in the following locations:
	- **macOS and Linux**: The token is stored in `~/.canva-cli/credentials`.
		- **Windows**: The token is stored in `%USERPROFILE%\.canva-cli\credentials`.
2. Delete the file.

## CLI Reference

After installation, you can use the Canva CLI by running:

```shell
canva <command-name>
```

### Flags

Top-level flags applicable to commands:

- `--help`: Show help information about commands and flags.
- `--lite`: Enable a simplified CLI interface for enhanced accessibility.
- `--version`: Show the CLI version number.

### Commands

#### welcome

Show the welcome page and general information.

```shell
canva welcome
```

#### tip

Print a random development tip for working with the Apps SDK.

```shell
canva tip
```

- **Aliases**:
	- `tips`: Also prints a random development tip.

#### bug

Raise an issue with the Canva CLI on GitHub.

```shell
canva bug
```

#### login

Log in to the Canva CLI.

```shell
canva login
```

- **Flags**:
	- `--china`, `--cn`: Login to canva.cn, this will use canva.cn for all subsequent commands until you log out.
		- `--mode`: The authentication mode or flow to use when logging in.
		Available modes:
		- `"callback"`: Runs a local server to receive the auth code (default).
				- `"manual"`: Prompts you to copy and paste the auth code manually.

#### logout

Log out of the Canva CLI, and delete the saved auth token:

```shell
canva logout
```

#### mcp

Start the canva [MCP⁠(opens in a new tab or window)](https://modelcontextprotocol.io/) server. This is usually called by your MCP client, such as Claude Desktop, Cursor, or other compatible tools. For more information on how to configure your MCP client to use the Canva MCP server, please see [MCP Server](https://www.canva.dev/docs/apps/mcp-server/) in the developer documentation.

#### apps

Manage your Canva apps.

```shell
canva apps
```

##### create

Create a new Canva app.

```shell
canva apps create "My New App" --template="hello_world" --distribution="public" --git --installDependencies
```

- **Arguments**:
	- `--name`: Sets the app's name. Provide the name you want for the app.
- **Flags**:
	- `--template`: Specifies the starting template for the app. Templates are pre-built starter projects that demonstrate common use cases and best practices. For a complete list of available templates, see [App templates](https://www.canva.dev/docs/apps/app-templates/).
		- `--distribution`: Sets the app's distribution type.
		Available types:
		- `"public"`: Available to all Canva users, subject to Canva review.
				- `"private"`: Only available to your team on an [Enterprise plan⁠(opens in a new tab or window)](https://www.canva.com/enterprise/), and requires team admin approval.
			You can't change the distribution setting after creating a new app with the `canva apps create` command.
		- `--git`: Initializes a Git repository in the project directory.
		- `--installDependencies`: Automatically installs necessary npm dependencies during the app creation process.
		- `--optionalConfig`: Optional configuration files to be created in the project directory.
		Available options:
		- `"vscode"`: Adds a `.vscode` folder to the project directory.
				- `"cursor"`: Adds a `.cursor` folder to the project directory.
				- `"agents.md"`: Adds a `AGENTS.md` file to the project directory.
				- `"claude"`: Adds a `CLAUDE.md` file to the project directory.
		- `--offline`: Scaffold the app locally without also creating an app in the Developer Portal.
		- `--yes`: Answer yes, or use the default, for all questions during app creation.

##### list

List all Canva apps.

```shell
canva apps list
```

- **Flags**:
	- `--appId`: Specifies an App ID to select.
		- `--all`, `-a`: Lists all apps at once without pagination.
		- `--print`, `-p`: Prints the list of apps to the console without interactivity.

##### preview

Preview your app.

```shell
canva apps preview
```

##### doctor

Run diagnostics on your Canva App to identify and fix issues.

```shell
canva apps doctor
```

- **Flags**:
	- `--ci`: Run in CI mode (overrides all other flags: enables `--report`, `--silenceUpdates`, disables `--fix`, `--verbose`, skips environment checks).
		- `--fix`: Automatically apply fixes for issues where possible.
		- `--report`: Output check results without prompting for fixes.
		- `--verbose`: Show detailed diagnostic output optimized for AI agent assistance.
		- `--check`: Specify a specific check to run.

##### migrate

Run specific code migrations to update your app to newer patterns and APIs.

```shell
canva apps migrate <migrationName>
```

- **Arguments**:
	- `migrationName`: Name of the migration to run.
		Available migrations:
		- `"apps-sdk-v1-v2"`: Migrates apps using the Apps SDK v1 packages to v2.
				- `"app-ui-kit-v5"`: Migrates apps using App UI Kit v4 to v5.
				- `"design-editor-intent"`: Migrates from direct render pattern to design intents pattern.
- **Examples**:
	```shell
	canva apps migrate apps-sdk-v1-v2
	canva apps migrate app-ui-kit-v5
	canva apps migrate design-editor-intent
	canva apps migrate apps-sdk-v1-v2 --debug
	```

##### config

Manage your [App Configuration](https://www.canva.dev/docs/apps/app-configuration/).

```shell
canva apps config
```

###### pull

Fetch the [canva-app.json](https://www.canva.dev/docs/apps/app-configuration/canva-app-json/) config from the Developer Portal.

```shell
canva apps config pull
```

- **Flags**:
	- `--force`: Automatically pull config regardless of conflicts.
		- `--strategy`: Choose the resolution option for config conflicts - local, remote or manual

###### push

Submit the local [canva-app.json](https://www.canva.dev/docs/apps/app-configuration/canva-app-json/) to the Developer Portal.

```shell
canva apps config push
```

- **Flags**:
	- `--force`: Automatically push config regardless of conflicts.
		- `--strategy`: Choose the resolution option for config conflicts - local, remote or manual

###### status

Report on the status and validity of the [canva-app.json](https://www.canva.dev/docs/apps/app-configuration/canva-app-json/) config.

```shell
canva apps config status
```

##### link

Link your local project to an existing Canva app by updating the.env file

```shell
canva apps link
```

- **Flags**:
	- `--appId`: Specifies an App ID to select.

#### logout

Log out and revoke Canva CLI access.

```shell
canva logout
```

## Next Steps

- [Preview your app in the Canva editor](https://www.canva.dev/docs/apps/previewing-apps/)
- [Integrate your app with Canva using the Apps SDK](https://www.canva.dev/docs/apps/integrating-canva/)

## Limitations

You must manage your new app created through the Canva CLI through the [Developer Portal⁠(opens in a new tab or window)](https://www.canva.com/developers/apps). You can't manage apps completely through the Canva CLI.

## Updates

To update the CLI to the latest version, run:

```shell
npm update -g @canva/cli@latest
```

## Contributions

Currently the Canva CLI doesn't accept third-party contributions. Please submit any feature requests through the [Canva Developers Community⁠(opens in a new tab or window)](https://community.canva.dev/) or raise an issue on [Github⁠(opens in a new tab or window)](https://github.com/canva-sdks/canva-cli/issues/new).

## License

Refer to the `LICENSE.md` file for more information.