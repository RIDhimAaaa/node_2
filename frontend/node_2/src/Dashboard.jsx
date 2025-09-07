// Dashboard.jsx - Universal Web Scraping Platform Dashboard
import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'

function Dashboard({ session }) {
  const [trackers, setTrackers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newTracker, setNewTracker] = useState({
    name: '',
    target_url: '',
    search_term: ''
  })

  const handleSignOut = async () => {
    await supabase.auth.signOut()
  }

  const fetchTrackers = async () => {
    try {
      if (!session) return

      const response = await fetch('http://localhost:8000/trackers', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTrackers(data)
      } else {
        console.error('Error response:', response.status, response.statusText)
        const errorText = await response.text()
        console.error('Error details:', errorText)
      }
    } catch (error) {
      console.error('Error fetching trackers:', error)
    } finally {
      setLoading(false)
    }
  }

  const addTracker = async (e) => {
    e.preventDefault()
    try {
      if (!session) return

      const response = await fetch('http://localhost:8000/trackers', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: newTracker.name,
          target_url: newTracker.target_url,
          search_term: newTracker.search_term
        })
      })

      if (response.ok) {
        setNewTracker({ 
          name: '', 
          target_url: '', 
          search_term: '' 
        })
        setShowAddForm(false)
        fetchTrackers() // Refresh the list
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail}`)
      }
    } catch (error) {
      console.error('Error adding tracker:', error)
      alert('Failed to add tracker')
    }
  }

  const refreshTracker = async (trackerId) => {
    try {
      if (!session) return

      const response = await fetch(`http://localhost:8000/trackers/${trackerId}/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        fetchTrackers() // Refresh the list to show updated status
      }
    } catch (error) {
      console.error('Error refreshing tracker:', error)
    }
  }

  const getDomainIcon = (url) => {
    if (url.includes('gndu')) return '🎓'
    if (url.includes('passport')) return '🛂'
    if (url.includes('visa')) return '✈️'
    if (url.includes('gov')) return '🏛️'
    return '🌐'
  }

  useEffect(() => {
    fetchTrackers()
  }, [])

  return (
    <div className="container">
      <div className="dashboard-header">
        <div>
          <h1>�️ Universal Web Scraper</h1>
          <p>Welcome back, {session.user.email}!</p>
          <span className="platform-subtitle">Scrape any website, track any data, get notified instantly</span>
        </div>
        <button onClick={handleSignOut} className="button secondary">
          Sign Out
        </button>
      </div>
      
      <div className="tracker-list">
        <div className="list-header">
          <h3>Your Active Scrapers</h3>
          <button 
            onClick={() => setShowAddForm(true)} 
            className="button"
            disabled={showAddForm}
          >
            + Add New Scraper
          </button>
        </div>

        {showAddForm && (
          <div className="add-tracker-form">
            <h4>Add New Web Scraper</h4>
            <form onSubmit={addTracker}>
              <div className="form-group">
                <label>Scraper Name:</label>
                <input
                  type="text"
                  value={newTracker.name}
                  onChange={(e) => setNewTracker({...newTracker, name: e.target.value})}
                  placeholder="e.g., My Result Tracker"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Target URL:</label>
                <input
                  type="url"
                  value={newTracker.target_url}
                  onChange={(e) => setNewTracker({...newTracker, target_url: e.target.value})}
                  placeholder="https://example.com/check-status"
                  required
                />
                <small>The website URL you want to scrape</small>
              </div>
              
              <div className="form-group">
                <label>Search Term/ID:</label>
                <input
                  type="text"
                  value={newTracker.search_term}
                  onChange={(e) => setNewTracker({...newTracker, search_term: e.target.value})}
                  placeholder="Use DEMO123 for testing"
                  required
                />
                <small>What to search for on the page (roll number, application ID, etc.)</small>
              </div>
              
              <div className="form-actions">
                <button type="submit" className="button">Add Scraper</button>
                <button 
                  type="button" 
                  onClick={() => setShowAddForm(false)} 
                  className="button secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
        
        {loading ? (
          <div className="loading">Loading your scrapers...</div>
        ) : trackers.length > 0 ? (
          trackers.map((tracker) => {
            return (
              <div key={tracker.id} className="tracker-item">
                <div className="tracker-item-info">
                  <div className="tracker-header">
                    <span className="tracker-icon">{getDomainIcon(tracker.target_url)}</span>
                    <strong>{tracker.name}</strong>
                    <span className="tracker-type">Web Scraper</span>
                  </div>
                  <span className="tracker-url">🔗 {tracker.target_url}</span>
                  <span className="tracker-id">🔍 Searching for: {tracker.search_term}</span>
                  <span className="tracker-date">Added: {new Date(tracker.created_at).toLocaleDateString()}</span>
                </div>
                <div className="tracker-item-status">
                  <div className="status-text">{tracker.last_status || 'No status yet'}</div>
                  <button 
                    onClick={() => refreshTracker(tracker.id)}
                    className="button small"
                  >
                    🔄 Scrape Now
                  </button>
                </div>
              </div>
            )
          })
        ) : (
          <div className="empty-state">
            <h3>🕷️ No scrapers yet</h3>
            <p>Add your first web scraper to start monitoring any website!</p>
            <div className="demo-suggestions">
              <h4>Try these demo URLs:</h4>
              <ul>
                <li><strong>GNDU Results:</strong> http://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx (use DEMO123)</li>
                <li><strong>Any website:</strong> Just paste the URL and add a search term!</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
