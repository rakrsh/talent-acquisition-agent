'use client';

import React, { useState, useEffect } from 'react';
import Head from 'next/head';

// --- Types ---
interface Job {
  title: string;
  company: string;
  location: string;
  url: string;
  source: string;
  posted_date?: string;
}

interface Application {
  title: string;
  company: string;
  location: string;
  url: string;
  source: string;
  applied_date: string;
  status: string;
  notes?: string;
}

// --- Components ---
const StatCard = ({ title, value, icon, color }: { title: string, value: string | number, icon: string, color: string }) => (
  <div className="stat-card">
    <div className={`stat-icon ${color}`}>
      <i className={`fas ${icon}`}></i>
    </div>
    <div className="stat-info">
      <h3>{title}</h3>
      <p>{value}</p>
    </div>
  </div>
);

export default function Dashboard() {
  const [activeView, setActiveView] = useState('dashboard');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [status, setStatus] = useState('Connecting...');

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  useEffect(() => {
    fetchData();
    checkHealth();
  }, [activeView]);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) setStatus('Online');
      else setStatus('Offline');
    } catch {
      setStatus('Offline');
    }
  };

  const fetchData = async () => {
    try {
      const res = await fetch(`${API_BASE}/applications`);
      const data = await res.json();
      setApplications(data.applications || []);
    } catch (err) {
      console.error("Failed to fetch applications", err);
    }
  };

  const handleSearch = async () => {
    setIsSearching(true);
    try {
      const res = await fetch(`${API_BASE}/jobs`);
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (err) {
      console.error("Search failed", err);
    } finally {
      setIsSearching(false);
    }
  };

  const trackApplication = async (job: Job) => {
    try {
      const res = await fetch(`${API_BASE}/applications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(job)
      });
      if (res.ok) {
        fetchData();
        alert(`Tracked application for ${job.company}`);
      }
    } catch (err) {
      console.error("Tracking failed", err);
    }
  };

  return (
    <div className="app-container">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <i className="fas fa-robot"></i>
          <span>JobAgent</span>
        </div>
        <nav>
          <button
            className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveView('dashboard')}
          >
            <i className="fas fa-th-large"></i> Dashboard
          </button>
          <button
            className={`nav-item ${activeView === 'search' ? 'active' : ''}`}
            onClick={() => setActiveView('search')}
          >
            <i className="fas fa-search"></i> Job Search
          </button>
          <button
            className={`nav-item ${activeView === 'applications' ? 'active' : ''}`}
            onClick={() => setActiveView('applications')}
          >
            <i className="fas fa-briefcase"></i> Applications
          </button>
        </nav>
        <div className="sidebar-footer">
          <div className="status-indicator">
            <span className={`dot ${status === 'Online' ? 'online' : 'offline'}`}></span>
            Backend: {status}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="top-bar">
          <h1>{activeView.charAt(0).toUpperCase() + activeView.slice(1)}</h1>
          <div className="user-profile">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
        </header>

        {activeView === 'dashboard' && (
          <section className="view active">
            <div className="stats-grid">
              <StatCard title="Total Jobs" value={jobs.length} icon="fa-search" color="purple" />
              <StatCard title="Applications" value={applications.length} icon="fa-paper-plane" color="blue" />
              <StatCard title="Interviews" value={applications.filter(a => a.status === 'interviewing').length} icon="fa-check-circle" color="green" />
              <StatCard title="Pending" value={applications.filter(a => a.status === 'applied').length} icon="fa-clock" color="orange" />
            </div>

            <div className="card">
              <div className="card-header">
                <h2>Recent Applications</h2>
              </div>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Position</th>
                      <th>Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {applications.slice(0, 5).map((app, i) => (
                      <tr key={i}>
                        <td>{app.company}</td>
                        <td>{app.title}</td>
                        <td>{new Date(app.applied_date).toLocaleDateString()}</td>
                        <td><span className={`badge ${app.status}`}>{app.status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        )}

        {activeView === 'search' && (
          <section className="view active">
            <div className="search-controls">
              <button className="btn-primary" onClick={handleSearch} disabled={isSearching}>
                <i className={`fas ${isSearching ? 'fa-spinner fa-spin' : 'fa-sync-alt'}`}></i>
                {isSearching ? 'Searching...' : 'Run Pipeline Search'}
              </button>
            </div>
            <div className="job-grid">
              {jobs.map((job, i) => (
                <div key={i} className="job-card">
                  <div className="job-header">
                    <div className="company-logo">{job.company.charAt(0)}</div>
                    <span className="job-source">{job.source}</span>
                  </div>
                  <div>
                    <div className="job-title">{job.title}</div>
                    <div className="job-company">{job.company}</div>
                  </div>
                  <div className="job-meta">
                    <span><i className="fas fa-map-marker-alt"></i> {job.location}</span>
                    <span><i className="fas fa-calendar-alt"></i> {job.posted_date || 'Recent'}</span>
                  </div>
                  <div className="job-footer">
                    <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn-outline">View Details</a>
                    <button
                      className="btn-primary"
                      onClick={() => trackApplication(job)}
                      disabled={applications.some(a => a.url === job.url)}
                    >
                      {applications.some(a => a.url === job.url) ? 'Applied' : 'Track App'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {activeView === 'applications' && (
          <section className="view active">
            <div className="kanban-board">
              {['applied', 'interviewing', 'offered', 'rejected'].map(status => (
                <div key={status} className="kanban-column">
                  <div className="column-header">
                    {status.toUpperCase()}
                    <span className="count">{applications.filter(a => a.status === status).length}</span>
                  </div>
                  <div className="kanban-items">
                    {applications.filter(a => a.status === status).map((app, i) => (
                      <div key={i} className="kanban-card">
                        <div style={{ fontWeight: 700 }}>{app.title}</div>
                        <div style={{ color: 'var(--primary)', fontSize: '13px' }}>{app.company}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '11px', marginTop: '8px' }}>
                          {new Date(app.applied_date).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <style jsx>{`
        /* Embedded styles for specific components to maintain premium look */
        .sidebar {
          width: 260px;
          background-color: var(--bg-sidebar);
          display: flex;
          flex-direction: column;
          padding: 24px;
          border-right: 1px solid var(--border);
        }
        .nav-item {
          background: none;
          border: none;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: 12px;
          color: var(--text-muted);
          font-weight: 500;
          cursor: pointer;
          text-align: left;
          width: 100%;
          font-family: inherit;
          transition: all 0.2s ease;
        }
        .nav-item:hover { background-color: rgba(99, 102, 241, 0.1); color: var(--primary); }
        .nav-item.active { background-color: var(--primary); color: white; }

        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
          padding: 32px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 24px;
          margin-bottom: 32px;
        }

        .stat-card {
          background-color: var(--bg-card);
          padding: 24px;
          border-radius: 20px;
          display: flex;
          align-items: center;
          gap: 20px;
          border: 1px solid var(--border);
        }

        .job-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 24px;
        }

        .job-card {
          background-color: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: 20px;
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .btn-primary {
          background-color: var(--primary);
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 10px;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .btn-outline {
          border: 1px solid var(--border);
          color: var(--text-main);
          padding: 8px 16px;
          border-radius: 8px;
          text-decoration: none;
          font-size: 14px;
        }

        .kanban-board {
          display: flex;
          gap: 24px;
          overflow-x: auto;
        }

        .kanban-column {
          min-width: 280px;
          background: rgba(2, 6, 23, 0.3);
          border-radius: 20px;
          padding: 16px;
        }

        .badge {
          padding: 4px 10px;
          border-radius: 100px;
          font-size: 11px;
          font-weight: 600;
        }
        .badge.applied { background: rgba(59, 130, 246, 0.1); color: var(--blue); }

        .status-indicator {
          font-size: 12px;
          color: var(--text-muted);
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: #64748b; }
        .dot.online { background: var(--green); }
        .dot.offline { background: var(--red); }
      `}</style>
    </div>
  );
}
