import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function Quote() {
  const sectionRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="quote"]', {
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
      background: '#0D0D0D',
      padding: '100px 0',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    }}>
      <div data-animate="quote" style={{
        maxWidth: '900px',
        padding: '0 48px',
        textAlign: 'center',
      }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: '#C9A84C',
          marginBottom: '32px',
        }}>
          El Arte
        </p>

        <p style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '52px',
          fontWeight: 300,
          fontStyle: 'italic',
          lineHeight: 1.4,
          color: '#FAF9F6',
          margin: 0,
        }}>
          La obra no termina en el taller, termina en los ojos del espectador.
        </p>

        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          color: '#C9A84C',
          marginTop: '32px',
        }}>
          — Carlos Cruz-Diez
        </p>
      </div>
    </section>
  )
}
