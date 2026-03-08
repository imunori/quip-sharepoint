import { useEffect, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';

interface SpreadsheetData {
  headers: string[];
  rows: string[][];
}

const API_BASE = '/api/1';

export function SpreadsheetEditor({ threadId }: { threadId: string }) {
  const [data, setData] = useState<SpreadsheetData>({ headers: [], rows: [] });
  const [editingCell, setEditingCell] = useState<{ row: number; col: number } | null>(null);
  const [editValue, setEditValue] = useState('');
  const [selectedRow, setSelectedRow] = useState<number | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/threads/${threadId}/spreadsheet`)
      .then((r) => r.json())
      .then((d) => setData(d.spreadsheet));
  }, [threadId]);

  const addRow = async () => {
    const cells = data.headers.map(() => '');
    const res = await fetch(`${API_BASE}/threads/spreadsheet/add-row`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ thread_id: threadId, cells }),
    });
    const d = await res.json();
    setData(d.spreadsheet);
  };

  const deleteRow = async (index: number) => {
    const res = await fetch(
      `${API_BASE}/threads/spreadsheet/delete-row?thread_id=${threadId}&row_index=${index}`,
      { method: 'POST' }
    );
    const d = await res.json();
    setData(d.spreadsheet);
    setSelectedRow(null);
  };

  const startEdit = (row: number, col: number) => {
    setEditingCell({ row, col });
    setEditValue(data.rows[row]?.[col] || '');
  };

  const commitEdit = async () => {
    if (!editingCell) return;
    const res = await fetch(`${API_BASE}/threads/spreadsheet/edit-cell`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        thread_id: threadId,
        row: editingCell.row,
        col: editingCell.col,
        value: editValue,
      }),
    });
    const d = await res.json();
    setData(d.spreadsheet);
    setEditingCell(null);
  };

  const addColumn = async () => {
    const header = prompt('列名を入力:');
    if (!header) return;
    const res = await fetch(
      `${API_BASE}/threads/spreadsheet/add-column?thread_id=${threadId}&header=${encodeURIComponent(header)}`,
      { method: 'POST' }
    );
    const d = await res.json();
    setData(d.spreadsheet);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      commitEdit();
    } else if (e.key === 'Escape') {
      setEditingCell(null);
    } else if (e.key === 'Tab') {
      e.preventDefault();
      if (editingCell) {
        commitEdit();
        const nextCol = editingCell.col + 1;
        if (nextCol < data.headers.length) {
          startEdit(editingCell.row, nextCol);
        }
      }
    }
  };

  return (
    <div className="spreadsheet-editor">
      <div className="spreadsheet-toolbar">
        <button className="btn btn-sm" onClick={addRow}>
          <Plus size={14} /> 行を追加
        </button>
        <button className="btn btn-sm" onClick={addColumn}>
          <Plus size={14} /> 列を追加
        </button>
        {selectedRow !== null && (
          <button className="btn btn-sm btn-danger" onClick={() => deleteRow(selectedRow)}>
            <Trash2 size={14} /> 行を削除
          </button>
        )}
      </div>
      <div className="spreadsheet-container">
        <table className="spreadsheet-table">
          <thead>
            <tr>
              <th className="row-number">#</th>
              {data.headers.map((h, i) => (
                <th key={i}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, ri) => (
              <tr
                key={ri}
                className={selectedRow === ri ? 'selected' : ''}
                onClick={() => setSelectedRow(ri)}
              >
                <td className="row-number">{ri + 1}</td>
                {row.map((cell, ci) => (
                  <td
                    key={ci}
                    className={`spreadsheet-cell ${editingCell?.row === ri && editingCell?.col === ci ? 'editing' : ''}`}
                    onDoubleClick={() => startEdit(ri, ci)}
                  >
                    {editingCell?.row === ri && editingCell?.col === ci ? (
                      <input
                        className="cell-input"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={commitEdit}
                        onKeyDown={handleKeyDown}
                        autoFocus
                      />
                    ) : (
                      <span className="cell-value">{cell}</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
            {data.rows.length === 0 && (
              <tr>
                <td colSpan={data.headers.length + 1} className="spreadsheet-empty">
                  データがありません。「行を追加」で始めましょう
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
