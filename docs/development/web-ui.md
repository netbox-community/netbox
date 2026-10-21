# Web UI Development

## Code Structure

Most static resources for the NetBox UI are housed within the `netbox/project-static/` directory.

| Path      | Description                                        |
|-----------|----------------------------------------------------|
| `dist/`   | Destination path for installed dependencies        |
| `docs/`   | Local build path for documentation                 |
| `img/`    | Image files                                        |
| `js/`     | Miscellaneous JavaScript resources served directly |
| `src/`    | TypeScript resources (to be compiled into JS)      |
| `styles/` | Sass resources (to be compiled into CSS)           |

## Front End Technologies

Front end scripting is written in [TypeScript](https://www.typescriptlang.org/), which is a strongly-typed extension to JavaScript. TypeScript is "transpiled" into JavaScript resources which are served to and executed by the client web browser.

All UI styling is written in [Sass](https://sass-lang.com/), which is an extension to browser-native [Cascading Stylesheets (CSS)](https://developer.mozilla.org/en-US/docs/Web/CSS). Similar to how TypeScript content is transpiled to JavaScript, Sass resources (`.scss` files) are compiled to CSS.

## Dependencies

The following software is employed by the NetBox user interface.

* [Bootstrap 5](https://getbootstrap.com/) - A popular CSS & JS framework
* [flatpickr](https://flatpickr.js.org/) - A lightweight date & time selection widget
* [gridstack.js](https://gridstackjs.com/) - Enables interactive grid layouts (for the dashboard)
* [HTMX](https://htmx.org/) - Enables dynamic web interfaces through the use of HTML element attributes
* [Material Design Icons](https://pictogrammers.com/library/mdi/) - An extensive open source collection of graphical icons, delivered as a web font
* [Tabler](https://tabler.io/) - A web application UI toolkit & theme based on Bootstrap 5
* [Tom Select](https://tom-select.js.org/) - Provides dynamic selection form fields

## Guidance

NetBox generally follows the following guidelines for front-end code:

- Bootstrap utility classes may be used to solve one-off issues or to implement singular components, as long as the class list does not exceed 4-5 classes. If an element needs more than 5 utility classes, a custom SCSS class should be added that contains the required style properties.
- Custom classes must be commented, explaining the general purpose of the class and where it is used.
- Reuse SCSS variables whenever possible. CSS values should (almost) never be hard-coded.
- All TypeScript functions must have, at a minimum, a basic [JSDoc](https://jsdoc.app/) description of what the function is for and where it is used. If possible, document all function arguments via [`@param` JSDoc block tags](https://jsdoc.app/tags-param.html).
- Expanding on NetBox's [dependency policy](style-guide.md#introducing-new-dependencies), new front-end dependencies should be avoided unless absolutely necessary. Every new front-end dependency adds to the CSS/JavaScript file size that must be loaded by the client and this should be minimized as much as possible. If adding a new dependency is unavoidable, use a tool like [Bundlephobia](https://bundlephobia.com/) to ensure the smallest possible library is used.
- All UI elements must be usable on all common screen sizes, including mobile devices. Be sure to test newly implemented solutions (JavaScript included) on as many screen sizes and device types as possible.
- NetBox aligns with Tabler's [supported browsers](https://docs.tabler.io/ui/getting-started/browser-support) list.

## UI Development

To contribute to the NetBox UI, you'll need to review the main [Getting Started guide](getting-started.md) in order to set up your base environment.

### Tools

Once you have a working NetBox development environment, you'll need to install [Node.js](https://nodejs.org/en/download/) to work with the NetBox UI. Use Node.js 24 or later (CI uses the latest release of the major version recorded in `netbox/project-static/.nvmrc`). Node.js includes npm, which manages the NetBox UI dependencies; no other package manager is needed.

Install the NetBox UI dependencies:

```console
$ cd netbox/project-static
$ npm ci
```

!!! warning "Check Your Working Directory"
    You need to be in the `netbox/project-static` directory to run the `npm` commands below.

`npm ci` installs exactly the versions recorded in `package-lock.json`. The project's `.npmrc` file disables dependency lifecycle scripts (none are needed) and records exact versions whenever a dependency is added or upgraded.

### Building

In order for the TypeScript and Sass (SCSS) source files to be usable by a browser, they must first be transpiled (TypeScript → JavaScript, Sass → CSS), bundled, and minified. After making changes to TypeScript or Sass source files, run `npm run build`.

| Command                 | Action                                         |
| :---------------------- | :--------------------------------------------- |
| `npm run build`         | Build TypeScript and Sass (SCSS) source files. |
| `npm run build:styles`  | Build Sass (SCSS) source files only.           |
| `npm run build:scripts` | Build TypeScript source files only.            |

All output files will be written to `netbox/project-static/dist`, where Django will pick them up when `manage.py collectstatic` is run. A full build (`npm run build`) replaces the entire contents of `dist/`, so don't place any other files there. Commit the contents of `dist/` together with the source changes that produced them: CI rebuilds the assets and fails if they differ from what was committed.

!!! info "Remember to re-run `manage.py collectstatic`"
    If you're running the development web server — `manage.py runserver` — you'll need to run `manage.py collectstatic` to see your changes.

### Linting, Formatting & Type Checking

Before committing any changes to TypeScript or Sass files, and periodically throughout the development process, you should run `npm run check` to catch formatting, code quality, or type errors.

!!! tip "IDE Integrations"
    If you're using an IDE, it is strongly recommended to install [ESLint](https://eslint.org/docs/user-guide/integrations), [TypeScript](https://github.com/Microsoft/TypeScript/wiki/TypeScript-Editor-Support), and [Prettier](https://prettier.io/docs/en/editors.html) integrations, if available. Most of them will automatically check and/or correct issues in the code as you develop, which can significantly increase your productivity as a contributor.

`npm run check` is a wrapper around the following subcommands, any of which can be run individually:

| Command                | Action                                                                     |
| :--------------------- | :------------------------------------------------------------------------- |
| `npm run check`        | Run all checks.                                                            |
| `npm run check:types`  | Check TypeScript types.                                                    |
| `npm run check:lint`   | Check TypeScript code with [ESLint](https://eslint.org/).                  |
| `npm run check:format` | Check the formatting of TypeScript and Sass (SCSS) files with [Prettier](https://prettier.io/). |

Run `npm run format` to automatically fix any formatting issues.

### Updating Dependencies

UI dependencies are upgraded to their latest releases as part of each NetBox release (see the [release checklist](release-checklist.md#update-ui-dependencies)):

```console
$ npm run upgrade
```

This upgrades every direct dependency to its latest release, except for those held back in `upgrade.mjs`, and then refreshes all transitive dependencies within their declared version ranges. Finally, it lists any dependency which remains behind its latest release (normally only the held dependencies), along with the reason.

To add a new dependency, run `npm install <package>`, or `npm install --save-dev <package>` for build tooling.

#### Held Dependencies

Some dependencies are intentionally held below their latest releases, typically because a new major version requires migration work. Each held dependency is listed, along with the version range it is held to and the reason, in the `HELD` map at the top of `netbox/project-static/upgrade.mjs`. `npm run upgrade` reports each held dependency for which a newer release is available.

A few dependencies, such as Tabler and Bootstrap, are held with a range of `patch`. This applies only patch releases of the version currently in `package.json`. Their minor and major upgrades are reviewed and applied separately, after which `npm run upgrade` continues with patch releases of the new version.

When a blocker has been resolved, remove the dependency's entry from `HELD` so that it is upgraded along with everything else.
