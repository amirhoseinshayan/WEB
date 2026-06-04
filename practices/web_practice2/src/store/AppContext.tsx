import {
  createContext,
  useContext,
  useMemo,
  useReducer,
  type Dispatch,
  type ReactNode
} from 'react';
import { createInitialAppState } from '../constants/defaults';
import type { AppState } from '../types/apiClient';
import { appReducer, type AppAction } from './appReducer';

interface AppContextValue {
  state: AppState;
  dispatch: Dispatch<AppAction>;
}

const AppContext = createContext<AppContextValue | null>(null);

interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  const [state, dispatch] = useReducer(appReducer, undefined, () =>
    createInitialAppState()
  );

  const value = useMemo(
    () => ({
      state,
      dispatch
    }),
    [state]
  );

  // Provide global app state to all child components.
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppState(): AppContextValue {
  const context = useContext(AppContext);

  if (!context) {
    throw new Error('useAppState must be used inside AppProvider.');
  }

  return context;
}