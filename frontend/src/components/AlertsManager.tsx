import React, { useState } from 'react';
import { AlertItem, AlertUpdatePayload } from '../types/api';

interface AlertsManagerProps {
  alerts: AlertItem[];
  onUpdateAlert: (id: string, payload: AlertUpdatePayload) => Promise<void>;
  onRefreshAlerts?: () => void;
}

export const AlertsManager: React.FC<AlertsManagerProps> = ({ alerts, onUpdateAlert }) => {
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);
  const [newStatus, setNewStatus] = useState<'in_review' | 'resolved' | 'dismissed'>('in_review');
  const [notes, setNotes] = useState('');
  const [updating, setUpdating] = useState(false);

  const handleOpenModal = (alert: AlertItem) => {
    setSelectedAlert(alert);
    setNewStatus(alert.status === 'open' ? 'in_review' : (alert.status as any));
    setNotes(alert.notes || '');
  };

  const handleSaveStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAlert) return;
    setUpdating(true);
    try {
      await onUpdateAlert(selectedAlert.id, {
        status: newStatus,
        notes,
      });
      setSelectedAlert(null);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="alerts-manager-view glass-panel">
      <div className="alerts-top-header">
        <div>
          <h2 className="table-title">🔔 Active Fraud Alerts & Investigations</h2>
          <p className="table-subtitle">Review flagged transactions requiring human intervention</p>
        </div>
      </div>

      <div className="alerts-cards-list">
        {alerts.map((alert) => (
          <div key={alert.id} className={`alert-card-item priority-${alert.priority}`}>
            <div className="alert-card-left">
              <div className="alert-icon-ring">⚠️</div>
              <div className="alert-body-content">
                <div className="alert-top-meta">
                  <span className="alert-id-tag">{alert.id}</span>
                  <span className="tx-id-tag">TX: {alert.transaction_id}</span>
                  <span className={`status-pill status-${alert.status}`}>{alert.status.toUpperCase()}</span>
                </div>
                <div className="alert-main-title">{alert.notes || 'Anomalous Activity Flagged'}</div>
                {alert.amount_display && (
                  <div className="alert-amount-display">
                    Flagged Amount: <span className="amount-bold">{alert.amount_display}</span>
                  </div>
                )}
              </div>
            </div>

            <div className="alert-card-actions">
              <span className="alert-time-label">{alert.timestamp_display || 'Recent'}</span>
              <button className="btn btn-outline investigate-btn" onClick={() => handleOpenModal(alert)}>
                Investigate & Resolve
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Investigation Modal */}
      {selectedAlert && (
        <div className="modal-overlay open">
          <div className="modal-box">
            <div className="modal-header">
              <h3>Investigate Alert: {selectedAlert.id}</h3>
              <button className="modal-close-btn" onClick={() => setSelectedAlert(null)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveStatus}>
              <div className="form-group">
                <label className="form-label">Transaction ID</label>
                <input
                  type="text"
                  className="form-input"
                  value={selectedAlert.transaction_id}
                  disabled
                />
              </div>

              <div className="form-group">
                <label className="form-label">Investigation Resolution Status</label>
                <select
                  className="form-select"
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value as any)}
                >
                  <option value="in_review">In Review (Keep Open)</option>
                  <option value="resolved">Resolved (Confirmed Fraud Action Taken)</option>
                  <option value="dismissed">Dismissed (False Positive)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Reviewer Notes</label>
                <textarea
                  className="form-input"
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Enter notes on phone verification, IP audit, or account freeze..."
                />
              </div>

              <div className="modal-actions-row">
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setSelectedAlert(null)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-gold" disabled={updating}>
                  {updating ? 'Saving...' : 'Update Alert Status'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
