# API Client — Final QA Checklist

Complete this checklist before creating the final submission archive.

## 1. Project Health

* [ ] `npm install` completes successfully.
* [ ] `npm run typecheck` completes without errors.
* [ ] `npm run build` completes without errors.
* [ ] `npm run preview` starts the production preview.
* [ ] The browser console contains no unexpected errors.

## 2. User Interface

* [ ] The application loads correctly.
* [ ] The layout is left-to-right.
* [ ] The sidebar remains beside the main workspace.
* [ ] The sidebar has independent vertical scrolling.
* [ ] The main workspace has independent vertical scrolling.
* [ ] The page has no global horizontal scrollbar.
* [ ] The layout remains usable at small viewport widths.
* [ ] Light Mode works.
* [ ] Dark Mode works.
* [ ] The selected theme remains after refresh.

## 3. Request Methods

Verify each available method can be selected:

* [ ] GET
* [ ] POST
* [ ] PUT
* [ ] PATCH
* [ ] DELETE

## 4. URL Validation

* [ ] An empty URL shows a validation error.
* [ ] A URL without `http://` or `https://` shows an error.
* [ ] An invalid URL structure shows an error.
* [ ] A valid HTTP URL passes validation.
* [ ] A valid HTTPS URL passes validation.

## 5. Query Parameters

* [ ] A parameter row can be added.
* [ ] Parameter keys can be edited.
* [ ] Parameter values can be edited.
* [ ] A parameter can be disabled.
* [ ] A parameter can be enabled.
* [ ] A parameter can be removed.
* [ ] All parameters can be cleared.
* [ ] Enabled parameters appear in the URL.
* [ ] Disabled parameters do not appear in the URL.
* [ ] Existing parameters can be imported from the URL.
* [ ] Duplicate parameter keys remain supported.

## 6. Request Headers

* [ ] A header row can be added.
* [ ] Header keys can be edited.
* [ ] Header values can be edited.
* [ ] A header can be disabled.
* [ ] A header can be enabled.
* [ ] A header can be removed.
* [ ] All headers can be cleared.
* [ ] Disabled headers are not sent.
* [ ] Enabled headers are sent.

## 7. Request Body

* [ ] JSON mode can be selected.
* [ ] Raw mode can be selected.
* [ ] Valid JSON passes validation.
* [ ] Invalid JSON shows a validation error.
* [ ] JSON formatting works.
* [ ] Raw text does not require JSON validation.
* [ ] Clear Body removes the body.
* [ ] POST requests send a body.
* [ ] PUT requests send a body.
* [ ] PATCH requests send a body.

## 8. Sending Requests

Test with a browser-accessible public API.

* [ ] A GET request can be sent.
* [ ] A POST request can be sent.
* [ ] A loading indicator appears while waiting.
* [ ] The Send button is disabled while loading.
* [ ] The request finishes without leaving loading active.
* [ ] URL validation prevents invalid requests.
* [ ] JSON validation prevents invalid JSON requests.

## 9. Response Display

* [ ] HTTP status code is displayed.
* [ ] Status category is displayed.
* [ ] Request duration is displayed.
* [ ] Response timestamp is displayed.
* [ ] Response headers are displayed.
* [ ] JSON response bodies are formatted.
* [ ] Text response bodies are displayed.
* [ ] Empty response bodies are handled.
* [ ] HTTP 4xx responses show an appropriate warning.
* [ ] HTTP 5xx responses show an appropriate warning.

## 10. Error Handling

* [ ] Validation errors are understandable.
* [ ] URL errors identify the URL field.
* [ ] Body errors identify the body field.
* [ ] Network errors are displayed.
* [ ] CORS-related failures are displayed as network failures.
* [ ] Timeout errors are displayed.
* [ ] The application remains usable after an error.

## 11. Clear All

