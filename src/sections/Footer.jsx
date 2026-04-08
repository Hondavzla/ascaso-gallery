export default function Footer() {
  const labelStyle = {
    fontFamily: 'DM Sans, sans-serif',
    fontSize: '10px',
    letterSpacing: '0.2em',
    textTransform: 'uppercase',
    color: '#C9A84C',
    marginBottom: '20px',
  }

  const bodyStyle = {
    fontFamily: 'DM Sans, sans-serif',
    fontSize: '13px',
    color: '#FAF9F6',
    opacity: 0.6,
    lineHeight: 1.8,
    margin: 0,
  }

  const cityStyle = {
    fontFamily: 'Cormorant Garamond, serif',
    fontSize: '24px',
    fontWeight: 300,
    color: '#FAF9F6',
    margin: '0 0 8px 0',
  }

  return (
    <footer style={{ background: '#0D0D0D' }}>
      {/* Main columns */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '64px',
        padding: '80px 10vw 40px',
      }}>
        {/* Left — Logo & contact */}
        <div>
          <img
            src="/logo.svg"
            alt="Ascaso Gallery"
            style={{ height: '40px', filter: 'invert(1) brightness(2)', marginBottom: '24px', display: 'block' }}
          />
          <p style={bodyStyle}>
            1325 NE 1st Ave.<br />
            Miami, FL 33132, USA<br />
            T: +1 (305) 571.9410<br />
            @ascasogallery<br />
            www.ascasogallery.com
          </p>
        </div>

        {/* Center — Navigation */}
        <div>
          <p style={labelStyle}>Navigation</p>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {['Artists', 'Exhibitions', 'Publications', 'Fairs', 'The Galleries', 'News', 'Virtual Tours', 'Contact'].map((link) => (
              <li key={link}>
                <a
                  href="#"
                  style={{
                    fontFamily: 'DM Sans, sans-serif',
                    fontSize: '13px',
                    color: '#FAF9F6',
                    opacity: 0.7,
                    textDecoration: 'none',
                    transition: 'opacity 0.3s ease',
                  }}
                >
                  {link}
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Right — Locations */}
        <div>
          <p style={labelStyle}>Locations</p>

          <h3 style={cityStyle}>Miami</h3>
          <p style={{ ...bodyStyle, marginBottom: '32px' }}>
            1325 NE 1st Ave.<br />
            Miami, FL 33132, USA
          </p>

          <h3 style={cityStyle}>Caracas</h3>
          <p style={bodyStyle}>Venezuela</p>
        </div>
      </div>

      {/* Bottom bar */}
      <div style={{
        borderTop: '1px solid rgba(250,249,246,0.1)',
        margin: '0 10vw',
        padding: '24px 0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '11px',
          color: '#FAF9F6',
          opacity: 0.4,
          margin: 0,
        }}>
          &copy; 2025 Ascaso Gallery. All rights reserved.
        </p>
        <img
          src="/images/Logo Ascaso Gallery 1000x1000.jpg"
          alt="FADA"
          style={{ height: '32px', opacity: 0.6 }}
        />
      </div>
    </footer>
  )
}
