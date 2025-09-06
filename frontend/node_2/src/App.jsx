import { useState, useEffect } from 'react'
import { supabase } from './supabaseClient'
import Auth from './Auth'
import Dashboard from './Dashboard'
import './App.css'

function App() {
  const [session, setSession] = useState(null)
  const [profileSynced, setProfileSynced] = useState(false)

  const syncProfile = async (session) => {
    try {
      const response = await fetch('http://localhost:8000/auth/sync-profile', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        console.log('Profile synced successfully')
        setProfileSynced(true)
      } else {
        console.error('Profile sync failed')
        setProfileSynced(true) // Continue anyway
      }
    } catch (error) {
      console.error('Error syncing profile:', error)
      setProfileSynced(true) // Continue anyway
    }
  }

  useEffect(() => {
    // Check for an active session when the app loads
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session) {
        syncProfile(session)
      }
    })

    // Listen for changes in authentication state (login, logout)
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setProfileSynced(false) // Reset sync state
      if (session) {
        syncProfile(session)
      }
    })

    // Cleanup the listener when the component is unmounted
    return () => subscription.unsubscribe()
  }, [])

  return (
    <div className="container">
      {!session ? (
        <Auth />
      ) : !profileSynced ? (
        <div className="loading">Setting up your profile...</div>
      ) : (
        // We pass the session key to force a re-render of the Dashboard on login
        <Dashboard key={session.user.id} session={session} />
      )}
    </div>
  )
}

export default App
