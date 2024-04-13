# 🔥 Elevate Your Development Experience 🔥

A collection of heavily opinionated terminal configurations for personalized development environment. These settings reflect my preferred tools and workflows. Feel free to explore, use, and adapt them to your own needs.

## 🔍 Overview

The setup is designed to enhance the development experience on the [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/), leveraging the capabilities of the Ubuntu Linux system. The current configuration of dotfiles employs a variety of tools, each contributing to a sophisticated development environment. Some of the tools included:

- [Oh-My-Zsh](https://ohmyz.sh/): A community-driven framework for managing Zsh configuration, which includes helpful features such as plugin and theme support.
- [Tmux](https://github.com/tmux/tmux): A terminal multiplexer that enables multiple terminal sessions within a single window.
- [Vim](https://www.vim.org/): A highly configurable text editor built to facilitate efficient text editing.
- [Git](https://git-scm.com/): A distributed version control system used to track changes in source code during software development.
- [Atuin](https://github.com/atuinsh/atuin): A replacement for shell's history that syncs across multiple machines and provides advanced features like search and analytics.

The setup is flexible and can easily accommodate the integration of additional plugins as per the user's requirements.

## 🕐 Quickstart

1. Begin by cloning the repository and navigating into the directory

```bash
git clone https://github.com/janezlapajne/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
```

2. Setup environment variables

The configuration of the dotfiles is driven by environment variables. To establish a basic configuration, execute the following command:

```bash
tail -n +7 .env.example > .env
```

This command generates an `.env` file, which serves as the blueprint for defining variables. For detailed guidance on configuring the environment, refer to the **Configuration** section.

3. Execute the setup procedure by running

```bash
./setup.sh
```

This will symlink the appropriate files in subdirectories of `.dotfiles/dotfiles` to home directory.

## 🛠 Configuration

To ensure correct configuration, it's essential to define the environment variables outlined below.

### Git

- `GIT_NAME`: Name to appear in Git commits.
- `GIT_EMAIL`: Email to appear in Git commits.
- `GIT_CREDENTIAL_HELPER`: The path to the Git credential helper executable. This is used by Git to remember the credentials.

Example:

```
GIT_NAME=name
GIT_EMAIL=email@example.com
GIT_CREDENTIAL_HELPER=/mnt/c/Program/Files/Git/mingw64/libexec/git-core/git-credential-wincred.exe
```

> :exclamation: **Note:** For the Git credential helper to work, [git-credential-manager](https://github.com/git-ecosystem/git-credential-manager/blob/release/docs/install.md) needs to be installed. The exact location of *git-credential-wincred.exe* may vary depending on the specific Git installation.

### Atuin

- `ATUIN_USERNAME`: Atuin username.
- `ATUIN_EMAIL`: The email address associated with Atuin account.
- `ATUIN_PASSWORD:` The password for Atuin account.
- `ATUIN_KEY:` _(Optional)_ Atuin key, used for syncing shell history across devices.

Example:

```
ATUIN_USERNAME=name
ATUIN_EMAIL=email@example.com
ATUIN_PASSWORD=password
ATUIN_KEY=
```

### SSH

- `SSH_EMAIL`: The email address used when generating SSH key.
- `SSH_PASSPHRASE`: _(Optional)_ The passphrase for SSH key.

Example:

```
SSH_EMAIL=email@example.com
SSH_PASSPHRASE=
```

### Terminal

- `TERMINAL_THEME_STARSHIP`: _(Optional)_ Bool value whether to use [starship](https://github.com/starship/starship) theme.

Example:

```
TERMINAL_THEME_STARSHIP=true
```

> :exclamation: **Note:**
> For optimal usage of the `starship` theme in both the terminal and Visual Studio Code, it is recommended to install the `FiraCode Nerd Font`:
>
> 1. Visit [Nerd Fonts](https://www.nerdfonts.com/font-downloads) and download "FiraCode Nerd Font".
> 2. Install the font by double-clicking on the downloaded file.
>
> To use the font in Windows Terminal:
>
> 1. Go to Settings and navigate to Defaults > Appearance > Font Face.
> 2. Select `FiraCode Nerd Font` from the dropdown menu.
>
> To use the font in Visual Studio Code:
>
> 1. Open the settings (File > Preferences > Settings or `Ctrl + ,`).
> 2. Search for `terminal.integrated.fontFamily`.
> 3. Set the value to `FiraCode Nerd Font` → This will update the setting as follows: `"terminal.integrated.fontFamily": "FiraCode Nerd Font"`.

## 📖 Folder Structure

The following diagram provides a schematic representation of the project's folder structure. Each directory and file is briefly described to give an overview of their purpose and function within the project:

```
📚 .dotfiles/
│
├── 🚀 setup.sh                -> Main script to setup the dotfiles
├── 🛠️ .env                    -> Configuration variables
│
├── 📂 bin/                    -> Various utility scripts (added to $PATH)
│   ├── 📄 dot                 -> main update script
│   └── 📄 ...                 -> other scripts
│
├── 📂 core/                   -> Core setup scripts
│   ├── 📄 paths.sh
│   └── 📄 setup-dotfiles.sh
│
├── 📂 docs/                   -> Documentation, notes, etc.
│   └── 📄 ...
│
├── 📂 dotfiles/               -> Configuration for various tools
│   ├── 📂 zsh/                -> main shell configuration
│   └── 📂 .../
│
├── 📂 functions/              -> Utility functions (added to $PATH)
│   └── 📄 ...
│
├── 📂 scripts/                -> Main scripts
│   ├── 📄 install-packages.sh -> installs system packages using apt-get
│   ├── 📄 install-tools.sh    -> installs other tools, using pip3, npm etc.
│   ├── 📄 install.sh          -> executes all install.sh scripts
│   ├── 📄 setup-all.sh        -> executes all setup.sh scripts
│   └── 📄 update-env.sh       -> updates .env.example (used during development)
│
└── 📂 utils/                  -> Utility scripts used inside repo
    └── 📄 ...
```

This project follows a specific set of conventions for organization and functionality:

- **bin/**: This directory contains utility scripts. Any script placed here will be added to the `$PATH` and made accessible from anywhere in the system.
- **bin/dot**: This is a simple script designed to manage dependencies and system packages. It not only installs and updates dependencies but also upgrades system packages. To maintain an up-to-date and efficient environment, it's recommended to execute this script periodically.
- **docs**: This directory serves as a repository for documentation, notes, and frequently used commands, among other things. It's a convenient location for storing any information that might be needed at hand.
- **functions/**: This directory is for utility functions. Like the `bin/` directory, anything placed here will be added to the `$PATH` and can be used globally.
- **dotfiles/\*\*/\*.zsh**: Any file with a `.zsh` extension located in the `dotfiles/` directory or its subdirectories will be loaded into the environment.
- **dotfiles/\*\*/path.zsh**: Any file named `path.zsh` is loaded before other files. It's expected to set up `$PATH` or similar environment variables.
- **dotfiles/\*\*/completion.zsh**: Any file named `completion.zsh` is loaded last and is expected to set up autocomplete functionality.
- **dotfiles/\*\*/install.sh**: Any file named `install.sh` is executed when the `scripts/install.sh` script is run. These files have a `.sh` extension instead of `.zsh` to prevent them from being loaded automatically. These scripts are run each time the `bin/dot` script is run.
- **dotfiles/\*\*/setup.sh**: Any file named `setup.sh` is executed when the `scripts/setup-all.sh` script is run. Like `install.sh` files, these have a `.sh` extension to prevent automatic loading. The `setup.sh` scripts are run after `install.sh` scripts and only when the `scripts/setup.sh` script is run.
- **dotfiles/\*\*/\.\***: Any file starting with a `.` is symlinked into the `$HOME` directory when the main `setup.sh` script is executed. This allows for easy management of dotfiles.

## 🎉 Additional notes

We greatly appreciate any contribution, no matter how small. If you've identified a problem with the setup, we encourage you to first browse through both open and closed issues to see if it has been addressed before. If it's a new issue, please don't hesitate to create a new one on GitHub. If you're interested in correcting an existing issue or expanding the project's functionality, we welcome your involvement. Simply fork the repository, make your changes, and then submit a pull request on GitHub. Questions are also welcome. If you're unsure about something or need clarification, feel free to post an issue on GitHub.

## 🤝 License

This project is licensed under the MIT License. See [LICENSE](https://github.com/janezlapajne/dotfiles/blob/main/LICENCE.md) for more details.

## 🏆 Acknowledgements

This work was inspired by the [dotfiles](https://github.com/holman/dotfiles) project by Zach Holman. Moreover, this project directly incorporates certain code snippets and design patterns for enhanced functionality.
