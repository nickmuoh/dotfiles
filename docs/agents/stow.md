# Stow packages

Each package directory mirrors its target path under `$HOME`. Edit the package file in this repository, not the deployed target.

Before deploying a package, run:

```sh
stow -nv <package>
stow -v <package>
```

When a deployed target already exists, verify its link target with `ls -l <path>`. Do not overwrite a real file in `$HOME`; inspect it and ask the user before replacing or adopting it.
