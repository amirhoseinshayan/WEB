(function (root) {
  'use strict';

  var STORAGE_KEY = 'wp_hw1_notion_lite_state_v1';
  var STATE_VERSION = 1;
  var LOCALE = 'fa';

  function nowIso() {
    return new Date().toISOString();
  }

  function uid(prefix) {
    return [prefix || 'id', Date.now().toString(36), Math.random().toString(36).slice(2, 10)].join('_');
  }

  function deepClone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function stripHtml(value) {
    return String(value || '').replace(/<[^>]*>/g, ' ');
  }

  function normaliseText(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function compareDatesDesc(a, b) {
    return new Date(b).getTime() - new Date(a).getTime();
  }

  function compareDatesAsc(a, b) {
    return new Date(a).getTime() - new Date(b).getTime();
  }

  function createCollator() {
    return new Intl.Collator(LOCALE, { sensitivity: 'base', numeric: true });
  }

  function createDefaultState() {
    var noteId = uid('note');
    var time = nowIso();
    return {
      version: STATE_VERSION,
      preferences: {
        theme: 'system',
        sortBy: 'updated-desc'
      },
      folders: [],
      notes: [
        {
          id: noteId,
          title: 'یادداشت نمونه',
          content: '# خوش آمدید\n\nاین یک یادداشت نمونه است.\n\n- پوشه بسازید\n- یادداشت جدید بسازید\n- از نوار ابزار استفاده کنید\n\n`code`',
          folderId: null,
          pinned: true,
          createdAt: time,
          updatedAt: time
        }
      ]
    };
  }

  function createMemoryStorage() {
    var store = {};
    return {
      getItem: function (key) {
        return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null;
      },
      setItem: function (key, value) {
        store[key] = String(value);
      },
      removeItem: function (key) {
        delete store[key];
      }
    };
  }

  function pickStorage(storageLike) {
    if (storageLike && typeof storageLike.getItem === 'function' && typeof storageLike.setItem === 'function') {
      return storageLike;
    }
    if (typeof localStorage !== 'undefined') {
      return localStorage;
    }
    return createMemoryStorage();
  }

  function sanitiseFolder(folder) {
    return {
      id: String(folder && folder.id ? folder.id : uid('folder')),
      name: String(folder && folder.name ? folder.name : 'پوشه جدید').trim().slice(0, 80) || 'پوشه جدید',
      createdAt: folder && folder.createdAt ? String(folder.createdAt) : nowIso(),
      updatedAt: folder && folder.updatedAt ? String(folder.updatedAt) : nowIso()
    };
  }

  function sanitiseNote(note, knownFolderIds) {
    knownFolderIds = knownFolderIds || new Set();
    var title = String(note && note.title ? note.title : 'یادداشت جدید').trim().slice(0, 120) || 'یادداشت بدون عنوان';
    var content = String(note && note.content ? note.content : '');
    var folderId = note && note.folderId != null ? String(note.folderId) : null;
    if (folderId && !knownFolderIds.has(folderId)) {
      folderId = null;
    }
    return {
      id: String(note && note.id ? note.id : uid('note')),
      title: title,
      content: content,
      folderId: folderId,
      pinned: Boolean(note && note.pinned),
      createdAt: note && note.createdAt ? String(note.createdAt) : nowIso(),
      updatedAt: note && note.updatedAt ? String(note.updatedAt) : nowIso()
    };
  }

  function sanitisePreferences(preferences) {
    var theme = preferences && typeof preferences.theme === 'string' ? preferences.theme : 'system';
    var sortBy = preferences && typeof preferences.sortBy === 'string' ? preferences.sortBy : 'updated-desc';
    if (['light', 'dark', 'system'].indexOf(theme) === -1) {
      theme = 'system';
    }
    if (['title-asc', 'title-desc', 'created-desc', 'created-asc', 'updated-desc', 'updated-asc'].indexOf(sortBy) === -1) {
      sortBy = 'updated-desc';
    }
    return {
      theme: theme,
      sortBy: sortBy
    };
  }

  function sanitiseState(raw) {
    var base = raw && typeof raw === 'object' ? raw : createDefaultState();
    var folders = Array.isArray(base.folders) ? base.folders.map(sanitiseFolder) : [];
    var folderIds = new Set(folders.map(function (folder) {
      return folder.id;
    }));
    var notes = Array.isArray(base.notes) ? base.notes.map(function (note) {
      return sanitiseNote(note, folderIds);
    }) : [];
    if (notes.length === 0) {
      notes = createDefaultState().notes;
    }
    return {
      version: STATE_VERSION,
      preferences: sanitisePreferences(base.preferences),
      folders: folders,
      notes: notes
    };
  }

  function loadState(storageLike) {
    var storage = pickStorage(storageLike);
    var raw = storage.getItem(STORAGE_KEY);
    if (!raw) {
      var fresh = createDefaultState();
      saveState(storage, fresh);
      return fresh;
    }
    try {
      return sanitiseState(JSON.parse(raw));
    } catch (error) {
      var fallback = createDefaultState();
      saveState(storage, fallback);
      return fallback;
    }
  }

  function saveState(storageLike, state) {
    var storage = pickStorage(storageLike);
    var safeState = sanitiseState(state);
    storage.setItem(STORAGE_KEY, JSON.stringify(safeState));
    return safeState;
  }

  function exportState(state) {
    var safeState = sanitiseState(state);
    return JSON.stringify(
      {
        meta: {
          version: STATE_VERSION,
          exportedAt: nowIso(),
          app: 'Notion Lite Homework Solution'
        },
        preferences: safeState.preferences,
        folders: safeState.folders,
        notes: safeState.notes
      },
      null,
      2
    );
  }

  function importStateFromText(text) {
    var parsed;
    try {
      parsed = JSON.parse(text);
    } catch (error) {
      throw new Error('Invalid JSON file.');
    }

    var importPayload = parsed;
    if (parsed && parsed.meta && parsed.notes && parsed.folders) {
      importPayload = {
        preferences: parsed.preferences,
        folders: parsed.folders,
        notes: parsed.notes
      };
    }

    return sanitiseState(importPayload);
  }

  function findFolder(state, folderId) {
    return state.folders.find(function (folder) {
      return folder.id === folderId;
    }) || null;
  }

  function findNote(state, noteId) {
    return state.notes.find(function (note) {
      return note.id === noteId;
    }) || null;
  }

  function touch(entity) {
    entity.updatedAt = nowIso();
    return entity;
  }

  function createFolder(state, name) {
    var folder = sanitiseFolder({ name: name || 'پوشه جدید' });
    state.folders.push(folder);
    return folder;
  }

  function renameFolder(state, folderId, nextName) {
    var folder = findFolder(state, folderId);
    if (!folder) {
      throw new Error('Folder not found.');
    }
    folder.name = String(nextName || '').trim().slice(0, 80) || 'پوشه جدید';
    touch(folder);
    return folder;
  }

  function deleteFolder(state, folderId) {
    state.folders = state.folders.filter(function (folder) {
      return folder.id !== folderId;
    });
    state.notes.forEach(function (note) {
      if (note.folderId === folderId) {
        note.folderId = null;
        touch(note);
      }
    });
  }

  function createNote(state, data) {
    var folderIds = new Set(state.folders.map(function (folder) {
      return folder.id;
    }));
    var note = sanitiseNote(
      {
        title: data && data.title ? data.title : 'یادداشت جدید',
        content: data && data.content ? data.content : '',
        folderId: data && data.folderId != null ? data.folderId : null,
        pinned: data && data.pinned ? data.pinned : false
      },
      folderIds
    );
    state.notes.unshift(note);
    return note;
  }

  function updateNote(state, noteId, patch) {
    var note = findNote(state, noteId);
    if (!note) {
      throw new Error('Note not found.');
    }
    var folderIds = new Set(state.folders.map(function (folder) {
      return folder.id;
    }));
    if (patch && Object.prototype.hasOwnProperty.call(patch, 'title')) {
      note.title = String(patch.title || '').trim().slice(0, 120) || 'یادداشت بدون عنوان';
    }
    if (patch && Object.prototype.hasOwnProperty.call(patch, 'content')) {
      note.content = String(patch.content || '');
    }
    if (patch && Object.prototype.hasOwnProperty.call(patch, 'pinned')) {
      note.pinned = Boolean(patch.pinned);
    }
    if (patch && Object.prototype.hasOwnProperty.call(patch, 'folderId')) {
      var nextFolderId = patch.folderId == null || patch.folderId === '' ? null : String(patch.folderId);
      note.folderId = nextFolderId && folderIds.has(nextFolderId) ? nextFolderId : null;
    }
    touch(note);
    return note;
  }

  function deleteNote(state, noteId) {
    state.notes = state.notes.filter(function (note) {
      return note.id !== noteId;
    });
  }

  function togglePin(state, noteId) {
    var note = findNote(state, noteId);
    if (!note) {
      throw new Error('Note not found.');
    }
    note.pinned = !note.pinned;
    touch(note);
    return note;
  }

  function moveNote(state, noteId, folderId) {
    return updateNote(state, noteId, { folderId: folderId });
  }

  function safeIncludes(haystack, needle) {
    return normaliseText(haystack).toLocaleLowerCase(LOCALE).indexOf(normaliseText(needle).toLocaleLowerCase(LOCALE)) !== -1;
  }

  function getSortedNotes(notes, sortBy) {
    var collator = createCollator();
    var list = notes.slice();
    list.sort(function (a, b) {
      if (a.pinned !== b.pinned) {
        return a.pinned ? -1 : 1;
      }
      if (sortBy === 'title-asc') {
        return collator.compare(a.title, b.title);
      }
      if (sortBy === 'title-desc') {
        return collator.compare(b.title, a.title);
      }
      if (sortBy === 'created-asc') {
        return compareDatesAsc(a.createdAt, b.createdAt);
      }
      if (sortBy === 'created-desc') {
        return compareDatesDesc(a.createdAt, b.createdAt);
      }
      if (sortBy === 'updated-asc') {
        return compareDatesAsc(a.updatedAt, b.updatedAt);
      }
      return compareDatesDesc(a.updatedAt, b.updatedAt);
    });
    return list;
  }

  function filterNotes(notes, query) {
    if (!normaliseText(query)) {
      return notes.slice();
    }
    return notes.filter(function (note) {
      return safeIncludes(note.title, query) || safeIncludes(stripHtml(note.content), query);
    });
  }

  function getVisibleNotes(state, query, sortBy) {
    return getSortedNotes(filterNotes(state.notes, query), sortBy || state.preferences.sortBy);
  }

  function groupNotesByFolder(notes) {
    return notes.reduce(function (acc, note) {
      var key = note.folderId || '__root__';
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(note);
      return acc;
    }, {});
  }

  function makeSelectionWrap(prefix, suffix, selected, placeholder) {
    var body = selected || placeholder || 'text';
    return prefix + body + suffix;
  }

  function insertAtSelection(textareaValue, selectionStart, selectionEnd, prefix, suffix, placeholder) {
    var start = Number(selectionStart || 0);
    var end = Number(selectionEnd || 0);
    var before = textareaValue.slice(0, start);
    var selected = textareaValue.slice(start, end);
    var after = textareaValue.slice(end);
    var inserted = makeSelectionWrap(prefix, suffix, selected, placeholder);
    var hasSelection = end > start;
    var caretStart = start + prefix.length;
    var caretEnd = hasSelection ? start + inserted.length - suffix.length : start + inserted.length - suffix.length;
    var nextValue = before + inserted + after;
    return {
      value: nextValue,
      selectionStart: hasSelection ? caretStart : caretStart,
      selectionEnd: hasSelection ? caretEnd : caretEnd
    };
  }

  function blockWrap(textareaValue, selectionStart, selectionEnd, prefix, suffix, placeholder) {
    var start = Number(selectionStart || 0);
    var end = Number(selectionEnd || 0);
    var before = textareaValue.slice(0, start);
    var selected = textareaValue.slice(start, end);
    var after = textareaValue.slice(end);
    var body = selected || placeholder || '';
    var inserted = prefix + body + suffix;
    return {
      value: before + inserted + after,
      selectionStart: start + prefix.length,
      selectionEnd: start + prefix.length + body.length
    };
  }

  function prefixSelectedLines(textareaValue, selectionStart, selectionEnd, prefixBuilder) {
    var start = Number(selectionStart || 0);
    var end = Number(selectionEnd || 0);
    var blockStart = textareaValue.lastIndexOf('\n', start - 1) + 1;
    var blockEndNext = textareaValue.indexOf('\n', end);
    var blockEnd = blockEndNext === -1 ? textareaValue.length : blockEndNext;
    var before = textareaValue.slice(0, blockStart);
    var selectedBlock = textareaValue.slice(blockStart, blockEnd);
    var after = textareaValue.slice(blockEnd);
    var lines = selectedBlock.split('\n');
    var prefixed = lines.map(function (line, index) {
      return prefixBuilder(index, line) + line;
    }).join('\n');
    return {
      value: before + prefixed + after,
      selectionStart: blockStart,
      selectionEnd: blockStart + prefixed.length
    };
  }

  function sanitiseAllowedHtml(raw) {
    var protectedText = String(raw || '');
    var slots = [];

    function reserve(html) {
      var token = '\uE000HTML' + slots.length + '\uE000';
      slots.push(html);
      return token;
    }

    protectedText = protectedText.replace(/<u>/gi, function () {
      return reserve('<u>');
    });

    protectedText = protectedText.replace(/<\/u>/gi, function () {
      return reserve('</u>');
    });

    protectedText = protectedText.replace(/<span\s+style="color:\s*(#[0-9a-fA-F]{6})\s*">/gi, function (_, color) {
      return reserve('<span style="color:' + color.toLowerCase() + '">');
    });

    protectedText = protectedText.replace(/<\/span>/gi, function () {
      return reserve('</span>');
    });

    return {
      text: protectedText,
      restore: function (html) {
        return html.replace(/\uE000HTML(\d+)\uE000/g, function (_, index) {
          return slots[Number(index)] || '';
        });
      }
    };
  }

  function parseInline(source) {
    var htmlSafe = sanitiseAllowedHtml(String(source || ''));
    var text = escapeHtml(htmlSafe.text);
    var codeSlots = [];

    text = text.replace(/`([^`]+)`/g, function (_, code) {
      var token = '\uE000CODE' + codeSlots.length + '\uE000';
      codeSlots.push('<code>' + code + '</code>');
      return token;
    });

    text = text.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, function (_, label, href) {
      return '<a href="' + href + '" target="_blank" rel="noopener noreferrer">' + label + '</a>';
    });

    text = text.replace(/\*\*([\s\S]+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__([\s\S]+?)__/g, '<strong>$1</strong>');
    text = text.replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, '$1<em>$2</em>');
    text = text.replace(/(^|[^_])_([^_\n]+?)_(?!_)/g, '$1<em>$2</em>');

    text = text.replace(/\uE000CODE(\d+)\uE000/g, function (_, index) {
      return codeSlots[Number(index)] || '';
    });

    text = text.replace(/\n/g, '<br>');

    return htmlSafe.restore(text);
  }

  function parseMarkdown(markdown) {
    var source = String(markdown || '').replace(/\r\n/g, '\n');
    var codeBlocks = [];

    source = source.replace(/```([\s\S]*?)```/g, function (_, code) {
      var token = '\uE000BLOCK' + codeBlocks.length + '\uE000';
      codeBlocks.push('<pre><code>' + escapeHtml(code.trim()) + '</code></pre>');
      return token;
    });

    var lines = source.split('\n');
    var html = [];
    var paragraph = [];
    var listMode = null;

    function flushParagraph() {
      if (paragraph.length) {
        html.push('<p>' + parseInline(paragraph.join('\n')) + '</p>');
        paragraph = [];
      }
    }

    function closeList() {
      if (listMode) {
        html.push('</' + listMode + '>');
        listMode = null;
      }
    }

    lines.forEach(function (line) {
      var trimmed = line.trim();

      if (/^\uE000BLOCK\d+\uE000$/.test(trimmed)) {
        flushParagraph();
        closeList();
        html.push(trimmed);
        return;
      }

      if (!trimmed) {
        flushParagraph();
        closeList();
        return;
      }

      var headingMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (headingMatch) {
        flushParagraph();
        closeList();
        var level = headingMatch[1].length;
        html.push('<h' + level + '>' + parseInline(headingMatch[2]) + '</h' + level + '>');
        return;
      }

      var ulMatch = trimmed.match(/^[-*]\s+(.*)$/);
      if (ulMatch) {
        flushParagraph();
        if (listMode !== 'ul') {
          closeList();
          html.push('<ul>');
          listMode = 'ul';
        }
        html.push('<li>' + parseInline(ulMatch[1]) + '</li>');
        return;
      }

      var olMatch = trimmed.match(/^\d+\.\s+(.*)$/);
      if (olMatch) {
        flushParagraph();
        if (listMode !== 'ol') {
          closeList();
          html.push('<ol>');
          listMode = 'ol';
        }
        html.push('<li>' + parseInline(olMatch[1]) + '</li>');
        return;
      }

      if (listMode) {
        closeList();
      }
      paragraph.push(trimmed);
    });

    flushParagraph();
    closeList();

    var joined = html.join('');
    joined = joined.replace(/\uE000BLOCK(\d+)\uE000/g, function (_, index) {
      return codeBlocks[Number(index)] || '';
    });

    return joined || '<p class="empty-preview">هنوز محتوایی وجود ندارد.</p>';
  }

  function createAppModel(storageLike) {
    var storage = pickStorage(storageLike);
    var state = loadState(storage);

    function commit() {
      state = saveState(storage, state);
      return state;
    }

    return {
      getState: function () {
        return deepClone(state);
      },
      replaceState: function (nextState) {
        state = sanitiseState(nextState);
        return commit();
      },
      createFolder: function (name) {
        var folder = createFolder(state, name);
        commit();
        return folder;
      },
      renameFolder: function (folderId, name) {
        var folder = renameFolder(state, folderId, name);
        commit();
        return folder;
      },
      deleteFolder: function (folderId) {
        deleteFolder(state, folderId);
        return commit();
      },
      createNote: function (data) {
        var note = createNote(state, data || {});
        commit();
        return note;
      },
      updateNote: function (noteId, patch) {
        var note = updateNote(state, noteId, patch || {});
        commit();
        return note;
      },
      deleteNote: function (noteId) {
        deleteNote(state, noteId);
        return commit();
      },
      togglePin: function (noteId) {
        var note = togglePin(state, noteId);
        commit();
        return note;
      },
      moveNote: function (noteId, folderId) {
        var note = moveNote(state, noteId, folderId);
        commit();
        return note;
      },
      setTheme: function (theme) {
        state.preferences.theme = sanitisePreferences({ theme: theme, sortBy: state.preferences.sortBy }).theme;
        return commit();
      },
      setSortBy: function (sortBy) {
        state.preferences.sortBy = sanitisePreferences({ theme: state.preferences.theme, sortBy: sortBy }).sortBy;
        return commit();
      },
      exportState: function () {
        return exportState(state);
      },
      importState: function (text) {
        state = importStateFromText(text);
        return commit();
      },
      findNote: function (noteId) {
        return findNote(state, noteId);
      },
      findFolder: function (folderId) {
        return findFolder(state, folderId);
      },
      getVisibleNotes: function (query, sortBy) {
        return getVisibleNotes(state, query, sortBy);
      },
      groupedNotes: function (query, sortBy) {
        return groupNotesByFolder(getVisibleNotes(state, query, sortBy));
      }
    };
  }

  root.NotionLiteCore = {
    STORAGE_KEY: STORAGE_KEY,
    STATE_VERSION: STATE_VERSION,
    LOCALE: LOCALE,
    nowIso: nowIso,
    uid: uid,
    createDefaultState: createDefaultState,
    createMemoryStorage: createMemoryStorage,
    sanitiseState: sanitiseState,
    loadState: loadState,
    saveState: saveState,
    exportState: exportState,
    importStateFromText: importStateFromText,
    createFolder: createFolder,
    renameFolder: renameFolder,
    deleteFolder: deleteFolder,
    createNote: createNote,
    updateNote: updateNote,
    deleteNote: deleteNote,
    togglePin: togglePin,
    moveNote: moveNote,
    findNote: findNote,
    findFolder: findFolder,
    getVisibleNotes: getVisibleNotes,
    groupNotesByFolder: groupNotesByFolder,
    insertAtSelection: insertAtSelection,
    blockWrap: blockWrap,
    prefixSelectedLines: prefixSelectedLines,
    parseMarkdown: parseMarkdown,
    escapeHtml: escapeHtml,
    stripHtml: stripHtml,
    normaliseText: normaliseText,
    createAppModel: createAppModel
  };
})(window);