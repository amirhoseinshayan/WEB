# API Client — Web Programming Homework 2

A complete browser-based API client inspired by tools such as Postman.

This project is implemented with **React**, **TypeScript**, and **Vite**. It allows users to create, configure, send, inspect, save, import, and export HTTP requests directly from the browser.

---

## Overview

The application provides an interactive interface for working with REST APIs.

Each request can contain:

* An HTTP method
* A valid HTTP or HTTPS URL
* Query parameters
* Request headers
* A Raw or JSON body
* An independent response
* An independent error and loading state

The application also supports request history, saved collections, multiple tabs, Local Storage persistence, JSON import/export, theme switching, and request summaries.

---

## Main Features

### HTTP Methods

The following HTTP methods are supported:

* GET
* POST
* PUT
* PATCH
* DELETE

The selected method is stored separately for every request tab.

---

### URL Input and Validation

Before a request is sent, the URL is validated.

The application detects:

* Empty URLs
* URLs without `http://` or `https://`
* Invalid URL structures
* Missing or invalid hosts
* Unsupported protocols

Only valid HTTP and HTTPS URLs can be sent.

---

### Query Parameters

The Query Parameters editor supports:

* Adding rows
* Editing keys and values
* Removing rows
* Enabling and disabling rows
* Clearing all parameters
* Importing query parameters from the entered URL
* Automatically synchronizing enabled parameters with the final URL
* Supporting repeated parameter keys

Disabled or empty query parameters are not added to the final request URL.

---

### Request Headers

The Headers editor supports:

* Adding headers
* Editing header names and values
* Removing headers
* Enabling and disabling headers
* Clearing all headers
* Keeping headers independent between request tabs

Only enabled headers with non-empty names are sent.

When a JSON body is sent and no Content-Type header has been entered, the application automatically adds:

```text
Content-Type: application/json
```

---

### Request Body

Two body modes are supported:

* JSON
* Raw

JSON mode provides:

* JSON syntax validation
* JSON formatting
* Clear error messages for invalid JSON
* Pretty formatting with indentation

Raw mode accepts plain text without JSON validation.

Request bodies are sent for:

* POST
* PUT
* PATCH

For methods that normally do not use a request body, the editor displays an appropriate warning.

---

### Sending HTTP Requests

Requests are sent using the browser Fetch API.

Before sending, the application validates:

* The request URL
* The JSON body when JSON mode is selected

During a request:

* A loading state is displayed
* The Send button becomes disabled
* Request fields cannot be accidentally modified
* The request is automatically cancelled after the configured timeout

The default timeout is:

```text
30 seconds
```

---

### Response Display

The Response panel displays:

* HTTP status code
* HTTP status text
* Status category
* Request duration
* Response timestamp
* Response header count
* Response headers
* Response body

JSON responses are automatically formatted when possible.

The response status is categorized as:

* Informational
* Successful
* Redirection
* Client-side error
* Server-side error

Responses with status codes of 400 or higher are visually displayed as errors.

The Received date is displayed using this format:

```text
DD/MM/YYYY - HH:mm:ss
```

---

### Error Handling

The application handles and displays:

* URL validation errors
* JSON validation errors
* Network failures
* CORS-related failures
* Server connection failures
* Request timeout errors
* Unknown runtime errors
* HTTP error statuses such as 400, 404, and 500

Errors display their type, affected field, message, and additional details when available.

A server response with an error status is still displayed in the Response panel.

---

### Clear All

The `Clear All` button resets the active request tab.

It clears:

* URL
* Query parameters
* Headers
* Request body
* Response
* Errors
* Loading state

It also resets:

* Method to GET
* Body mode to JSON

When the current tab contains data, a confirmation dialog is shown before clearing.

Only the active tab is affected. History and Collections remain unchanged.

---

### Request History

Every sent request is stored in History.

History entries include:

* HTTP method
* URL
* Response status
* Request date and time
* Failed request state

Users can:

* Load a History item into the active tab
* Remove one History item
* Clear all History items

History is persisted in Local Storage and remains available after a page refresh.

---

### Collections

Collections allow users to organize and save requests.

Users can:

* Create collections
* Rename collections
* Delete collections
* Save the current request
* Load saved requests
* Remove saved requests
* Export one collection
* Export all collections
* Import collections from JSON

A saved request preserves:

* Method
* URL
* Query parameters
* Headers
* Body
* Body mode

Collections are persisted in Local Storage.

---

### Collection Import and Export

The project supports JSON import and export.

Supported import structures include:

* A single collection object
* An array of collections
* An object containing a `collections` array

Imported data is validated before being added.

The importer:

* Rejects invalid JSON
* Rejects unsupported structures
* Prevents the application from crashing
* Generates new IDs for imported data
* Preserves request information
* Displays success and error notifications

Exported files can later be imported into the application.

---

### Multiple Request Tabs

Every tab represents an independent request.

Each tab stores its own:

* Method
* URL
* Query parameters
* Headers
* Body
* Body mode
* Response
* Error state
* Loading state

Tabs can be:

* Created
* Selected
* Renamed
* Duplicated
* Closed

The final remaining tab cannot be closed.

When many tabs are open, the tab list becomes horizontally scrollable while the `Duplicate` and `+` controls remain visible.

Tabs are persisted in Local Storage.

---

### Request Summary

The Request Summary panel displays:

