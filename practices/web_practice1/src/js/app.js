(function () {
  'use strict';

  var Core = window.NotionLiteCore;
  var model = Core.createAppModel();
  var ui = {
    currentNoteId: null,
    searchQuery: '',
    saveTimer: null,
    lastSelectionStart: 0,
    lastSelectionEnd: 0
  };

  var refs = {
    body: document.body,
    sidebar: document.querySelector('.sidebar'),
    sidebarToggle: document.getElementById('sidebarToggle'),
    searchInput: document.getElementById('searchInput'),
    sortSelect: document.getElementById('sortSelect'),
    themeSelect: document.getElementById('themeSelect'),
    newNoteButton: document.getElementById('newNoteButton'),
    newFolderButton: document.getElementById('newFolderButton'),
    exportButton: document.getElementById('exportButton'),
    importButton: document.getElementById('importButton'),
    importFileInput: document.getElementById('importFileInput'),
    pinnedNotesList: document.getElementById('pinnedNotesList'),
    foldersList: document.getElementById('foldersList'),
    rootNotesList: document.getElementById('rootNotesList'),
    pinnedCount: document.getElementById('pinnedCount'),
    foldersCount: document.getElementById('foldersCount'),
    rootNotesCount: document.getElementById('rootNotesCount'),
    noteTitleInput: document.getElementById('noteTitleInput'),
    noteContentInput: document.getElementById('noteContentInput'),
    folderSelect: document.getElementById('folderSelect'),
    pinButton: document.getElementById('pinButton'),
    deleteNoteButton: document.getElementById('deleteNoteButton'),
    previewPanel: document.getElementById('previewPanel'),
    saveStatus: document.getElementById('saveStatus'),
    emptyState: document.getElementById('emptyState'),
    editorCard: document.getElementById('editorCard'),
    markdownToolbar: document.getElementById('markdownToolbar'),
    colorInput: document.getElementById('colorInput')
  };

  function getState() {
    return model.getState();
  }

  function getCurrentNote() {
    return model.findNote(ui.currentNoteId);
  }

  function ensureCurrentNote() {
    var state = getState();
    var exists = ui.currentNoteId && model.findNote(ui.currentNoteId);
    if (exists) {
      return;
    }
    ui.currentNoteId = state.notes.length ? state.notes[0].id : null;
  }

  function toLocaleDate(iso) {
    if (!iso) {
      return '-';
    }
    return new Date(iso).toLocaleString('fa-IR', {
      dateStyle: 'short',
      timeStyle: 'short'
    });
  }

  function applyTheme(theme) {
    refs.body.dataset.theme = theme;
  }

  function flashSaved(message) {
    refs.saveStatus.textContent = message || 'ذخیره شد';
    clearTimeout(ui.saveTimer);
    ui.saveTimer = setTimeout(function () {
      refs.saveStatus.textContent = 'ذخیره شد';
    }, 1200);
  }

  function smallNoteCard(note, currentNoteId) {
    var activeClass = note.id === currentNoteId ? ' active' : '';
    var pin = note.pinned ? '📌 ' : '';
    return (
      '<button type="button" class="note-card' + activeClass + '" data-role="open-note" data-note-id="' + note.id + '">' +
      '<div class="note-card-header"><span class="note-title">' + pin + Core.escapeHtml(note.title) + '</span></div>' +
      '<div class="note-snippet">' + Core.escapeHtml(Core.normaliseText(Core.stripHtml(note.content)).slice(0, 100) || 'بدون محتوا') + '</div>' +
      '<div class="note-meta"><span>ویرایش: ' + Core.escapeHtml(toLocaleDate(note.updatedAt)) + '</span></div>' +
      '</button>'
    );
  }

  function renderPinned(notes) {
    refs.pinnedCount.textContent = String(notes.length);
    refs.pinnedNotesList.innerHTML = notes.length
      ? notes.map(function (note) { return smallNoteCard(note, ui.currentNoteId); }).join('')
      : '<div class="empty-box">هیچ یادداشت پین‌شده‌ای پیدا نشد.</div>';
  }

  function renderRootNotes(notes) {
    refs.rootNotesCount.textContent = String(notes.length);
    refs.rootNotesList.innerHTML = notes.length
      ? notes.map(function (note) { return smallNoteCard(note, ui.currentNoteId); }).join('')
      : '<div class="empty-box">یادداشت بدون پوشه‌ای وجود ندارد.</div>';
  }

  function getCleanSearchQuery() {
    return Core.normaliseText(ui.searchQuery).toLocaleLowerCase(Core.LOCALE);
  }

  function textIncludes(value, query) {
    return Core.normaliseText(value).toLocaleLowerCase(Core.LOCALE).indexOf(query) !== -1;
  }

  function folderMatchesQuery(folder, query) {
    if (!query) {
      return true;
    }

    return textIncludes(folder.name, query);
  }

  function sortFolders(folders, sortBy) {
    var collator = new Intl.Collator(Core.LOCALE, { sensitivity: 'base', numeric: true });
    var list = folders.slice();

    list.sort(function (a, b) {
      if (sortBy === 'title-asc') {
        return collator.compare(a.name, b.name);
      }

      if (sortBy === 'title-desc') {
        return collator.compare(b.name, a.name);
      }

      if (sortBy === 'created-asc') {
        return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      }

      if (sortBy === 'created-desc') {
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      }

      if (sortBy === 'updated-asc') {
        return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
      }

      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });

    return list;
  }

  function sortNotesForFolder(notes, sortBy) {
    var collator = new Intl.Collator(Core.LOCALE, { sensitivity: 'base', numeric: true });
    var list = notes.slice();

    list.sort(function (a, b) {
      if (sortBy === 'title-asc') {
        return collator.compare(a.title, b.title);
      }

      if (sortBy === 'title-desc') {
        return collator.compare(b.title, a.title);
      }

      if (sortBy === 'created-asc') {
        return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
      }

      if (sortBy === 'created-desc') {
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      }

      if (sortBy === 'updated-asc') {
        return new Date(a.updatedAt).getTime() - new Date(b.updatedAt).getTime();
      }

      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });

    return list;
  }

  function getSearchAwareNotes(state) {
    var query = getCleanSearchQuery();
    var sortBy = state.preferences.sortBy;

    if (!query) {
      return model.getVisibleNotes('', sortBy);
    }

    var directNoteMatches = model.getVisibleNotes(query, sortBy);

    var matchedFolderIds = state.folders
      .filter(function (folder) {
        return folderMatchesQuery(folder, query);
      })
      .map(function (folder) {
        return folder.id;
      });

    var notesFromMatchedFolders = state.notes.filter(function (note) {
      return note.folderId && matchedFolderIds.indexOf(note.folderId) !== -1;
    });

    var byId = {};

    directNoteMatches.concat(notesFromMatchedFolders).forEach(function (note) {
      byId[note.id] = note;
    });

    return model.getVisibleNotes('', sortBy).filter(function (note) {
      return Object.prototype.hasOwnProperty.call(byId, note.id);
    });
  }

  function folderCard(folder, notes) {
    var notesHtml = notes.length
      ? notes.map(function (note) { return smallNoteCard(note, ui.currentNoteId); }).join('')
      : '<div class="empty-box">در این پوشه یادداشتی نیست.</div>';

    return (
      '<section class="folder-card" data-folder-id="' + folder.id + '">' +
      '<div class="folder-card-header">' +
      '<div><strong>' + Core.escapeHtml(folder.name) + '</strong><div class="muted-text">آخرین تغییر: ' + Core.escapeHtml(toLocaleDate(folder.updatedAt)) + '</div></div>' +
      '<div class="folder-actions">' +
      '<button type="button" class="mini-button" data-action="create-note-in-folder" data-folder-id="' + folder.id + '" title="یادداشت جدید">＋</button>' +
      '<button type="button" class="mini-button" data-action="rename-folder" data-folder-id="' + folder.id + '" title="تغییر نام">✎</button>' +
      '<button type="button" class="mini-button" data-action="delete-folder" data-folder-id="' + folder.id + '" title="حذف">✕</button>' +
      '</div></div>' +
      '<div class="folder-notes">' + notesHtml + '</div>' +
      '</section>'
    );
  }

  function renderFolders(state, visibleNotes) {
    var query = getCleanSearchQuery();
    var byFolder = Core.groupNotesByFolder(visibleNotes);

    var foldersToShow = state.folders.filter(function (folder) {
      if (!query) {
        return true;
      }

      return folderMatchesQuery(folder, query) || Boolean(byFolder[folder.id] && byFolder[folder.id].length);
    });

    foldersToShow = sortFolders(foldersToShow, state.preferences.sortBy);

    refs.foldersCount.textContent = String(foldersToShow.length);
    refs.foldersList.innerHTML = foldersToShow.length
      ? foldersToShow.map(function (folder) {
          var folderNotes = sortNotesForFolder(byFolder[folder.id] || [], state.preferences.sortBy);
          return folderCard(folder, folderNotes);
        }).join('')
      : '<div class="empty-box">پوشه‌ای برای نمایش وجود ندارد.</div>';
  }

  function renderFolderSelect(state, note) {
    var options = ['<option value="">بدون پوشه</option>'];
    state.folders.forEach(function (folder) {
      var selected = note && note.folderId === folder.id ? ' selected' : '';
      options.push('<option value="' + folder.id + '"' + selected + '>' + Core.escapeHtml(folder.name) + '</option>');
    });
    refs.folderSelect.innerHTML = options.join('');
  }

  function renderEditor() {
    ensureCurrentNote();
    var state = getState();
    var note = getCurrentNote();

    if (!note) {
      refs.editorCard.classList.add('hidden');
      refs.emptyState.classList.remove('hidden');
      refs.noteTitleInput.value = '';
      refs.noteContentInput.value = '';
      refs.previewPanel.innerHTML = '';
      return;
    }

    refs.editorCard.classList.remove('hidden');
    refs.emptyState.classList.add('hidden');

    refs.noteTitleInput.value = note.title;
    refs.noteContentInput.value = note.content;
    refs.pinButton.textContent = note.pinned ? '📌 حذف پین' : '📌 پین';
    refs.previewPanel.innerHTML = Core.parseMarkdown(note.content);
    renderFolderSelect(state, note);
  }

  function renderSidebarSections() {
    var state = getState();
    var visibleNotes = getSearchAwareNotes(state);
    var pinnedNotes = visibleNotes.filter(function (note) { return note.pinned; });
    var rootNotes = visibleNotes.filter(function (note) { return !note.folderId; });

    renderPinned(pinnedNotes);
    renderFolders(state, visibleNotes);
    renderRootNotes(rootNotes);
    updateSearchAccordionState();
  }

  function renderAll() {
    ensureCurrentNote();
    var state = getState();
    applyTheme(state.preferences.theme);
    refs.sortSelect.value = state.preferences.sortBy;
    refs.themeSelect.value = state.preferences.theme;

    renderSidebarSections();
    renderEditor();
  }

  function selectNote(noteId) {
    ui.currentNoteId = noteId;
    renderAll();
  }

  function syncCurrentNote(patch, message, options) {
    if (!ui.currentNoteId) {
      return;
    }
    var opts = options || {};
    model.updateNote(ui.currentNoteId, patch);

    if (opts.preview) {
      refs.previewPanel.innerHTML = Core.parseMarkdown(refs.noteContentInput.value);
    }
    if (opts.sidebar) {
      renderSidebarSections();
    }
    if (opts.editor) {
      renderEditor();
    }
    flashSaved(message || 'ذخیره خودکار شد');
  }

  function rememberEditorSelection() {
    ui.lastSelectionStart = refs.noteContentInput.selectionStart || 0;
    ui.lastSelectionEnd = refs.noteContentInput.selectionEnd || ui.lastSelectionStart;
  }

  function isTextPart(char) {
    return Boolean(char) && !/[\s()[\]{}<>.,!?،؛:;'"`*#\\\/|]/.test(char);
  }

  function expandSelectionToWord(value, start, end) {
    if (end > start) {
      return {
        start: start,
        end: end
      };
    }

    var left = start;
    var right = end;

    if (left > 0 && isTextPart(value.charAt(left - 1))) {
      while (left > 0 && isTextPart(value.charAt(left - 1))) {
        left -= 1;
      }

      while (right < value.length && isTextPart(value.charAt(right))) {
        right += 1;
      }

      return {
        start: left,
        end: right
      };
    }

    if (right < value.length && isTextPart(value.charAt(right))) {
      while (left > 0 && isTextPart(value.charAt(left - 1))) {
        left -= 1;
      }

      while (right < value.length && isTextPart(value.charAt(right))) {
        right += 1;
      }

      return {
        start: left,
        end: right
      };
    }

    return {
      start: start,
      end: end
    };
  }

  function getEditorSelection(expandWord) {
    if (document.activeElement === refs.noteContentInput) {
      rememberEditorSelection();
    }

    var start = ui.lastSelectionStart || 0;
    var end = ui.lastSelectionEnd || start;

    if (expandWord) {
      return expandSelectionToWord(refs.noteContentInput.value, start, end);
    }

    return {
      start: start,
      end: end
    };
  }

  function applySelectionResult(result) {
    refs.noteContentInput.value = result.value;
    refs.noteContentInput.focus();
    refs.noteContentInput.selectionStart = result.selectionStart;
    refs.noteContentInput.selectionEnd = result.selectionEnd;
    rememberEditorSelection();
    syncCurrentNote({ content: refs.noteContentInput.value }, 'تغییر متن ذخیره شد', { preview: true, sidebar: true });
  }

  function buildLinkInsertion() {
    var textarea = refs.noteContentInput;
    var selection = getEditorSelection(true);
    var start = selection.start;
    var end = selection.end;
    var selected = textarea.value.slice(start, end) || 'link text';
    var url = window.prompt('Link URL', 'https://example.com');

    if (!url) {
      return null;
    }

    var before = textarea.value.slice(0, start);
    var after = textarea.value.slice(end);
    var inserted = '[' + selected + '](' + url + ')';

    return {
      value: before + inserted + after,
      selectionStart: start + 1,
      selectionEnd: start + 1 + selected.length
    };
  }

  function addColorTag(hexColor) {
    var textarea = refs.noteContentInput;
    var selection = getEditorSelection(true);
    var color = String(hexColor || '#2563eb').trim();
    var result = Core.insertAtSelection(
      textarea.value,
      selection.start,
      selection.end,
      '<span style="color:' + color + '">',
      '</span>',
      'colored text'
    );
    applySelectionResult(result);
  }

  function handleToolbarAction(action) {
    var textarea = refs.noteContentInput;

    if (!getCurrentNote()) {
      return;
    }

    if (action === 'link') {
      var linkResult = buildLinkInsertion();
      if (linkResult) {
        applySelectionResult(linkResult);
      }
      return;
    }

    var selection = getEditorSelection(true);
    var start = selection.start;
    var end = selection.end;

    if (action === 'bold') {
      applySelectionResult(Core.insertAtSelection(textarea.value, start, end, '**', '**', 'bold text'));
      return;
    }

    if (action === 'italic') {
      applySelectionResult(Core.insertAtSelection(textarea.value, start, end, '*', '*', 'italic text'));
      return;
    }

    if (action === 'underline') {
      applySelectionResult(Core.insertAtSelection(textarea.value, start, end, '<u>', '</u>', 'underlined text'));
      return;
    }

    if (action === 'inline-code') {
      applySelectionResult(Core.insertAtSelection(textarea.value, start, end, '`', '`', 'code'));
      return;
    }

    if (action === 'code-block') {
      applySelectionResult(Core.blockWrap(textarea.value, start, end, '```\n', '\n```', 'code block'));
      return;
    }

    if (action === 'heading') {
      applySelectionResult(Core.prefixSelectedLines(textarea.value, start, end, function () { return '# '; }));
      return;
    }

    if (action === 'bullet') {
      applySelectionResult(Core.prefixSelectedLines(textarea.value, start, end, function () { return '- '; }));
      return;
    }

    if (action === 'numbered') {
      applySelectionResult(Core.prefixSelectedLines(textarea.value, start, end, function (index) {
        return String(index + 1) + '. ';
      }));
    }
  }

  function handleSidebarClick(event) {
    var openButton = event.target.closest('[data-role="open-note"]');

    if (openButton) {
      selectNote(openButton.dataset.noteId);
      return;
    }

    var actionButton = event.target.closest('[data-action]');

    if (!actionButton) {
      return;
    }

    var action = actionButton.dataset.action;
    var folderId = actionButton.dataset.folderId;

    if (action === 'rename-folder') {
      var folder = model.findFolder(folderId);
      var nextName = window.prompt('Folder name', folder ? folder.name : '');

      if (nextName != null) {
        model.renameFolder(folderId, nextName);
        renderAll();
        flashSaved('پوشه به‌روزرسانی شد');
      }
      return;
    }

    if (action === 'delete-folder') {
      if (window.confirm('این پوشه حذف شود؟ یادداشت‌ها به بخش بدون پوشه منتقل می‌شوند.')) {
        model.deleteFolder(folderId);
        renderAll();
        flashSaved('پوشه حذف شد');
      }
      return;
    }

    if (action === 'create-note-in-folder') {
      var newNote = model.createNote({ title: 'یادداشت جدید', folderId: folderId });
      ui.currentNoteId = newNote.id;
      renderAll();
      refs.noteTitleInput.focus();
      refs.noteTitleInput.select();
      flashSaved('یادداشت جدید ساخته شد');
    }
  }

  function setSectionOpen(section, shouldOpen) {
    section.classList.toggle('is-collapsed', !shouldOpen);
    section.classList.toggle('is-open', shouldOpen);
  }

  function updateSearchAccordionState() {
    var hasQuery = Boolean(getCleanSearchQuery());

    if (!hasQuery) {
      return;
    }

    document.querySelectorAll('.sidebar-section').forEach(function (section) {
      setSectionOpen(section, true);
    });
  }

  function setupSidebarAccordions() {
    var sections = document.querySelectorAll('.sidebar-section');

    sections.forEach(function (section) {
      var header = section.querySelector('.section-title-row');
      var list = section.querySelector('.list-stack');

      if (!header || !list || header.dataset.accordionReady === 'true') {
        return;
      }

      header.dataset.accordionReady = 'true';

      setSectionOpen(section, true);

      header.addEventListener('click', function () {
        var isCollapsed = section.classList.contains('is-collapsed');
        setSectionOpen(section, isCollapsed);
      });
    });
  }

  function downloadTextFile(filename, text) {
    var blob = new Blob([text], { type: 'application/json;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var anchor = document.createElement('a');

    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 0);
  }

  function initEvents() {
    refs.sidebarToggle.addEventListener('click', function () {
      refs.sidebar.classList.toggle('tools-collapsed');
    });

    refs.searchInput.addEventListener('input', function () {
      ui.searchQuery = refs.searchInput.value;
      renderAll();
    });

    refs.sortSelect.addEventListener('change', function () {
      model.setSortBy(refs.sortSelect.value);
      renderAll();
      flashSaved('مرتب‌سازی ذخیره شد');
    });

    refs.themeSelect.addEventListener('change', function () {
      model.setTheme(refs.themeSelect.value);
      renderAll();
      flashSaved('پوسته ذخیره شد');
    });

    refs.newNoteButton.addEventListener('click', function () {
      var current = getCurrentNote();
      var newNote = model.createNote({
        title: 'یادداشت جدید',
        folderId: current ? current.folderId : null
      });

      ui.currentNoteId = newNote.id;
      renderAll();
      refs.noteTitleInput.focus();
      refs.noteTitleInput.select();
      flashSaved('یادداشت جدید ساخته شد');
    });

    refs.newFolderButton.addEventListener('click', function () {
      var folderName = window.prompt('Folder name', 'پوشه جدید');

      if (folderName == null) {
        return;
      }

      model.createFolder(folderName);
      renderAll();
      flashSaved('پوشه جدید ساخته شد');
    });

    refs.exportButton.addEventListener('click', function () {
      downloadTextFile('notion-lite-export.json', model.exportState());
      flashSaved('خروجی JSON ساخته شد');
    });

    refs.importButton.addEventListener('click', function () {
      refs.importFileInput.click();
    });

    refs.importFileInput.addEventListener('change', function () {
      var file = refs.importFileInput.files[0];

      if (!file) {
        return;
      }

      var reader = new FileReader();

      reader.onload = function () {
        try {
          model.importState(String(reader.result || ''));
          ui.currentNoteId = getState().notes.length ? getState().notes[0].id : null;
          renderAll();
          flashSaved('داده‌ها با موفقیت وارد شدند');
        } catch (error) {
          window.alert('خطا در ورود فایل JSON');
        }
      };

      reader.readAsText(file, 'utf-8');
      refs.importFileInput.value = '';
    });

    refs.noteTitleInput.addEventListener('input', function () {
      syncCurrentNote({ title: refs.noteTitleInput.value }, 'عنوان ذخیره شد', { sidebar: true });
    });

    refs.noteContentInput.addEventListener('input', function () {
      rememberEditorSelection();
      syncCurrentNote({ content: refs.noteContentInput.value }, 'محتوا ذخیره شد', { preview: true, sidebar: true });
    });

    refs.noteContentInput.addEventListener('click', rememberEditorSelection);
    refs.noteContentInput.addEventListener('keyup', rememberEditorSelection);
    refs.noteContentInput.addEventListener('select', rememberEditorSelection);

    refs.folderSelect.addEventListener('change', function () {
      syncCurrentNote({ folderId: refs.folderSelect.value || null }, 'پوشه به‌روزرسانی شد', { sidebar: true, editor: true });
    });

    refs.pinButton.addEventListener('click', function () {
      if (!ui.currentNoteId) {
        return;
      }

      model.togglePin(ui.currentNoteId);
      renderAll();
      flashSaved('وضعیت پین تغییر کرد');
    });

    refs.deleteNoteButton.addEventListener('click', function () {
      if (!ui.currentNoteId) {
        return;
      }

      if (window.confirm('این یادداشت حذف شود؟')) {
        model.deleteNote(ui.currentNoteId);
        ui.currentNoteId = null;
        renderAll();
        flashSaved('یادداشت حذف شد');
      }
    });

    refs.markdownToolbar.addEventListener('mousedown', function (event) {
      if (event.target.closest('[data-action]')) {
        event.preventDefault();
      }
    });

    refs.markdownToolbar.addEventListener('click', function (event) {
      var button = event.target.closest('[data-action]');

      if (!button) {
        return;
      }

      handleToolbarAction(button.dataset.action);
    });

    refs.colorInput.addEventListener('input', function () {
      addColorTag(refs.colorInput.value);
    });

    refs.pinnedNotesList.addEventListener('click', handleSidebarClick);
    refs.rootNotesList.addEventListener('click', handleSidebarClick);
    refs.foldersList.addEventListener('click', handleSidebarClick);
  }

  function init() {
    ensureCurrentNote();

    var state = getState();

    refs.searchInput.value = ui.searchQuery;
    refs.sortSelect.value = state.preferences.sortBy;
    refs.themeSelect.value = state.preferences.theme;

    applyTheme(state.preferences.theme);

    if (window.innerWidth <= 860) {
      refs.sidebar.classList.add('tools-collapsed');
    }

    initEvents();
    renderAll();
    setupSidebarAccordions();
  }

  init();
})();