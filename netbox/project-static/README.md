<div style="align:center;">
    <h1>NetBox UI Development</h1>
</div>

## Introduction

The following tools and languages are used during the **build** process:

### Languages
#### [Sass](https://sass-lang.com/)

Sass is similar to CSS, but has variables, functions, utilities, mixins, and other nice syntax additions. With Sass, we can import Bootstrap's Sass files, override or extend variables, and add classes of our own using Bootstrap's variables (as well as other CSS libraries used).

#### [TypeScript](https://www.typescriptlang.org/)

TypeScript is a strict static-typed superset of JavaScript. In development, it's an _extremely_ effective tool for accurately describing and checking the code, which leads to significantly fewer bugs, a better development experience, and more predictable/readable code.

### Tools

#### [ParcelJS](https://parceljs.org/)

Parcel is a bundling tool that takes given input files of most front-end languages (Sass and TypeScript, in our case), follows each of their dependencies (via import statements), and bundles them into a single minified file.

For JavaScript, every `.ts` file in `netbox/project-static/src` is:

1. Transpiled from TypeScript to JavaScript
2. Minified
3. Combined into a single output file at `netbox/project-static/dist/netbox.js` (this includes any dependant libraries imported in a file)

Likewise, with Sass, each `*.scss` file is:

1. Transpiled from Sass to CSS
2. Minified
3. Combined into a single output file at `netbox/project-static/dist/netbox.css` (this includes any dependant libraries imported in file)

For pre v3 releases, this process will be run in development, and the files in `netbox/project-static/dist` checked into change control. This is because running Parcel (and installing dependencies via NPM/Yarn, as described below) requires other system dependencies like NodeJS and Yarn, which aren't part of the current v2 dependency list.

#### [Yarn](https://yarnpkg.com/)

Yarn is a package manager (think `pip` in the Python world) for JavaScript packages on the [NPM](https://www.npmjs.com/) registry (think PyPI in the Python world). Technically, one could simply use NPM's own `npm` tool as well, however, `yarn` is widely used because it tends to be significantly faster than `npm` (and has other cool features, which we aren't using in NetBox).

### Installation

#### NodeJS

If you don't already have it, install [NodeJS](https://nodejs.org/en/download/) (the LTS release should be fine).

#### Yarn

Next, install [Yarn](https://yarnpkg.com/getting-started/install):

```bash
npm install -g yarn
```

#### NetBox Dependencies

From `netbox/project-static`, run the command `yarn` — this will install all production and development dependencies to `netbox/project-static/node_modules`.

### Creating dist files

After any changes to TypeScript or Sass files, you'll need to recompile/bundle the dist files.

To bundle only CSS files, run:

```bash
# netbox/project-static
yarn bundle --styles
```

To bundle only JS files, run:

```bash
# netbox/project-static
yarn bundle --scripts
```

Or, to bundle both, run:

```bash
# netbox/project-static
yarn bundle
```

_**Note:** if you're running the development web server_ — `manage.py runserver` — _you'll need to run_ `manage.py collectstatic` _to see your changes._
