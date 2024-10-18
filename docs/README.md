Docs for Mesa-Geo
=============

The readable version of the docs is hosted at [mesa-geo.readthedocs.org](http://mesa-geo.readthedocs.io/).

This folder contains the docs that build the docs for   Mesa-Geo on readthdocs.

## How to publish updates to the docs

Updating docs can be confusing. Here are the basic setups.

### Install dependencies

From the project root, install the dependencies for building the docs:

```shell
pip install -e ".[docs]"
```

### Submit a pull request with updates

1. Create branch (either via branching or fork of repo) -- try to use a descriptive name.
    * `git checkout -b doc-updates`
2. Update the docs. Save.
3. Build the docs, from the inside of the docs folder.
    * `make html`
4. Commit the changes. If there are new files, you will have to explicit add them.
    * `git commit -am "update docs"`
5. Push the branch.
    * `git push origin doc-updates`
6. From here you will want to submit a pull request to main.

### Update read the docs

From this point, you will need to find someone that has access to readthedocs. Currently, that is [@wang-boyu](https://github.com/wang-boyu).

1. Accept the pull request into main.
2. Log into readthedocs and launch a new build -- builds take about 10 minutes or so.

## Helpful Sphnix tips
* Build html from docs:
  * `make html`
* Autogenerate / update sphninx from docstrings (replace your name as the author):
  * `sphinx-apidoc -A "Jackie Kazil" -F -o docs mesa_geo/`