* [ ] Clear All asks for confirmation when data exists.
* [ ] Cancel keeps all request data unchanged.
* [ ] Confirm clears the URL.
* [ ] Confirm clears parameters.
* [ ] Confirm clears headers.
* [ ] Confirm clears the body.
* [ ] Confirm clears the response.
* [ ] Confirm clears errors.
* [ ] Confirm resets the method to GET.
* [ ] Confirm resets body mode to JSON.
* [ ] Only the active tab is cleared.

## 12. History

* [ ] A successful request creates a History item.
* [ ] A failed request creates a History item.
* [ ] History displays request method.
* [ ] History displays response status or failure.
* [ ] A History item can be loaded.
* [ ] A History item can be removed.
* [ ] All History items can be cleared.
* [ ] History remains after refresh.

## 13. Collections

* [ ] A collection can be created.
* [ ] A collection can be renamed.
* [ ] A collection can be deleted.
* [ ] The current request can be saved.
* [ ] Saved request method is preserved.
* [ ] Saved request URL is preserved.
* [ ] Saved request parameters are preserved.
* [ ] Saved request headers are preserved.
* [ ] Saved request body is preserved.
* [ ] A saved request can be loaded.
* [ ] A saved request can be removed.
* [ ] Collections remain after refresh.

## 14. Collection Import and Export

* [ ] One collection can be exported.
* [ ] All collections can be exported.
* [ ] An exported collection can be imported.
* [ ] An exported collection preserves its requests.
* [ ] Imported IDs do not conflict with existing IDs.
* [ ] Invalid JSON displays an error notification.
* [ ] Invalid import data does not crash the application.
* [ ] Imported collections remain after refresh.

## 15. Multiple Tabs

* [ ] A new tab can be created.
* [ ] Tabs can be selected.
* [ ] Tabs can be renamed.
* [ ] Tabs can be duplicated.
* [ ] Tabs can be closed.
* [ ] The final remaining tab cannot be closed.
* [ ] URL is independent between tabs.
* [ ] Parameters are independent between tabs.
* [ ] Headers are independent between tabs.
* [ ] Body is independent between tabs.
* [ ] Response is independent between tabs.
* [ ] Tabs remain after refresh.

## 16. Request Summary and cURL

* [ ] The final URL is displayed.
* [ ] Enabled parameter count is correct.
* [ ] Enabled header count is correct.
* [ ] Body information is correct.
* [ ] Copy URL works.
* [ ] cURL preview is generated.
* [ ] cURL includes the selected method.
* [ ] cURL includes enabled headers.
* [ ] cURL includes a supported request body.
* [ ] Copy cURL works.

## 17. Notifications

* [ ] Copy URL displays a success notification.
* [ ] Copy cURL displays a success notification.
* [ ] Successful collection import displays a notification.
* [ ] Failed collection import displays an error notification.
* [ ] Notifications can be closed manually.
* [ ] Notifications disappear automatically.
* [ ] Notifications do not return after refresh.

## 18. Local Storage

* [ ] Tabs remain after refresh.
* [ ] Theme remains after refresh.
* [ ] History remains after refresh.
* [ ] Collections remain after refresh.
* [ ] Loading state does not remain after refresh.
* [ ] Notifications are not stored.
* [ ] Corrupted or missing stored data does not prevent startup.

## 19. Final Repository Check

* [ ] `node_modules` is not tracked.
* [ ] `dist` is not tracked.
* [ ] No environment secret is committed.
* [ ] `package.json` is committed.
* [ ] `package-lock.json` is committed.
* [ ] Source files are committed.
* [ ] README is committed.
* [ ] The working tree is clean.

## 20. Submission Archive

* [ ] The final project is committed.
* [ ] The archive has the required assignment name.
* [ ] The archive does not contain `node_modules`.
* [ ] The archive does not contain `dist`.
* [ ] The archive contains `src`.
* [ ] The archive contains `package.json`.
* [ ] The archive contains `package-lock.json`.
* [ ] The archive contains `README.md`.
* [ ] The archive extracts successfully.
