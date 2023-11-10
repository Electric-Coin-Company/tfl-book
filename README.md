# tfl-book

The [Zcash Trailing Finality Layer](https://electric-coin-company.github.io/tfl-book/) design book.

This repository is the source text and rendering configuration for the book. To read the book, use the link above.

The `mdbook` tool renders the contents into a pretty format from `markdown` based source code

## Github CI

There are two github CI workflows:

- `merge-acceptance.yaml`: triggers on `pull_request` to check that `mdbook build` succeeds and there aren't dangling `md` files (e.g. you remove an entry in `SUMMARY.md` but forget to rm the file.)
- `render-site.yaml`: triggers on `push` to `main` to render the site to https://electric-coin-company.github.io/tfl-book/
  - **Warning:** this workflow relies on full read/write access to the `gh-pages` branch. Don't mess with that branch unless you're very confident in the impacts.

## `git-hooks`

There is a directory `git-hooks` that we advocate all contributors use.

Use this command to enable it:

```
git config --local core.hooksPath git-hooks
```

## Prerequisites

### Rust prerequisites

- `cargo install mdbook`
- `cargo install mdbook-graphviz`
- `cargo install mdbook-linkcheck`

### Other prerequisites

- `graphviz` - on debian-like: `sudo apt install graphviz`

## Rendering

- `mdbook build`
