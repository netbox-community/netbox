# Web UI Development

## Front End Technologies

The NetBox UI is built on languages and frameworks:

### Styling & HTML Elements

#### [Bootstrap](https://getbootstrap.com/) 5

The majority of the NetBox UI is made up of stock Bootstrap components, with some styling modifications and custom components added on an as-needed basis. Bootstrap uses [Sass](https://sass-lang.com/), and NetBox extends Bootstrap's core Sass files for theming and customization.

### Client-side Scripting

#### [TypeScript](https://www.typescriptlang.org/)

All client-side scripting is transpiled from TypeScript to JavaScript and served by Django. In development, TypeScript is an _extremely_ effective tool for accurately describing and checking the code, which leads to significantly fewer bugs, a better development experience, and more predictable/readable code.

As part of the [bundling](#bundling) process, Bootstrap's JavaScript plugins are imported and bundled alongside NetBox's front-end code.

!!! danger "NetBox is jQuery-free"
    Following the Bootstrap team's deprecation of jQuery in Bootstrap 5, NetBox also no longer uses jQuery in front-end code.

## Guidance

NetBox generally follows the following guidelines for front-end code:

- Bootstrap utility classes may be used to solve one-off issues or to implement singular components, as long as the class list does not exceed 4-5 classes. If an element needs more than 5 utility classes, a custom SCSS class should be added that contains the required style properties.
- Custom classes must be commented, explaining the general purpose of the class and where it is used.
- Reuse SCSS variables whenever possible. CSS values should (almost) never be hard-coded.
- All TypeScript functions must have, at a minimum, a basic [JSDoc](https://jsdoc.app/) description of what the function is for and where it is used. If possible, document all function arguments via [`@param` JSDoc block tags](https://jsdoc.app/tags-param.html).
- Expanding on NetBox's [dependency policy](style-guide.md#introducing-new-dependencies), new front-end dependencies should be avoided unless absolutely necessary. Every new front-end dependency adds to the CSS/JavaScript file size that must be loaded by the client and this should be minimized as much as possible. If adding a new dependency is unavoidable, use a tool like [Bundlephobia](https://bundlephobia.com/) to ensure the smallest possible library is used.
- All UI elements must be usable on all common screen sizes, including mobile devices. Be sure to test newly implemented solutions (JavaScript included) on as many screen sizes and device types as possible.
- NetBox aligns with Bootstrap's [supported Browsers and Devices](https://getbootstrap.com/docs/5.1/getting-started/browsers-devices/) list.

## UI Development

To contribute to the NetBox UI, you'll need to review the main [Getting Started guide](getting-started.md) in order to set up your base environment.

### Tools

Once you have a working NetBox development environment, you'll need to install a few more tools to work with the NetBox UI:

- [NodeJS](https://nodejs.org/en/download/) (the LTS release should suffice)
- [Yarn](https://yarnpkg.com/getting-started/install) (version 1)

After Node and Yarn are installed on your system, you'll need to install all the NetBox UI dependencies:

```console
$ cd netbox/project-static
$ yarn
```

!!! warning "Check Your Working Directory"
    You need to be in the `netbox/project-static` directory to run the below `yarn` commands.

### Bundling

In order for the TypeScript and Sass (SCSS) source files to be usable by a browser, they must first be transpiled (TypeScript → JavaScript, Sass → CSS), bundled, and minified. After making changes to TypeScript or Sass source files, run `yarn bundle`.

`yarn bundle` is a wrapper around the following subcommands, any of which can be run individually:

| Command               | Action                                          |
| :-------------------- | :---------------------------------------------- |
| `yarn bundle`         | Bundle TypeScript and Sass (SCSS) source files. |
| `yarn bundle:styles`  | Bundle Sass (SCSS) source files only.           |
| `yarn bundle:scripts` | Bundle TypeScript source files only.            |

All output files will be written to `netbox/project-static/dist`, where Django will pick them up when `manage.py collectstatic` is run.

!!! info "Remember to re-run `manage.py collectstatic`"
    If you're running the development web server — `manage.py runserver` — you'll need to run `manage.py collectstatic` to see your changes.

### Linting, Formatting & Type Checking

Before committing any changes to TypeScript files, and periodically throughout the development process, you should run `yarn validate` to catch formatting, code quality, or type errors.

!!! tip "IDE Integrations"
    If you're using an IDE, it is strongly recommended to install [ESLint](https://eslint.org/docs/user-guide/integrations), [TypeScript](https://github.com/Microsoft/TypeScript/wiki/TypeScript-Editor-Support), and [Prettier](https://prettier.io/docs/en/editors.html) integrations, if available. Most of them will automatically check and/or correct issues in the code as you develop, which can significantly increase your productivity as a contributor.

`yarn validate` is a wrapper around the following subcommands, any of which can be run individually:

| Command                            | Action                                                           |
| :--------------------------------- | :--------------------------------------------------------------- |
| `yarn validate`                    | Run all validation.                                              |
| `yarn validate:lint`               | Validate TypeScript code via [ESLint](https://eslint.org/) only. |
| `yarn validate:types`              | Validate TypeScript code compilation only.                       |
| `yarn validate:formatting`         | Validate code formatting of JavaScript & Sass/SCSS files.        |
| `yarn validate:formatting:styles`  | Validate code formatting Sass/SCSS only.                         |
| `yarn validate:formatting:scripts` | Validate code formatting TypeScript only.                        |

You can also run the following commands to automatically fix formatting issues:

| Command               | Action                                          |
| :-------------------- | :---------------------------------------------- |
| `yarn format`         | Format TypeScript and Sass (SCSS) source files. |
| `yarn format:styles`  | Format Sass (SCSS) source files only.           |
| `yarn format:scripts` | Format TypeScript source files only.            |

