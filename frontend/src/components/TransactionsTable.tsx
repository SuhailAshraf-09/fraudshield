import React, { useState } from 'react';
import { TransactionItem } from '../types/api';

interface TransactionsTableProps {
  transactions: TransactionItem[];
  onSelectTransaction?: (tx: TransactionItem) => void;
}

export const TransactionsTable: React.FC<TransactionsTableProps> = ({
  transactions,
  onSelectTransaction,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTier, setFilterTier] = useState<string>('all');

  const filtered = transactions.filter((tx) => {
    const matchesSearch =
      tx.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tx.merchant_category || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTier =
      filterTier === 'all' ||
      (tx.risk_tier && tx.risk_tier.toLowerCase() === filterTier.toLowerCase());
    return matchesSearch && matchesTier;
  });

  return (
    <div className="transactions-view glass-panel">
      <div className="table-top-toolbar">
        <div>
          <h2 className="table-title">💳 Transactions Ledger</h2>
          <p className="table-subtitle">All real-time audited payments and risk scores</p>
        </div>

        <div className="toolbar-controls">
          <div className="search-box-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              placeholder="Search by ID, merchant..."
              className="toolbar-search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            className="form-select tier-filter-sel"
            value={filterTier}
            onChange={(e) => setFilterTier(e.target.value)}
          >
            <option value="all">All Tiers</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>
      </div>

      <div className="table-responsive">
        <table className="custom-table">
          <thead>
            <tr>
              <th>Transaction ID</th>
              <th>Amount</th>
              <th>Category</th>
              <th>Occurred At</th>
              <th>Risk Score</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? (
              filtered.map((tx) => {
                const amountDisplay = (tx.amount_minor / 100).toLocaleString(undefined, {
                  style: 'currency',
                  currency: tx.currency || 'USD',
                });

                return (
                  <tr key={tx.id} className="table-row-hover">
                    <td className="mono-col">{tx.id}</td>
                    <td className="amount-col">{amountDisplay}</td>
                    <td>
                      <span className="cat-pill">{tx.merchant_category || 'General'}</span>
                    </td>
                    <td className="time-col">
                      {new Date(tx.occurred_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td>
                      <div className="score-cell-group">
                        <span className="score-num">{tx.risk_index ?? '--'}</span>
                        {tx.risk_index !== undefined && (
                          <div className="mini-score-bar">
                            <div
                              className={`bar-fill ${
                                (tx.risk_index || 0) > 70
                                  ? 'bg-red'
                                  : (tx.risk_index || 0) > 40
                                  ? 'bg-gold'
                                  : 'bg-green'
                              }`}
                              style={{ width: `${Math.min(tx.risk_index || 0, 100)}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className={`risk-badge badge-${(tx.risk_tier || 'low').toLowerCase()}`}>
                        {tx.risk_tier || 'NORMAL'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-table-action"
                        onClick={() => onSelectTransaction && onSelectTransaction(tx)}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={7} className="empty-table-cell">
                  No transactions match the selected criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
