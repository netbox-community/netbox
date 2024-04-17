# Markdown

NetBox supports Markdown rendering for certain text fields. Some common examples are provided below. For a complete Markdown reference, please see [Markdownguide.org](https://www.markdownguide.org/basic-syntax/).

## Headings

```no-highlight
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

<h1>Heading 1</h1>
<h2>Heading 2</h2>
<h3>Heading 3</h3>
<h4>Heading 4</h4>
<h5>Heading 5</h5>
<h6>Heading 6</h6>

Alternatively, for H1 and H2, an underline-ish style:

```no-highlight
Heading 1
=========

Heading 2
---------
```

<h1>Heading 1</h1>
<h2>Heading 2</h2>

## Text

```no-highlight
Italicize text with *asterisks* or _underscores_.
```

Italicize text with *asterisks* or _underscores_.

```no-highlight
Bold text with two **asterisks** or __underscores__.
```

Bold text with two **asterisks** or __underscores__.

```no-highlight
Strike text with two tildes. ~~Deleted text.~~
```

Strike text with two tildes. ~~Deleted text.~~

## Line Breaks

By default, Markdown will remove line breaks between successive lines of text. For example:

```no-highlight
This is one line.
And this is another line.
One more line here.
```

This is one line.
And this is another line.
One more line here.

To preserve line breaks, append two spaces to each line (represented below with the `⋅` character).

```no-highlight
This is one line.⋅⋅
And this is another line.⋅⋅
One more line here.
```

This is one line.  
And this is another line.  
One more line here.

## Lists

Use asterisks or hyphens for unordered lists. Indent items by four spaces to start a child list.

```no-highlight
* Alpha
* Bravo
* Charlie
  * Child item 1
  * Child item 2
* Delta
```

* Alpha
* Bravo
* Charlie
    * Child item 1
    * Child item 2
* Delta

Use digits followed by periods for ordered (numbered) lists.

```no-highlight
1. Red
2. Green
3. Blue
    1. Light blue
    2. Dark blue
4. Orange
```

1. Red
2. Green
3. Blue
    1. Light blue
    2. Dark blue
4. Orange

## Links

Text can be rendered as a hyperlink by encasing it in square brackets, followed by a URL in parentheses. A title (text displayed on hover) may optionally be included as well.

```no-highlight
Here's an [example](https://www.example.com) of a link.

And here's [another link](https://www.example.com "Click me!"), this time with a title.
```

Here's an [example](https://www.example.com) of a link.

And here's [another link](https://www.example.com "Click me!"), with a title.

## Images

The syntax for embedding an image is very similar to that used for a hyperlink. Alternate text should always be provided; this will be displayed if the image fails to load. As with hyperlinks, title text is optional.

```no-highlight
![Alternate text](/path/to/image.png "Image title text")
```

## Code Blocks

Single backticks can be used to annotate code inline. Text enclosed by lines of three backticks will be displayed as a code block.

```no-highlight
Paragraphs are rendered in HTML using `<p>` and `</p>` tags.
```

Paragraphs are rendered in HTML using `<p>` and `</p>` tags.

````
```
def my_func(foo, bar):
    # Do something
    return foo * bar
```
````

```no-highlight
def my_func(foo, bar):
    # Do something
    return foo * bar
```

## Tables

Simple tables can be constructed using the pipe character (`|`) to denote columns, and hyphens (`-`) to denote the heading. Inline Markdown can be used to style text within columns.

```no-highlight
| Heading 1 | Heading 2 | Heading 3 |
|-----------|-----------|-----------|
| Row 1     | Alpha     | Red       |
| Row 2     | **Bravo** | Green     |
| Row 3     | Charlie   | ~~Blue~~  |
```

| Heading 1 | Heading 2 | Heading 3 |
|-----------|-----------|-----------|
| _Row 1_   | Alpha     | Red       |
| Row 2     | **Bravo** | Green     |
| Row 3     | Charlie   | ~~Blue~~  |

Colons can be used to align text to the left or right side of a column.

```no-highlight
| Left-aligned | Centered | Right-aligned |
|:-------------|:--------:|--------------:|
| Text         | Text     | Text          |
| Text         | Text     | Text          |
| Text         | Text     | Text          |
```

| Left-aligned | Centered | Right-aligned |
|:-------------|:--------:|--------------:|
| Text         | Text     | Text          |
| Text         | Text     | Text          |
| Text         | Text     | Text          |

## Blockquotes

Text can be wrapped in a blockquote by prepending a right angle bracket (`>`) before each line.

```no-highlight
> I think that I shall never see
> a graph more lovely than a tree.
> A tree whose crucial property
> is loop-free connectivity.
```

> I think that I shall never see
> a graph more lovely than a tree.
> A tree whose crucial property
> is loop-free connectivity.

Markdown removes line breaks by default. To preserve line breaks, append two spaces to each line (represented below with the `⋅` character).

```no-highlight
> I think that I shall never see⋅⋅
> a graph more lovely than a tree.⋅⋅
> A tree whose crucial property⋅⋅
> is loop-free connectivity.
```

> I think that I shall never see  
> a graph more lovely than a tree.  
> A tree whose crucial property  
> is loop-free connectivity.

## Horizontal Rule

A horizontal rule is a single line rendered across the width of the page using a series of three or more hyphens or asterisks. It can be useful for separating sections of content.

```no-highlight
Content

---

More content

***

Final content
```

Content

---

More content

***

Final content
