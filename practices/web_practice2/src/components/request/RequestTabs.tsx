import { useAppState } from '../../store/AppContext';
import type { ApiTab } from '../../types/apiClient';

function getTabRequestSummary(tab: ApiTab): string {
  const url = tab.request.url.trim();

  if (!url) {
    return `${tab.request.method} request`;
  }

  return `${tab.request.method} ${url}`;
}

function EditIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L8 18l-4 1 1-4Z" />
    </svg>
  );
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
            <div
              key={tab.id}
              className={isActive ? 'tab-item active' : 'tab-item'}
            >
              <button
                type="button"
                className="tab-button"
                title={getTabRequestSummary(tab)}
                onClick={() =>
                  dispatch({
                    type: 'SET_ACTIVE_TAB',
                    payload: {
                      tabId: tab.id
                    }
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
                <EditIcon />
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
                    payload: {
                      tabId: tab.id
                    }
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
        aria-label="Create a new request tab"
        title="Create a new request tab"
        onClick={() => dispatch({ type: 'CREATE_TAB' })}
      >
        +
      </button>
    </div>
  );
}