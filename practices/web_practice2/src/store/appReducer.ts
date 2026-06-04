import type {
  ApiTab,
  AppState,
  RequestConfig,
  RequestError,
  ResponseData,
  ThemeMode
} from '../types/apiClient';
import {
  createDefaultRequestConfig,
  createDefaultTab
} from '../constants/defaults';

export type AppAction =
  | { type: 'CREATE_TAB' }
  | { type: 'CLOSE_TAB'; payload: { tabId: string } }
  | { type: 'SET_ACTIVE_TAB'; payload: { tabId: string } }
  | {
      type: 'UPDATE_ACTIVE_REQUEST';
      payload: { changes: Partial<RequestConfig> };
    }
  | { type: 'RESET_ACTIVE_REQUEST' }
  | { type: 'SET_ACTIVE_ERROR'; payload: { error: RequestError | null } }
  | { type: 'CLEAR_ACTIVE_ERROR' }
  | { type: 'SET_TAB_LOADING'; payload: { tabId: string; isLoading: boolean } }
  | { type: 'SET_TAB_RESPONSE'; payload: { tabId: string; response: ResponseData } }
  | { type: 'SET_TAB_ERROR'; payload: { tabId: string; error: RequestError | null } }
  | { type: 'SET_THEME'; payload: { theme: ThemeMode } };

function updateActiveTab(
  state: AppState,
  updater: (tab: ApiTab) => ApiTab
): AppState {
  return {
    ...state,
    tabs: state.tabs.map((tab) =>
      tab.id === state.activeTabId ? updater(tab) : tab
    )
  };
}

function updateTabById(
  state: AppState,
  tabId: string,
  updater: (tab: ApiTab) => ApiTab
): AppState {
  return {
    ...state,
    tabs: state.tabs.map((tab) => (tab.id === tabId ? updater(tab) : tab))
  };
}

export function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'CREATE_TAB': {
      const nextTabNumber = state.tabs.length + 1;
      const newTab = createDefaultTab(`Request ${nextTabNumber}`);

      return {
        ...state,
        tabs: [...state.tabs, newTab],
        activeTabId: newTab.id
      };
    }

    case 'CLOSE_TAB': {
      if (state.tabs.length === 1) {
        return state;
      }

      const tabIndex = state.tabs.findIndex(
        (tab) => tab.id === action.payload.tabId
      );

      if (tabIndex === -1) {
        return state;
      }

      const nextTabs = state.tabs.filter(
        (tab) => tab.id !== action.payload.tabId
      );

      let nextActiveTabId = state.activeTabId;

      if (state.activeTabId === action.payload.tabId) {
        const fallbackTab = nextTabs[Math.max(0, tabIndex - 1)] ?? nextTabs[0];
        nextActiveTabId = fallbackTab.id;
      }

      return {
        ...state,
        tabs: nextTabs,
        activeTabId: nextActiveTabId
      };
    }

    case 'SET_ACTIVE_TAB': {
      const tabExists = state.tabs.some(
        (tab) => tab.id === action.payload.tabId
      );

      if (!tabExists) {
        return state;
      }

      return {
        ...state,
        activeTabId: action.payload.tabId
      };
    }

    case 'UPDATE_ACTIVE_REQUEST': {
      return updateActiveTab(state, (tab) => ({
        ...tab,
        request: {
          ...tab.request,
          ...action.payload.changes
        },
        // Clear validation errors when the user edits the request.
        error: tab.error?.type === 'validation' ? null : tab.error
      }));
    }

    case 'RESET_ACTIVE_REQUEST': {
      return updateActiveTab(state, (tab) => ({
        ...tab,
        request: createDefaultRequestConfig(),
        response: null,
        error: null,
        isLoading: false
      }));
    }

    case 'SET_ACTIVE_ERROR': {
      return updateActiveTab(state, (tab) => ({
        ...tab,
        error: action.payload.error
      }));
    }

    case 'CLEAR_ACTIVE_ERROR': {
      return updateActiveTab(state, (tab) => ({
        ...tab,
        error: null
      }));
    }

    case 'SET_TAB_LOADING': {
      return updateTabById(state, action.payload.tabId, (tab) => ({
        ...tab,
        isLoading: action.payload.isLoading,
        error: action.payload.isLoading ? null : tab.error,
        response: action.payload.isLoading ? null : tab.response
      }));
    }

    case 'SET_TAB_RESPONSE': {
      return updateTabById(state, action.payload.tabId, (tab) => ({
        ...tab,
        response: action.payload.response,
        error: null,
        isLoading: false
      }));
    }

    case 'SET_TAB_ERROR': {
      return updateTabById(state, action.payload.tabId, (tab) => ({
        ...tab,
        response: null,
        error: action.payload.error,
        isLoading: false
      }));
    }

    case 'SET_THEME': {
      return {
        ...state,
        theme: action.payload.theme
      };
    }

    default:
      return state;
  }
}