import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function ArtFair() {
  const sectionRef = useRef(null)
  const imageRef = useRef(null)
  const overlayRef = useRef(null)

  /* Parallax tilt + overlay */
  useEffect(() => {
    const el = imageRef.current
    const overlay = overlayRef.current
    if (!el || !overlay) return

    const textEls = overlay.querySelectorAll('[data-hover-text]')

    const onEnter = () => {
      gsap.to(overlay, { opacity: 1, duration: 0.4, ease: 'power2.out' })
      gsap.fromTo(textEls,
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.4, ease: 'power2.out', stagger: 0.15 }
      )
    }

    const onMove = (e) => {
      const rect = el.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5
      const rotateX = y * -10
      const rotateY = x * 10
      gsap.to(el, {
        rotateX,
        rotateY,
        boxShadow: `${-rotateY * 2}px ${rotateX * 2}px 30px rgba(0,0,0,0.2)`,
        duration: 0.1,
        ease: 'power2.out',
        overwrite: true,
      })
    }

    const onLeave = () => {
      gsap.to(el, {
        rotateX: 0,
        rotateY: 0,
        boxShadow: '0px 0px 30px rgba(0,0,0,0)',
        duration: 0.8,
        ease: 'power2.out',
        overwrite: true,
      })
      gsap.to(overlay, { opacity: 0, duration: 0.3, ease: 'power2.in' })
      gsap.to(textEls, { y: 10, opacity: 0, duration: 0.3, ease: 'power2.in' })
    }

    el.addEventListener('mouseenter', onEnter)
    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)

    return () => {
      el.removeEventListener('mouseenter', onEnter)
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
    }
  }, [])

  /* Scroll animations */
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
        <div ref={imageRef} data-animate="fair-image" style={{
          flex: '0 0 55%',
          maxWidth: '55%',
          height: '560px',
          overflow: 'hidden',
          position: 'relative',
          transformStyle: 'preserve-3d',
          perspective: '1000px',
          willChange: 'transform',
          cursor: 'pointer',
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

          {/* Hover overlay */}
          <div
            ref={overlayRef}
            style={{
              position: 'absolute',
              inset: 0,
              background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.2) 60%, transparent 100%)',
              opacity: 0,
              pointerEvents: 'none',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            <p data-hover-text style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '11px',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: '#C9A84C',
              margin: '0 0 4px 0',
              opacity: 0,
            }}>
              Booth AM125
            </p>
            <p data-hover-text style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: '36px',
              fontWeight: 300,
              fontStyle: 'italic',
              color: '#FFFFFF',
              margin: 0,
              opacity: 0,
            }}>
              Art Miami 2025
            </p>
            <p data-hover-text style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '13px',
              color: '#FFFFFF',
              opacity: 0,
              marginTop: '4px',
            }}>
              December 2 – 7, 2025
            </p>
          </div>
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
