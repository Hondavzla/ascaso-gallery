import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function ArtFair() {
  const sectionRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="fair-image"]', {
        opacity: 0,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 75%',
          end: 'top 25%',
          scrub: 0.5,
        },
      })

      gsap.from('[data-animate="fair-text"]', {
        y: 40,
        opacity: 0,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 75%',
          end: 'top 25%',
          scrub: 0.5,
        },
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section ref={sectionRef} style={{
      background: '#FAF9F6',
      padding: '120px 0',
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 64px',
        display: 'flex',
        alignItems: 'center',
        gap: '0',
        minHeight: '560px',
      }}>
        {/* Left column — image */}
        <div data-animate="fair-image" style={{
          flex: '0 0 55%',
          maxWidth: '55%',
          height: '560px',
          overflow: 'hidden',
        }}>
          <img
            src="/images/art-fair-miami.jpg"
            alt="Art Miami 2025"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: 'block',
            }}
          />
        </div>

        {/* Right column — text */}
        <div data-animate="fair-text" style={{
          flex: '0 0 45%',
          maxWidth: '45%',
          paddingLeft: '80px',
        }}>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#C9A84C',
            marginBottom: '24px',
          }}>
            Last Art Fair
          </p>

          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '64px',
            fontWeight: 300,
            lineHeight: 1.05,
            color: '#0D0D0D',
            margin: '0 0 32px 0',
          }}>
            Art Miami 2025
          </h2>

          <div style={{
            width: '40px',
            height: '1px',
            background: '#C9A84C',
            marginBottom: '24px',
          }} />

          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '14px',
            color: '#0D0D0D',
            marginBottom: '16px',
          }}>
            December 2 – December 7, 2025
          </p>

          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '14px',
            lineHeight: 1.7,
            color: '#0D0D0D',
            opacity: 0.7,
            marginBottom: '48px',
          }}>
            Ascaso Gallery at Art Miami 2025 – Booth AM125, with works by Pablo Atchugarry, Fernando Botero, Carlos Cruz-Diez, Olga de Amaral, Jiménez Deredia, Julio Larraz.
          </p>

          <button style={{
            border: '1px solid #0D0D0D',
            background: 'transparent',
            padding: '14px 32px',
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '11px',
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            cursor: 'pointer',
            color: '#0D0D0D',
            transition: 'all 0.5s ease',
          }}>
            See Details
          </button>
        </div>
      </div>
    </section>
  )
}
