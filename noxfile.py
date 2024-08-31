import nox

nox.options.sessions = ["lint", "docs"]
nox.options.reuse_existing_virtualenvs = True

python = ["3.11"]
doc_deps = [
    "jinja2", 
    "mkdocs-autorefs",
    "mkdocs-gen-files",
    "mkdocs-get-deps",
    "mkdocs-git-authors-plugin",
    "mkdocs-glightbox",
    "mkdocs-macros-plugin",
    "mkdocs-material",
    "mkdocs-material-extensions",
    "mkdocs-rtd-dropdown",
    "mkdocstrings",
    "mkdocstrings-python"
    ]
lint_deps = ["black", "flake8", "mypy", "isort"]

@nox.session(reuse_venv=True)
def docs(session):
    session.install(*doc_deps)
    session.run("mkdocs", "serve")
    
@nox.session(reuse_venv=True)
def lint(session):
    session.install(*lint_deps)
    session.run("black", "--line-length=120", "src")
    # These can be quite messy lint issues to fix, use at your own will of being 
    # correct
    #session.run("flake8", "src")
    #session.run("mypy", "src")
    session.run("isort", "--profile", "black", "src")