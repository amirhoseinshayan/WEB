import { useAppState } from '../../store/AppContext';

export function RequestTabs() {
  const { state, dispatch } = useAppState();

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
                onClick={() =>
                  dispatch({
                    type: 'SET_ACTIVE_TAB',
                    payload: { tabId: tab.id }
                  })
                }
              >
                {tab.title}
              </button>

              <button
                type="button"
                className="tab-close"
                disabled={state.tabs.length === 1}
                aria-label={`Close ${tab.title}`}
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
        className="add-tab-button"
        onClick={() => dispatch({ type: 'CREATE_TAB' })}
      >
        +
      </button>
    </div>
  );
}