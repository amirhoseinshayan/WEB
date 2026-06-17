import { useAppState } from '../../store/AppContext';

export function TopBar() {
  const { state, dispatch } = useAppState();

  function handleToggleTheme() {
    dispatch({
      type: 'SET_THEME',
      payload: {
        theme: state.theme === 'dark' ? 'light' : 'dark'
      }
    });
  }

  return (
    <header className="topbar">
      <div className="topbar-title">
        <h1>API Client</h1>

        <p className="topbar-description">
          Build, organize, and inspect HTTP requests.
        </p>
      </div>

      <div className="topbar-actions">
        <button
          type="button"
          onClick={() => dispatch({ type: 'CREATE_TAB' })}
        >
          New Tab
        </button>

        <button type="button" onClick={handleToggleTheme}>
          {state.theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </header>
  );
}