* Selected HTTP method
* Number of enabled query parameters
* Number of enabled headers
* Body mode and body size
* Final request URL

It also provides:

* Copy URL
* Copy cURL
* cURL Preview

The generated cURL command includes:

* HTTP method
* Final URL
* Enabled headers
* Supported request body

---

### Notifications

The application contains an internal toast notification system.

Notifications are used for:

* Successful URL copying
* Successful cURL copying
* Successful collection import
* Import validation errors
* File read errors

Notifications:

* Automatically disappear
* Can be closed manually
* Support success, error, warning, and information states
* Are not saved in Local Storage

---

### Theme Support

The application supports:

* Light Mode
* Dark Mode

The selected theme is saved in Local Storage and remains active after refreshing the page.

---

### Responsive Layout

The layout is designed to remain usable across different viewport sizes.

Features include:

* Independent sidebar scrolling
* Independent main workspace scrolling
* No global horizontal page scrollbar
* Scrollable request tabs
* Responsive request and response panels
* Responsive parameter and header editors
* Responsive buttons and controls

---

## Technology Stack

* React
* TypeScript
* Vite
* CSS
* Fetch API
* AbortController
* Browser Local Storage
* Clipboard API

No backend service is required for the application itself.

---

## Project Structure

```text
src/
├── components/
│   ├── layout/
│   │   ├── NotificationCenter.tsx
│   │   ├── Sidebar.tsx
│   │   └── TopBar.tsx
│   ├── request/
│   │   ├── KeyValueEditor.tsx
│   │   ├── RequestLine.tsx
│   │   ├── RequestPanel.tsx
│   │   ├── RequestSummary.tsx
│   │   └── RequestTabs.tsx
│   └── response/
│       └── ResponsePanel.tsx
├── constants/
│   ├── defaults.ts
│   ├── http.ts
│   └── storage.ts
├── store/
│   ├── AppContext.tsx
│   └── appReducer.ts
├── styles/
│   └── global.css
├── types/
│   └── apiClient.ts
├── utils/
│   ├── clipboard.ts
│   ├── collections.ts
│   ├── curl.ts
│   ├── httpClient.ts
│   ├── id.ts
│   ├── queryParams.ts
│   ├── requestBody.ts
│   ├── requestHeaders.ts
│   ├── requestState.ts
│   ├── storage.ts
│   └── url.ts
├── App.tsx
└── main.tsx
```

---

## Installation

Clone or extract the project and enter its directory.

Install dependencies:

```bash
npm install
```

---

## Development Server

Start the development server:

```bash
npm run dev
```

Vite displays the local development URL in the terminal.

The default address is usually:

```text
http://localhost:5173/
```

---

## Type Checking

Run the TypeScript checker:

```bash
npm run typecheck
```

This command checks the project without generating output files.

---

## Production Build

Create a production build:

```bash
npm run build
```

The generated production files are placed in:

```text
dist/
```

The `dist` directory is ignored by Git.

---

## Complete Project Validation

Run TypeScript checking and the production build together:

```bash
npm run check
```

This command runs:

```text
npm run typecheck
npm run build
```

A successful result should finish without TypeScript or Vite errors.

---

## Production Preview

Build the project first, then run:

```bash
npm run preview
```

The preview server is usually available at:

```text
http://localhost:4173/
```

Use `Ctrl + C` in the terminal to stop the server.

---

## Example GET Request

Method:

```text
GET
```

URL:

```text
https://jsonplaceholder.typicode.com/posts/1
```

Expected result:

* Successful status code
* JSON response body
* Response headers
* Request duration
* History entry

---

## Example POST Request

Method:

```text
POST
```

URL:

```text
https://jsonplaceholder.typicode.com/posts
```

Header:

```text
Content-Type: application/json
```

JSON body:

```json
{
  "title": "Test Post",
  "body": "Created from the API Client",
  "userId": 1
}
```

Expected result:

* Successful response
* Formatted response body
* History entry
* Independent response state in the current tab

---

## CORS Notice

The application runs entirely inside the browser.

Some APIs reject requests from browser origins because of Cross-Origin Resource Sharing restrictions.

A CORS error may occur even when:

* The URL is correct
* The server is online
* The API works in tools such as Postman

For reliable browser testing, use APIs that explicitly allow cross-origin requests.

---

## Local Storage

The application stores its persistent state under this key:

```text
web-practice-2-api-client-state
```

Persisted information includes:

* Tabs
* Requests
* History
* Collections
* Theme

Temporary states are not persisted:

* Loading state
* Toast notifications

Removing this Local Storage key resets the application to its initial state.

---

## Git and Ignored Files

The following generated or local files should not be committed:

```text
node_modules/
dist/
build/
.env
.env.*
*.log
.vscode/
.DS_Store
Thumbs.db
```

The following files should be committed:

```text
src/
public/
README.md
package.json
package-lock.json
tsconfig.json
tsconfig.app.json
tsconfig.node.json
vite.config.ts
eslint.config.js
index.html
```

---

## Final Quality Check

Before submission, run:

```bash
npm run check
```

Then verify:

* Light and Dark Mode
* All HTTP methods
* URL validation
* Params editor
* Headers editor
* Raw and JSON bodies
* Successful responses
* 404 and 500 responses
* Network and timeout errors
* Clear All
* History
* Collections
* Import and Export
* Multiple tabs
* Local Storage persistence
* Responsive layout
* Production Preview

---


