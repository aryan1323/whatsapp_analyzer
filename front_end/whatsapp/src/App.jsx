// enhanced_upload_chat.js
import axios from 'axios';
import './UploadChat.css';
import { useState, useEffect } from 'react';

const API_URL = 'https://aryan-whatsapp-2.onrender.com';  // Set your backend API base URL here

export default function UploadChat() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [charts, setCharts] = useState([]);
  const [selectedCharts, setSelectedCharts] = useState(new Set());
  const [stats, setStats] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [zoomImg, setZoomImg] = useState(null);

  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [recommendationText, setRecommendationText] = useState('');
  const [recStatus, setRecStatus] = useState(null);

  // Rotating loading messages...
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const loadingMessages = [
    'Analyzing every message',
    'Reading your chat history',
    'Counting words and emojis',
    'Generating cool charts',
    'Crunching data bytes',
    'Detecting conversation trends',
    'Mapping user activity',
    'Uncovering chat secrets',
    'Building word clouds',
    'Preparing insights for you',
  ];
  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [loading]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(['dragenter', 'dragover'].includes(e.type));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files[0]) uploadChat(e.dataTransfer.files[0]);
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) uploadChat(f);
  };

  const uploadChat = async (f) => {
    setLoading(true);
    setError(null);
    setUsers([]);
    setStats(null);
    setCharts([]);
    setSelectedCharts(new Set());
    setSummary(null);
    try {
      const fd = new FormData();
      fd.append('file', f);
      const uRes = await axios.post(`${API_URL}/analyze`, fd);
      setUsers(uRes.data.users);
      setSelectedUser('');
      const sRes = await axios.get(`${API_URL}/stats`);
      setStats(sRes.data.stats);
      setCharts(sRes.data.charts);
      setSelectedCharts(new Set(sRes.data.charts.map((_, i) => i.toString())));
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleUserChange = async (e) => {
    const u = e.target.value;
    setSelectedUser(u);
    setLoading(true);
    setError(null);
    setSummary(null);
    try {
      const url = u
        ? `${API_URL}/stats?sender=${encodeURIComponent(u)}`
        : `${API_URL}/stats`;
      const res = await axios.get(url);
      setStats(res.data.stats);
      setCharts(res.data.charts);
      setSelectedCharts(new Set(res.data.charts.map((_, i) => i.toString())));
    } catch {
      setError('Failed to load stats');
    } finally {
      setLoading(false);
    }
  };

  const summarizeRange = async () => {
    if (!fromDate || !toDate) return;
    setLoading(true);
    setError(null);
    setSummary(null);
    try {
      const res = await axios.get(`${API_URL}/summary?start=${fromDate}&end=${toDate}`);
      setSummary(res.data);
    } catch {
      setError('Failed to summarize');
    } finally {
      setLoading(false);
    }
  };

  const sendRecommendation = async () => {
    if (!recommendationText.trim()) {
      setRecStatus('Please enter a recommendation.');
      return;
    }
    try {
      setRecStatus('Sending...');
      await axios.post(`${API_URL}/recommendations`, { text: recommendationText });
      setRecStatus('Recommendation sent. Thank you!');
      setRecommendationText('');
    } catch {
      setRecStatus('Failed to send recommendation. Try again later.');
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setUsers([]);
    setSelectedUser('');
    setCharts([]);
    setStats(null);
    setError(null);
    setSelectedCharts(new Set());
    setSummary(null);
    setFromDate('');
    setToDate('');
    setRecommendationText('');
    setRecStatus(null);
  };

  const toggleChartSelection = (id) => {
    const newSel = new Set(selectedCharts);
    newSel.has(id) ? newSel.delete(id) : newSel.add(id);
    setSelectedCharts(newSel);
  };
  const toggleSelectAllCharts = (e) => {
    if (e.target.checked) setSelectedCharts(new Set(charts.map((_, i) => i.toString())));
    else setSelectedCharts(new Set());
  };
  const visibleCharts = selectedCharts.size === 0 ? charts : charts.filter((_, i) => selectedCharts.has(i.toString()));

  return (
    <div className="chat-analyzer-dark">
      {loading && (
        <div className="loading-overlay" aria-live="polite" aria-busy="true" role="alert">
          <div className="loading-content">
            <div className="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </div>
            <div className="loading-message">{loadingMessages[loadingMessageIndex]}</div>
          </div>
        </div>
      )}

      {zoomImg && (
        <div className="zoom-overlay" onClick={() => setZoomImg(null)}>
          <img src={zoomImg} className="zoomed-chart" alt="Zoomed" />
        </div>
      )}

      <header className="header-dark"><h1>💬 WhatsApp Chat Analyzer</h1></header>

      <div className="main-container">
        <aside className="panel-left">
          {!users.length ? (
            <section
              className={`upload-area ${dragActive ? 'dragging' : ''}`}
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
            >
              {loading ? (
                <p className="upload-label">Processing…</p>
              ) : (
                <>
                  <input id="file-upload" type="file" accept=".txt" onChange={handleFileChange} className="file-input" />
                  <label htmlFor="file-upload" className="upload-label">
                    {file ? `📄 ${file.name}` : '📁 Upload Chat (.txt)'}
                  </label>
                </>
              )}
            </section>
          ) : (
            <>
              <div className="selectors">
                <label>
                  👤 Analyze for:
                  <select value={selectedUser} onChange={handleUserChange} disabled={loading}>
                    <option value="">All Users</option>
                    {users.map(u => (
                      <option key={u} value={u}>
                        {u}
                      </option>
                    ))}
                  </select>
                </label>
                <fieldset className="chart-checkboxes">
                  <legend>📊 Select Charts:</legend>
                  <label>
                    <input type="checkbox" checked={selectedCharts.size === charts.length} onChange={toggleSelectAllCharts} /> All Charts
                  </label>
                  {charts.map((c, i) => {
                    const id = i.toString();
                    return (
                      <label key={id}>
                        <input
                          type="checkbox"
                          value={id}
                          checked={selectedCharts.has(id)}
                          onChange={() => toggleChartSelection(id)}
                        />{' '}
                        {c.title}
                      </label>
                    );
                  })}
                </fieldset>

                <div className="date-range">
                  <label>
                    From:{' '}
                    <input
                      type="date"
                      value={fromDate}
                      onChange={(e) => setFromDate(e.target.value)}
                      disabled={loading}
                    />
                  </label>
                  <label>
                    To:{' '}
                    <input
                      type="date"
                      value={toDate}
                      onChange={(e) => setToDate(e.target.value)}
                      disabled={loading}
                    />
                  </label>
                  <button onClick={summarizeRange} disabled={loading || !fromDate || !toDate}>
                    🔍 Summarize
                  </button>
                </div>

                <textarea
                  placeholder="Additional recommendations..."
                  value={recommendationText}
                  onChange={e => setRecommendationText(e.target.value)}
                  disabled={loading}
                  rows={3}
                  style={{ width: '100%', marginTop: '1rem', borderRadius: '6px', padding: '0.5rem', backgroundColor: '#2a2c37', color: '#e6e8ec', border: '1px solid #444' }}
                />
                <button onClick={sendRecommendation} disabled={loading} style={{ marginTop: '0.5rem', width: '100%' }}>
                  📧 Send Recommendation
                </button>
                {recStatus && <p style={{ marginTop: '0.5rem', color: '#7f8dfc' }}>{recStatus}</p>}

                <button className="btn-reset" onClick={resetAnalysis} disabled={loading} style={{ marginTop: '1rem' }}>
                  🔄 New Chat
                </button>
              </div>
            </>
          )}
          {error && <div className="error-dark">{error}</div>}
        </aside>

        <section className="panel-right">
          {stats && (
            <div className="stats-dark" data-user={selectedUser || 'All Users'}>
              <div className="stats-grid">
                <div>
                  <strong>Active Days</strong>
                  <div>{stats.total_days}</div>
                </div>
                <div>
                  <strong>Messages</strong>
                  <div>{stats.total_messages.toLocaleString()}</div>
                </div>
                <div>
                  <strong>Words</strong>
                  <div>{stats.total_words.toLocaleString()}</div>
                </div>
                <div>
                  <strong>Avg Words</strong>
                  <div>{Math.round(stats.total_words / stats.total_messages)}</div>
                </div>
              </div>
            </div>
          )}

          {summary && (
            <div className="summary-dark" style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#2a2c37', borderRadius: '6px' }}>
              <h3>Summary ({fromDate} – {toDate})</h3>
              <p>
                <strong>Total Messages:</strong> {summary.total_messages}
              </p>
              <p>
                <strong>Top Sender:</strong> {summary.top_sender} ({summary.top_sender_count} messages)
              </p>
              <p>
                <strong>Most Active Hour:</strong> {summary.most_active_hour}:00
              </p>
              <p>
                <strong>Top Words:</strong> {summary.top_words.join(', ')}
              </p>
            </div>
          )}

          {visibleCharts.length > 0 && (
            <div className="charts-dark">
              {visibleCharts.map((c, i) => (
                <div key={c.id || i} className="chart-card-dark">
                  <h4>{c.title}</h4>
                  <img src={c.img} alt={c.title} onClick={() => setZoomImg(c.img)} style={{ cursor: 'pointer' }} />
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <footer className="footer-dark" style={{ textAlign: 'center', padding: '1rem', color: '#7f8dfc' }}>
        This project is built by Aryan P. | GitHub:&nbsp;
        <a href="https://github.com/aryan1323" target="_blank" rel="noopener noreferrer" style={{ color: '#7f8dfc' }}>
          aryan1323
        </a>
      </footer>
    </div>
  );
}
