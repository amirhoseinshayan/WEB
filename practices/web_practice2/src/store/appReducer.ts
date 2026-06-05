import type {
  ApiTab,
  AppState,
  Collection,
  HistoryItem,
  RequestConfig,
  RequestError,
  ResponseData,
  SavedRequest,
  ThemeMode
} from '../types/apiClient';
import {
  createDefaultRequestConfig,
  createDefaultTab
} from '../constants/defaults';
import { MAX_HISTORY_ITEMS } from '../constants/storage';

export type AppAction =
  | { type: 'CREATE_TAB' }
  | { type: 'DUPLICATE_TAB'; payload: { sourceTabId: string } }
  | { type: 'RENAME_TAB'; payload: { tabId: string; title: string } }
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
  | { type: 'ADD_HISTORY_ITEM'; payload: { item: HistoryItem } }
  | { type: 'REMOVE_HISTORY_ITEM'; payload: { historyItemId: string } }
  | { type: 'CLEAR_HISTORY' }
  | { type: 'LOAD_HISTORY_ITEM'; payload: { request: RequestConfig } }
  | { type: 'CREATE_COLLECTION'; payload: { collection: Collection } }
  | {
      type: 'RENAME_COLLECTION';
      payload: { collectionId: string; name: string; updatedAt: string };
    }
  | { type: 'DELETE_COLLECTION'; payload: { collectionId: string } }
  | {
      type: 'ADD_REQUEST_TO_COLLECTION';
      payload: { collectionId: string; savedRequest: SavedRequest };
    }
  | {
      type: 'REMOVE_REQUEST_FROM_COLLECTION';
      payload: { collectionId: string; savedRequestId: string; updatedAt: string };
    }
  | { type: 'IMPORT_COLLECTIONS'; payload: { collections: Collection[] } }
  | { type: 'LOAD_SAVED_REQUEST'; payload: { request: RequestConfig } }
  | { type: 'SET_THEME'; payload: { theme: ThemeMode } };

function cloneRequestConfig(request: RequestConfig): RequestConfig {
  return {
    ...request,
    params: request.params.map((param) => ({ ...param })),
    headers: request.headers.map((header) => ({ ...header }))
  };
}

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

    case 'DUPLICATE_TAB': {
      const sourceTab = state.tabs.find(
        (tab) => tab.id === action.payload.sourceTabId
      );

      if (!sourceTab) {
        return state;
      }

      const sourceTabIndex = state.tabs.findIndex(
        (tab) => tab.id === sourceTab.id
      );

      const duplicatedTab = createDefaultTab(`${sourceTab.title} Copy`);

      const newTab: ApiTab = {
        ...duplicatedTab,
        request: cloneRequestConfig(sourceTab.request),
        response: null,
        error: null,
        isLoading: false
      };

      const nextTabs = [...state.tabs];
      nextTabs.splice(sourceTabIndex + 1, 0, newTab);

      return {
        ...state,
        tabs: nextTabs,
        activeTabId: newTab.id
      };
    }

    case 'RENAME_TAB': {
      const trimmedTitle = action.payload.title.trim();

      if (!trimmedTitle) {
        return state;
      }

      return {
        ...state,
        tabs: state.tabs.map((tab) =>
          tab.id === action.payload.tabId
            ? {
                ...tab,
                title: trimmedTitle
              }
            : tab
        )
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

    case 'ADD_HISTORY_ITEM': {
      return {
        ...state,
        history: [action.payload.item, ...state.history].slice(
          0,
          MAX_HISTORY_ITEMS
        )
      };
    }

    case 'REMOVE_HISTORY_ITEM': {
      return {
        ...state,
        history: state.history.filter(
          (item) => item.id !== action.payload.historyItemId
        )
      };
    }

    case 'CLEAR_HISTORY': {
      return {
        ...state,
        history: []
      };
    }

    case 'LOAD_HISTORY_ITEM': {
      return updateActiveTab(state, (tab) => ({
        ...tab,
        request: cloneRequestConfig(action.payload.request),
        response: null,
        error: null,
        isLoading: false
      }));
    }

    case 'CREATE_COLLECTION': {
      return {
        ...state,
        collections: [action.payload.collection, ...state.collections]
      };
    }

    case 'RENAME_COLLECTION': {
      return {
        ...state,
        collections: state.collections.map((collection) =>
          collection.id === action.payload.collectionId
            ? {
                ...collection,
                name: action.payload.name,
                updatedAt: action.payload.updatedAt
              }
            : collection
        )
      };
    }

    case 'DELETE_COLLECTION': {
      return {
        ...state,
        collections: state.collections.filter(
          (collection) => collection.id !== action.payload.collectionId
        )
      };
    }

    case 'ADD_REQUEST_TO_COLLECTION': {
      return {
        ...state,
        collections: state.collections.map((collection) =>
          collection.id === action.payload.collectionId
            ? {
                ...collection,
                requests: [
                  action.payload.savedRequest,
                  ...collection.requests
                ],
                updatedAt: action.payload.savedRequest.updatedAt
              }
            : collection
        )
      };
    }

    case 'REMOVE_REQUEST_FROM_COLLECTION': {
      return {
        ...state,
        collections: state.collections.map((collection) =>
          collection.id === action.payload.collectionId
            ? {
                ...collection,
                requests: collection.requests.filter(
                  (request) => request.id !== action.payload.savedRequestId
                ),
                updatedAt: action.payload.updatedAt
              }
            : collection
        )
      };
    }

    case 'IMPORT_COLLECTIONS': {
      return {
        ...state,
        collections: [...action.payload.collections, ...state.collections]
      };
    }

    case 'LOAD_SAVED_REQUEST': {
      return updateActiveTab(state, (tab) => ({
        ...tab,
        request: cloneRequestConfig(action.payload.request),
        response: null,
        error: null,
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