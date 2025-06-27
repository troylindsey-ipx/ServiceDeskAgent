import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-text">IT Service Center</span>
          </div>
          <nav className="nav">
            <a href="#services">Services</a>
            <a href="#status">System Status</a>
            <a href="#knowledge">Knowledge Base</a>
            <a href="#contact">Contact</a>
          </nav>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <h1>AI-Powered Voice Support</h1>
            <p className="hero-subtitle">Experience the future of IT support with our intelligent voice assistant</p>
            
            <div className="voice-demo-section">
              <div className="demo-badge">🎧 LIVE DEMO</div>
              <h2>Talk to Our AI Support Agent</h2>
              <p>Get instant help by speaking naturally - no typing required!</p>
              
              <button className="primary-voice-button" onClick={handleSupportClick}>
                Speak to an Agent Now
              </button>
              
              <div className="demo-features">
                <div className="feature">
                  <span className="feature-icon">🗣️</span>
                  <span>Natural Speech Recognition</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">🤖</span>
                  <span>AI-Powered Responses</span>
                </div>
                <div className="feature">
                  <span className="feature-icon">🎫</span>
                  <span>Automatic Ticket Creation</span>
                </div>
              </div>
            </div>

            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">24/7</span>
                <span className="stat-label">AI Available</span>
              </div>
              <div className="stat">
                <span className="stat-number">&lt;2sec</span>
                <span className="stat-label">Response Time</span>
              </div>
              <div className="stat">
                <span className="stat-number">Voice</span>
                <span className="stat-label">Enabled</span>
              </div>
            </div>
          </div>
        </section>

        <section className="services" id="services">
          <div className="container">
            <h2>How Can We Help You Today?</h2>
            <div className="service-grid">
              <div className="service-card">
                <div className="service-icon">🎧</div>
                <h3>Live Support</h3>
                <p>Talk directly with our IT specialists for immediate assistance</p>
                <button className="service-button" onClick={handleSupportClick}>
                  Start Voice Chat
                </button>
              </div>
              <div className="service-card">
                <div className="service-icon">🎫</div>
                <h3>Submit Ticket</h3>
                <p>Create a support ticket for non-urgent issues</p>
                <button className="service-button">Create Ticket</button>
              </div>
              <div className="service-card">
                <div className="service-icon">📚</div>
                <h3>Knowledge Base</h3>
                <p>Find answers to common questions and troubleshooting guides</p>
                <button className="service-button">Browse Articles</button>
              </div>
              <div className="service-card">
                <div className="service-icon">📊</div>
                <h3>System Status</h3>
                <p>Check the current status of all IT systems and services</p>
                <button className="service-button">View Status</button>
              </div>
            </div>
          </div>
        </section>

        <section className="quick-actions">
          <div className="container">
            <h2>Quick Actions</h2>
            <div className="action-grid">
              <div className="action-item">
                <span className="action-icon">🔐</span>
                <span>Password Reset</span>
              </div>
              <div className="action-item">
                <span className="action-icon">📧</span>
                <span>Email Issues</span>
              </div>
              <div className="action-item">
                <span className="action-icon">🖨️</span>
                <span>Printer Problems</span>
              </div>
              <div className="action-item">
                <span className="action-icon">💻</span>
                <span>Software Installation</span>
              </div>
              <div className="action-item">
                <span className="action-icon">🌐</span>
                <span>Network Connectivity</span>
              </div>
              <div className="action-item">
                <span className="action-icon">🔧</span>
                <span>Hardware Support</span>
              </div>
            </div>
          </div>
        </section>

        <section className="contact-info">
          <div className="container">
            <div className="contact-grid">
              <div className="contact-card">
                <h3>Emergency Support</h3>
                <p>For critical system outages</p>
                <div className="contact-detail">
                  <span className="contact-icon">📞</span>
                  <span>(555) 123-HELP</span>
                </div>
              </div>
              <div className="contact-card">
                <h3>General Support</h3>
                <p>For standard IT requests</p>
                <div className="contact-detail">
                  <span className="contact-icon">✉️</span>
                  <span>support@company.com</span>
                </div>
              </div>
              <div className="contact-card">
                <h3>Office Hours</h3>
                <p>Monday - Friday</p>
                <div className="contact-detail">
                  <span className="contact-icon">🕒</span>
                  <span>8:00 AM - 6:00 PM EST</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="container">
          <p>&copy; 2024 IT Service Center. All rights reserved.</p>
          <p>Powered by ServiceDeskAgent</p>
        </div>
      </footer>

      {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
    </div>
  )
}

export default App
