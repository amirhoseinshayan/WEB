import type { ChangeEvent } from 'react';
import type { KeyValuePair } from '../../types/apiClient';

interface KeyValueEditorProps {
  title: string;
  description: string;
  rows: KeyValuePair[];
  emptyMessage: string;
  importButtonLabel?: string;
  onAddRow: () => void;
  onUpdateRow: (rowId: string, changes: Partial<KeyValuePair>) => void;
  onRemoveRow: (rowId: string) => void;
  onClearRows: () => void;
  onImportFromUrl?: () => void;
}

export function KeyValueEditor({
  title,
  description,
  rows,
  emptyMessage,
  importButtonLabel,
  onAddRow,
  onUpdateRow,
  onRemoveRow,
  onClearRows,
  onImportFromUrl
}: KeyValueEditorProps) {
  function handleCheckboxChange(
    row: KeyValuePair,
    event: ChangeEvent<HTMLInputElement>
  ) {
    onUpdateRow(row.id, {
      enabled: event.target.checked
    });
  }

  function handleKeyChange(
    row: KeyValuePair,
    event: ChangeEvent<HTMLInputElement>
  ) {
    onUpdateRow(row.id, {
      key: event.target.value
    });
  }

  function handleValueChange(
    row: KeyValuePair,
    event: ChangeEvent<HTMLInputElement>
  ) {
    onUpdateRow(row.id, {
      value: event.target.value
    });
  }

  return (
    <div className="kv-editor">
      <div className="subsection-header">
        <div>
          <h3>{title}</h3>
          <p>{description}</p>
        </div>

        <div className="kv-editor-actions">
          {onImportFromUrl && (
            <button type="button" onClick={onImportFromUrl}>
              {importButtonLabel ?? 'Import'}
            </button>
          )}

          <button type="button" onClick={onAddRow}>
            Add Row
          </button>

          <button type="button" disabled={rows.length === 0} onClick={onClearRows}>
            Clear
          </button>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="empty-state">
          <strong>{emptyMessage}</strong>
          <span>Click Add Row to create your first key-value pair.</span>
        </div>
      ) : (
        <div className="kv-editor-table">
          <div className="kv-editor-head">
            <span>Enabled</span>
            <span>Key</span>
            <span>Value</span>
            <span>Action</span>
          </div>

          {rows.map((row) => (
            <div key={row.id} className="kv-editor-row">
              <label className="checkbox-cell">
                <input
                  type="checkbox"
                  checked={row.enabled}
                  onChange={(event) => handleCheckboxChange(row, event)}
                />
              </label>

              <input
                type="text"
                value={row.key}
                placeholder="parameter"
                onChange={(event) => handleKeyChange(row, event)}
              />

              <input
                type="text"
                value={row.value}
                placeholder="value"
                onChange={(event) => handleValueChange(row, event)}
              />

              <button type="button" onClick={() => onRemoveRow(row.id)}>
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}