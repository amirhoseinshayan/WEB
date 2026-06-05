import type { ApiTab } from '../../types/apiClient';
import { useAppState } from '../../store/AppContext';

function getTabRequestSummary(tab: ApiTab): string {
  const url = tab.request.url.trim();

  if (!url) {
    return `${tab.request.method} request`;
  }

  return `${tab.request.method} ${url}`;
}

export function RequestTabs() {
  const { state, dispatch } = useAppState();

  const activeTab =
    state.tabs.find((tab) => tab.id === state.activeTabId) ?? state.tabs[0];

  function handleRenameTab(tab: ApiTab) {
    const nextTitle = window.prompt('Tab name:', tab.title);

    if (!nextTitle?.trim()) {
      return;
    }

    dispatch({
      type: 'RENAME_TAB',
      payload: {
        tabId: tab.id,
        title: nextTitle.trim()
      }
    });
  }

  function handleDuplicateActiveTab() {
    if (!activeTab) {
      return;
    }

    dispatch({
      type: 'DUPLICATE_TAB',
      payload: {
        sourceTabId: activeTab.id
      }
    });
  }

  return (
    <div className="tabs-bar" aria-label="Request tabs">
      <div className="tabs-scroll">
        {state.tabs.map((tab) => {
          const isActive = tab.id === state.activeTabId;

          return (
            <div key={tab.id} className={isActive ? 'tab-item active' : 'tab-item'}>
              <button
                type="button"
                className="tab-button"
                title={getTabRequestSummary(tab)}
                onClick={() =>
                  dispatch({
                    type: 'SET_ACTIVE_TAB',
                    payload: { tabId: tab.id }
                  })
                }
                onDoubleClick={() => handleRenameTab(tab)}
              >
                {tab.title}
              </button>

              <button
                type="button"
                className="tab-rename"
                aria-label={`Rename ${tab.title}`}
                title="Rename tab"
                onClick={() => handleRenameTab(tab)}
              >
                ✎
              </button>

              <button
                type="button"
                className="tab-close"
                disabled={state.tabs.length === 1}
                aria-label={`Close ${tab.title}`}
                title={
                  state.tabs.length === 1
                    ? 'At least one tab must remain open.'
                    : 'Close tab'
                }
                onClick={() =>
                  dispatch({
                    type: 'CLOSE_TAB',
                    payload: { tabId: tab.id }
                  })
                }
              >
                ×
              </button>
            </div>
          );
        })}
      </div>

      <button
        type="button"
        className="duplicate-tab-button"
        disabled={!activeTab}
        onClick={handleDuplicateActiveTab}
      >
        Duplicate
      </button>

      <button
        type="button"
        className="add-tab-button"
        onClick={() => dispatch({ type: 'CREATE_TAB' })}
      >
        +
      </button>
    </div>
  );
}