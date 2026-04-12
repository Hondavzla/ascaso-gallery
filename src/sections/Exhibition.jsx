import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useCurrentExhibition } from '../hooks/data'

gsap.registerPlugin(ScrollTrigger)

export default function Exhibition() {
  const { data: exhibition, isLoading } = useCurrentExhibition()
  const sectionRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="exhibit-text"]', {
        y: 40,
        opacity: 0,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 75%',
          end: 'top 25%',
          scrub: 0.5,
        },
      })

      gsap.from('[data-animate="exhibit-image"]', {
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

  if (isLoading || !exhibition) return null

  return (
    <section ref={sectionRef} id="exhibition" style={{ position: 'relative', zIndex: 1 }}>
      {/* Divider */}
      <hr style={{ border: 'none', borderTop: '1px solid rgba(13,13,13,0.1)', margin: 0 }} />

      <div style={{
        background: '#FAF9F6',
        padding: '120px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
          display: 'flex',
          gap: '80px',
          alignItems: 'center',
        }}>
          {/* Left column — text */}
          <div data-animate="exhibit-text" style={{ flex: '0 0 40%', maxWidth: '40%' }}>
            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '13px',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: '#C9A84C',
              marginBottom: '24px',
            }}>
              {exhibition.eyebrow}
            </p>

            <h2 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: '72px',
              fontWeight: 300,
              lineHeight: 1.05,
              color: '#0D0D0D',
              margin: '0 0 16px 0',
            }}>
              {exhibition.title}
            </h2>

            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '16px',
              fontWeight: 300,
              color: '#0D0D0D',
              opacity: 0.6,
              marginBottom: '40px',
            }}>
              {exhibition.subtitle}
            </p>

            <div style={{
              width: '40px',
              height: '1px',
              background: '#C9A84C',
              marginBottom: '16px',
            }} />

            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '13px',
              letterSpacing: '0.08em',
              color: '#0D0D0D',
              opacity: 0.5,
              marginBottom: '48px',
            }}>
              {exhibition.dateLabel}
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
              See Exhibition
            </button>
          </div>

          {/* Right column — poster */}
          <div data-animate="exhibit-image" style={{
            flex: '0 0 60%',
            maxWidth: '60%',
            height: '520px',
            overflow: 'hidden',
          }}>
            <img
              src={exhibition.image}
              alt={`${exhibition.title} — ${exhibition.subtitle}`}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                objectPosition: 'top center',
                display: 'block',
              }}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
