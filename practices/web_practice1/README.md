# Notion Lite

Notion Lite is a lightweight note-taking web application inspired by a simplified version of Notion.  
It is built only with **HTML**, **CSS**, and **JavaScript**. No external libraries, packages, frameworks, or modules are used.

The app supports note management, folders, search, sorting, Markdown preview, themes, and JSON import/export.  
All data is stored locally in the browser using `localStorage`.

---

## Project Structure

```text
.
├── index.html
├── README.md
├── data/
│   └── demo-data.json
└── src/
    ├── css/
    │   └── styles.css
    └── js/
        ├── core.js
        └── app.js
```

---

## Features

- Create, edit, delete, and pin notes
- Create, rename, and delete folders
- Move notes between folders
- Show pinned notes, folder notes, and notes without folders
- Search by note title, note content, and folder name
- Sort folders, pinned notes, root notes, and notes inside each folder
- Live Markdown preview
- Markdown toolbar for common formatting actions
- Light, dark, and system theme support
- Auto-save using browser `localStorage`
- Export all data as JSON
- Import data from JSON
- Responsive layout
- Right-to-left friendly interface for Persian content

---

## How to Run

This project does not need installation.

Use **VS Code Live Server**:

1. Open the project folder in VS Code.
2. Install the **Live Server** extension if it is not installed.
3. Open `index.html`.
4. Click **Go Live** in the bottom-right corner of VS Code.

The project usually opens at:

```text
http://127.0.0.1:5500/index.html
```

You can also right-click on `index.html` and choose:

```text
Open with Live Server
```

---

## File Descriptions

### `index.html`

The main HTML file of the project.  
It contains the page structure, including the sidebar, search box, sort selector, theme selector, note editor, Markdown toolbar, preview panel, and import/export controls.

It loads the project files in this order:

```html
<link rel="stylesheet" href="src/css/styles.css">
<script src="src/js/core.js"></script>
<script src="src/js/app.js"></script>
```

`core.js` must be loaded before `app.js`.

---

### `src/css/styles.css`

Contains all styles of the application, including:

- Main layout
- Sidebar design
- Note cards
- Folder cards
- Editor and preview panels
- Markdown toolbar
- Light and dark themes
- Responsive design

---

### `src/js/core.js`

Contains the main logic of the application.  
This file does not use any external module or package.

It handles:

- Creating the default app state
- Loading and saving data with `localStorage`
- Creating, updating, deleting, and pinning notes
- Creating, renaming, and deleting folders
- Moving notes between folders
- Sorting and filtering notes
- Grouping notes by folder
- Importing and exporting JSON data
- Parsing Markdown-like text into safe HTML
- Helper functions for text formatting

The file exposes the core logic through:

```js
window.NotionLiteCore
```

---

### `src/js/app.js`

Connects the user interface to the core logic.

It handles:

- Selecting DOM elements
- Rendering sidebar sections
- Rendering folders and notes
- Rendering the editor and live preview
- Handling user clicks and input events
- Handling search and sorting
- Handling theme changes
- Handling Markdown toolbar actions
- Handling JSON import and export
- Updating the UI after every change

---

### `data/demo-data.json`

A sample JSON file for testing the import feature.  
You can import it from inside the app to quickly add sample folders and notes.

---

## How the App Works

When the app starts:

1. `index.html` loads the UI.
2. `core.js` creates the main logic object.
3. `app.js` creates the app model using `NotionLiteCore`.
4. The app tries to load saved data from `localStorage`.
5. If no saved data exists, a default note is created.
6. The sidebar, editor, and preview are rendered.
7. Every user action updates the state and saves it automatically.

---

## Data Model

The app state has this structure:

```js
{
  version: 1,
  preferences: {
    theme: "system",
    sortBy: "updated-desc"
  },
  folders: [],
  notes: []
}
```

Each note contains:

```js
{
  id: "note_id",
  title: "Note title",
  content: "Note content",
  folderId: null,
  pinned: false,
  createdAt: "date",
  updatedAt: "date"
}
```

Each folder contains:

```js
{
  id: "folder_id",
  name: "Folder name",
  createdAt: "date",
  updatedAt: "date"
}
```

---

## Search

The search box filters results by:

- Note title
- Note content
- Folder name

If a folder name matches the search query, the folder and its notes are displayed.

---

## Sorting

The app supports sorting by:

- Title ascending
- Title descending
- Created date ascending
- Created date descending
- Updated date ascending
- Updated date descending

Sorting is applied to:

- Folders
- Pinned notes
- Notes without folders
- Notes inside each folder

---

## Markdown Preview

The editor supports a simple Markdown-like syntax.

Examples:

````md
# Heading

**Bold text**

*Italic text*

<u>Underlined text</u>

- First item
- Second item

1. First item
2. Second item

`inline code`

```js
console.log("Hello");
```

[Example](https://example.com)

<span style="color:#ff0000">Red text</span>