# 🔥 Elevate Your Development Experience 🔥

A collection of heavily opinionated dotfiles for personalized development environment. These configurations reflect my preferred tools and workflows. Feel free to explore, use, and adapt them to your own needs.

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

This command generates an `.env` file, which serves as the blueprint for defining your variables. For detailed guidance on configuring your environment, refer to the **Configuration** section.

3. Execute the setup procedure by running

```bash
./setup.sh
```

This will symlink the appropriate files in subdirectories of `.dotfiles/dotfiles` to home directory.

## 🛠 Configuration

For a proper configuration, the environment variables, described below, need to be specified.

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

> :exclamation: **Note:** To use this you need to install [git-credential-manager](https://github.com/git-ecosystem/git-credential-manager/blob/release/docs/install.md)

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

## 📖 Folder Structure

There's a few special files in the hierarchy.

- **bin/**: Anything in `bin/` will get added to your `$PATH` and be made
  available everywhere.
- **topic/\*.zsh**: Any files ending in `.zsh` get loaded into your
  environment.
- **topic/path.zsh**: Any file named `path.zsh` is loaded first and is
  expected to setup `$PATH` or similar.
- **topic/completion.zsh**: Any file named `completion.zsh` is loaded
  last and is expected to setup autocomplete.
- **topic/install.sh**: Any file named `install.sh` is executed when you run `script/install`. To avoid being loaded automatically, its extension is `.sh`, not `.zsh`.
- **topic/\*.symlink**: Any file ending in `*.symlink` gets symlinked into
  your `$HOME`. This is so you can keep all of those versioned in your dotfiles
  but still keep those autoloaded files in your home directory. These get
  symlinked in when you run `script/bootstrap`.

```
sklearn-project-template/
│
├── main.py - main script to start training and (optionally) testing
│
├── base/ - abstract base classes
│   ├── base_data_loader.py
│   ├── base_model.py
│   └── base_optimizer.py
```

## 🎉 Additional notes

`dot` is a simple script that installs some dependencies, sets sane macOS
defaults, and so on. Tweak this script, and occasionally run `dot` from
time to time to keep your environment fresh and up-to-date. You can find
this script in `bin/`.

## 🤝 License

This project is licensed under the MIT License. See [LICENSE](https://github.com/janezlapajne/dotfiles/blob/main/LICENCE.md) for more details.

## 🏆 Acknowledgements

This work was inspired by the [dotfiles](https://github.com/holman/dotfiles) project by Zach Holman. Moreover, this project directly incorporates certain code snippets and design patterns for enhanced functionality.
