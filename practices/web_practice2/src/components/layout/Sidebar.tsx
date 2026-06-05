import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent
} from 'react';
import type {
  Collection,
  HistoryItem,
  RequestConfig,
  SavedRequest
} from '../../types/apiClient';
import { useAppState } from '../../store/AppContext';
import {
  createCollectionsExportPayload,
  downloadJsonFile,
  getAllCollectionsExportFileName,
  getCollectionExportFileName,
  parseCollectionsJson
} from '../../utils/collections';
import { createId } from '../../utils/id';

function formatDate(value: string): string {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function getShortUrl(url: string): string {
  if (url.length <= 70) {
    return url;
  }

  return `${url.slice(0, 67)}...`;
}

function cloneRequestConfig(request: RequestConfig): RequestConfig {
  return {
    ...request,
    params: request.params.map((param) => ({ ...param })),
    headers: request.headers.map((header) => ({ ...header }))
  };
}

function createDefaultRequestName(request: RequestConfig): string {
  const url = request.url.trim();

  if (!url) {
    return `${request.method} Untitled Request`;
  }

  return `${request.method} ${getShortUrl(url)}`;
}

function createCollection(name: string): Collection {
  const now = new Date().toISOString();

  return {
    id: createId('collection'),
    name,
    requests: [],
    createdAt: now,
    updatedAt: now
  };
}

function createSavedRequest(name: string, request: RequestConfig): SavedRequest {
  const now = new Date().toISOString();

  return {
    id: createId('saved-request'),
    name,
    request: cloneRequestConfig(request),
    createdAt: now,
    updatedAt: now
  };
}

function HistoryStatus({ item }: { item: HistoryItem }) {
  if (item.responseStatus === null) {
    return <span className="history-status failed">Failed</span>;
  }

  if (item.responseStatus >= 200 && item.responseStatus < 300) {
    return <span className="history-status success">{item.responseStatus}</span>;
  }

  if (item.responseStatus >= 400) {
    return <span className="history-status error">{item.responseStatus}</span>;
  }

  return <span className="history-status neutral">{item.responseStatus}</span>;
}

export function Sidebar() {
  const { state, dispatch } = useAppState();
  const importInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(
    null
  );

  const activeTab =
    state.tabs.find((tab) => tab.id === state.activeTabId) ?? state.tabs[0];

  const selectedCollection = useMemo(
    () =>
      state.collections.find(
        (collection) => collection.id === selectedCollectionId
      ) ?? null,
    [selectedCollectionId, state.collections]
  );

  useEffect(() => {
    if (state.collections.length === 0) {
      setSelectedCollectionId(null);
      return;
    }

    const selectedExists = state.collections.some(
      (collection) => collection.id === selectedCollectionId
    );

    if (!selectedExists) {
      setSelectedCollectionId(state.collections[0].id);
    }
  }, [selectedCollectionId, state.collections]);

  function handleCreateCollection() {
    const name = window.prompt('Collection name:', 'New Collection');

    if (!name?.trim()) {
      return;
    }

    const collection = createCollection(name.trim());

    dispatch({
      type: 'CREATE_COLLECTION',
      payload: {
        collection
      }
    });

    setSelectedCollectionId(collection.id);
  }

  function handleRenameCollection(collection: Collection) {
    const name = window.prompt('New collection name:', collection.name);

    if (!name?.trim()) {
      return;
    }

    dispatch({
      type: 'RENAME_COLLECTION',
      payload: {
        collectionId: collection.id,
        name: name.trim(),
        updatedAt: new Date().toISOString()
      }
    });
  }

  function handleDeleteCollection(collection: Collection) {
    const confirmed = window.confirm(
      `Delete "${collection.name}" and all saved requests inside it?`
    );

    if (!confirmed) {
      return;
    }

    dispatch({
      type: 'DELETE_COLLECTION',
      payload: {
        collectionId: collection.id
      }
    });
  }

  function handleSaveActiveRequest(collection: Collection) {
    const defaultName = createDefaultRequestName(activeTab.request);
    const name = window.prompt('Request name:', defaultName);

    if (!name?.trim()) {
      return;
    }

    dispatch({
      type: 'ADD_REQUEST_TO_COLLECTION',
      payload: {
        collectionId: collection.id,
        savedRequest: createSavedRequest(name.trim(), activeTab.request)
      }
    });
  }

  function handleRemoveSavedRequest(
    collection: Collection,
    savedRequest: SavedRequest
  ) {
    const confirmed = window.confirm(`Remove "${savedRequest.name}"?`);

    if (!confirmed) {
      return;
    }

    dispatch({
      type: 'REMOVE_REQUEST_FROM_COLLECTION',
      payload: {
        collectionId: collection.id,
        savedRequestId: savedRequest.id,
        updatedAt: new Date().toISOString()
      }
    });
  }

  function handleExportAllCollections() {
    if (state.collections.length === 0) {
      return;
    }

    downloadJsonFile(
      getAllCollectionsExportFileName(),
      createCollectionsExportPayload(state.collections)
    );
  }

  function handleExportCollection(collection: Collection) {
    downloadJsonFile(
      getCollectionExportFileName(collection),
      createCollectionsExportPayload([collection])
    );
  }

  async function handleImportFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    try {
      const text = await file.text();
      const result = parseCollectionsJson(text);

      if (result.error) {
        dispatch({
          type: 'ADD_NOTIFICATION',
          payload: {
            notification: {
              id: createId('notification'),
              type: 'error',
              title: 'Import failed',
              message: result.error
            }
          }
        });

        return;
      }

      dispatch({
        type: 'IMPORT_COLLECTIONS',
        payload: {
          collections: result.collections
        }
      });

      setSelectedCollectionId(result.collections[0]?.id ?? null);

      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          notification: {
            id: createId('notification'),
            type: 'success',
            title: 'Collections imported',
            message: `Imported ${result.collections.length} collection${
              result.collections.length === 1 ? '' : 's'
            }.`
          }
        }
      });
    } catch {
      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          notification: {
            id: createId('notification'),
            type: 'error',
            title: 'File read failed',
            message: 'Could not read this file. Please try another JSON file.'
          }
        }
      });
    } finally {
      event.target.value = '';
    }
  }

  return (
    <aside className="sidebar">
      <section className="sidebar-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Saved</p>
            <h2>Collections</h2>
          </div>

          <span className="counter-badge">{state.collections.length}</span>
        </div>

        <div className="collections-toolbar">
          <button type="button" onClick={handleCreateCollection}>
            New Collection
          </button>

          <button
            type="button"
            onClick={() => importInputRef.current?.click()}
          >
            Import JSON
          </button>

          <button
            type="button"
            disabled={state.collections.length === 0}
            onClick={handleExportAllCollections}
          >
            Export All
          </button>

          <input
            ref={importInputRef}
            type="file"
            accept="application/json,.json"
            className="hidden-file-input"
            onChange={handleImportFile}
          />
        </div>

        {state.collections.length === 0 ? (
          <div className="empty-state compact">
            <strong>No collections yet</strong>
            <span>Create or import a collection to get started.</span>
          </div>
        ) : (
          <div className="collections-area">
            <div className="collection-list">
              {state.collections.map((collection) => (
                <button
                  key={collection.id}
                  type="button"
                  className={
                    collection.id === selectedCollectionId
                      ? 'collection-list-item active'
                      : 'collection-list-item'
                  }
                  onClick={() => setSelectedCollectionId(collection.id)}
                >
                  <strong>{collection.name}</strong>
                  <span>{collection.requests.length} requests</span>
                </button>
              ))}
            </div>

            {selectedCollection && (
              <div className="collection-detail">
                <div className="collection-detail-header">
                  <div>
                    <h3>{selectedCollection.name}</h3>
                    <span>
                      Updated {formatDate(selectedCollection.updatedAt)}
                    </span>
                  </div>

                  <div className="collection-detail-actions">
                    <button
                      type="button"
                      onClick={() => handleSaveActiveRequest(selectedCollection)}
                    >
                      Save Current
                    </button>

                    <button
                      type="button"
                      onClick={() => handleExportCollection(selectedCollection)}
                    >
                      Export
                    </button>

                    <button
                      type="button"
                      onClick={() => handleRenameCollection(selectedCollection)}
                    >
                      Rename
                    </button>

                    <button
                      type="button"
                      className="danger-button"
                      onClick={() => handleDeleteCollection(selectedCollection)}
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {selectedCollection.requests.length === 0 ? (
                  <div className="empty-state compact">
                    <strong>No saved requests</strong>
                    <span>Use Save Current to add the active request.</span>
                  </div>
                ) : (
                  <div className="saved-request-list">
                    {selectedCollection.requests.map((savedRequest) => (
                      <article
                        key={savedRequest.id}
                        className="saved-request-item"
                      >
                        <button
                          type="button"
                          className="saved-request-load"
                          onClick={() =>
                            dispatch({
                              type: 'LOAD_SAVED_REQUEST',
                              payload: {
                                request: savedRequest.request
                              }
                            })
                          }
                        >
                          <div className="saved-request-top">
                            <span>{savedRequest.request.method}</span>
                            <small>{formatDate(savedRequest.updatedAt)}</small>
                          </div>

                          <strong>{savedRequest.name}</strong>

                          <small title={savedRequest.request.url}>
                            {savedRequest.request.url
                              ? getShortUrl(savedRequest.request.url)
                              : 'No URL'}
                          </small>
                        </button>

                        <button
                          type="button"
                          className="saved-request-remove"
                          aria-label="Remove saved request"
                          onClick={() =>
                            handleRemoveSavedRequest(
                              selectedCollection,
                              savedRequest
                            )
                          }
                        >
                          ×
                        </button>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </section>

      <section className="sidebar-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Recent</p>
            <h2>History</h2>
          </div>

          <span className="counter-badge">{state.history.length}</span>
        </div>

        {state.history.length === 0 ? (
          <div className="empty-state compact">
            <strong>No requests sent yet</strong>
            <span>Request history will appear here after sending requests.</span>
          </div>
        ) : (
          <>
            <div className="history-list">
              {state.history.map((item) => (
                <article key={item.id} className="history-item">
                  <button
                    type="button"
                    className="history-load-button"
                    onClick={() =>
                      dispatch({
                        type: 'LOAD_HISTORY_ITEM',
                        payload: {
                          request: item.request
                        }
                      })
                    }
                  >
                    <div className="history-item-top">
                      <span className="history-method">
                        {item.request.method}
                      </span>
                      <HistoryStatus item={item} />
                    </div>

                    <strong title={item.request.url}>
                      {getShortUrl(item.request.url)}
                    </strong>

                    <span>{formatDate(item.createdAt)}</span>
                  </button>

                  <button
                    type="button"
                    className="history-remove-button"
                    aria-label="Remove history item"
                    onClick={() =>
                      dispatch({
                        type: 'REMOVE_HISTORY_ITEM',
                        payload: {
                          historyItemId: item.id
                        }
                      })
                    }
                  >
                    ×
                  </button>
                </article>
              ))}
            </div>

            <button
              type="button"
              className="clear-history-button"
              onClick={() => dispatch({ type: 'CLEAR_HISTORY' })}
            >
              Clear History
            </button>
          </>
        )}
      </section>

      <section className="sidebar-card">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Current</p>
            <h2>Active Tab</h2>
          </div>
        </div>

        <dl className="sidebar-summary">
          <div>
            <dt>Tab</dt>
            <dd>{activeTab?.title ?? 'None'}</dd>
          </div>

          <div>
            <dt>Method</dt>
            <dd>{activeTab?.request.method ?? '-'}</dd>
          </div>

          <div>
            <dt>URL</dt>
            <dd>{activeTab?.request.url || 'Empty'}</dd>
          </div>
        </dl>
      </section>
    </aside>
  );
}