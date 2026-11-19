import React, { useState } from 'react';
import { apiService } from '../services/api';
import { ApiStatus } from '../types/api';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  status: ApiStatus;
  onStatusUpdated: (newStatus: ApiStatus) => void;
}

export const BackendSettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  status,
  onStatusUpdated,
}) => {
  const [apiUrl, setApiUrl] = useState(status.baseUrl);
  const [testing, setTesting] = useState(false);

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    setTesting(true);
    apiService.setBaseUrl(apiUrl);
    const newStatus = await apiService.checkHealth();
    onStatusUpdated(newStatus);
    setTesting(false);
  };

  return (
    <div className="modal-overlay open">
      <div className="modal-box">
        <div className="modal-header">
          <h3>⚙️ Backend Integration Settings</h3>
          <button className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="settings-body">
          <div className="status-overview-card">
            <div className="status-row">
              <span className="status-label">Current Integration Mode:</span>
              <span className={`status-badge-val ${status.connected ? 'badge-live' : 'badge-demo'}`}>
                {status.connected ? '🟢 LIVE FASTAPI BACKEND' : '🟡 STANDALONE DEMO MODE'}
              </span>
            </div>
            {status.connected && (
              <div className="latency-row">
                <span>API Latency:</span> <strong>{status.latencyMs} ms</strong>
              </div>
            )}
          </div>

          <div className="form-group" style={{ marginTop: '16px' }}>
            <label className="form-label">FastAPI Backend URL</label>
            <input
              type="text"
              className="form-input"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8000/api/v1"
            />
            <small style={{ color: '#888', display: 'block', marginTop: '6px' }}>
              Default FastAPI local port is 8000. When backend is running, predictions & transactions stream live from SQLite / PostgreSQL.
            </small>
          </div>

          <div className="modal-actions-row">
            <button className="btn btn-outline" onClick={handleTestConnection} disabled={testing}>
              {testing ? 'Checking /health/live...' : 'Test Connection'}
            </button>
            <button className="btn btn-gold" onClick={onClose}>
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
