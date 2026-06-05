import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  type Dispatch,
  type ReactNode
} from 'react';
import { STORAGE_VERSION } from '../constants/http';
import { APP_STORAGE_KEY } from '../constants/storage';
import { createInitialAppState } from '../constants/defaults';
import type { AppState, ThemeMode } from '../types/apiClient';
import { loadFromStorage, saveToStorage } from '../utils/storage';
import { appReducer, type AppAction } from './appReducer';

interface AppContextValue {
  state: AppState;
  dispatch: Dispatch<AppAction>;
}

const AppContext = createContext<AppContextValue | null>(null);

interface AppProviderProps {
  children: ReactNode;
}

function isValidTheme(theme: unknown): theme is ThemeMode {
  return theme === 'light' || theme === 'dark';
}

function sanitizeLoadedState(loadedState: AppState, fallback: AppState): AppState {
  if (
    !loadedState ||
    loadedState.version !== STORAGE_VERSION ||
    !Array.isArray(loadedState.tabs) ||
    loadedState.tabs.length === 0
  ) {
    return fallback;
  }

  const activeTabExists = loadedState.tabs.some(
    (tab) => tab.id === loadedState.activeTabId
  );

  return {
    ...fallback,
    ...loadedState,
    activeTabId: activeTabExists
      ? loadedState.activeTabId
      : loadedState.tabs[0].id,
    tabs: loadedState.tabs.map((tab) => ({
      ...tab,
      isLoading: false
    })),
    history: Array.isArray(loadedState.history) ? loadedState.history : [],
    collections: Array.isArray(loadedState.collections)
      ? loadedState.collections
      : [],
    theme: isValidTheme(loadedState.theme) ? loadedState.theme : fallback.theme,
    notifications: []
  };
}

function sanitizeStateForStorage(state: AppState): AppState {
  return {
    ...state,
    tabs: state.tabs.map((tab) => ({
      ...tab,
      isLoading: false
    })),
    notifications: []
  };
}

function getInitialState(): AppState {
  const fallback = createInitialAppState();
  const loadedState = loadFromStorage<AppState>(APP_STORAGE_KEY, fallback);

  return sanitizeLoadedState(loadedState, fallback);
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, undefined, getInitialState);

  useEffect(() => {
    // Persist app state for refresh-safe usage.
    saveToStorage(APP_STORAGE_KEY, sanitizeStateForStorage(state));
  }, [state]);

  const value = useMemo(
    () => ({
      state,
      dispatch
    }),
    [state]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppState(): AppContextValue {
  const context = useContext(AppContext);

  if (!context) {
    throw new Error('useAppState must be used inside AppProvider.');
  }

  return context;
}