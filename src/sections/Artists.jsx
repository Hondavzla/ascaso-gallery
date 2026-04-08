import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const artists = [
  { name: 'Javier Martin', medium: 'Painting', image: '/images/artist-javier-martin.jpg' },
  { name: 'Julio Larraz', medium: 'Painting', image: '/images/artist-julio-larraz.png' },
  { name: 'Carlos Cruz-Diez', medium: 'Kinetic Art', image: '/images/artist-carlos-cruz-diez.jpg' },
  { name: 'Carlos Medina', medium: 'Sculpture', image: '/images/artist-carlos-medina.jpg' },
  { name: 'Alirio Palacios', medium: 'Painting', image: '/images/artist-alirio-palacios.jpg' },
]

const CARD_WIDTH = 380
const CARD_GAP = 32

export default function Artists() {
  const sectionRef = useRef(null)
  const trackRef = useRef(null)
  const progressRef = useRef(null)

  useEffect(() => {
    const track = trackRef.current
    const totalWidth = artists.length * CARD_WIDTH + (artists.length - 1) * CARD_GAP
    const scrollDistance = totalWidth - window.innerWidth + 200 // 200px for left padding (10vw ~)

    const ctx = gsap.context(() => {
      gsap.from('[data-animate="artists-header"]', {
        y: 30,
        opacity: 0,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 75%',
          end: 'top 25%',
          scrub: 0.5,
        },
      })

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          pin: true,
          scrub: 1,
          start: 'top top',
          end: () => `+=${totalWidth}`,
          onUpdate: (self) => {
            if (progressRef.current) {
              progressRef.current.style.width = `${self.progress * 100}%`
            }
          },
        },
      })

      tl.to(track, {
        x: -scrollDistance,
        ease: 'none',
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      ref={sectionRef}
      id="artists"
      style={{
        background: '#0D0D0D',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Section header */}
      <div data-animate="artists-header" style={{ paddingLeft: '10vw', paddingTop: '100px', paddingBottom: '60px' }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: '#C9A84C',
          marginBottom: '16px',
        }}>
          Our Artists
        </p>
        <h2 style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '64px',
          fontWeight: 300,
          lineHeight: 1.1,
          color: '#FAF9F6',
          margin: 0,
        }}>
          The Collection
        </h2>
      </div>

      {/* Horizontal track */}
      <div
        ref={trackRef}
        style={{
          display: 'flex',
          gap: `${CARD_GAP}px`,
          paddingLeft: '10vw',
          paddingRight: '10vw',
          paddingBottom: '80px',
        }}
      >
        {artists.map((artist) => (
          <div
            key={artist.name}
            style={{
              flex: `0 0 ${CARD_WIDTH}px`,
              height: '65vh',
              borderRadius: '2px',
              overflow: 'hidden',
              position: 'relative',
              cursor: 'pointer',
              transition: 'transform 600ms ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.05)' }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)' }}
          >
            <img
              src={artist.image}
              alt={artist.name}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                objectPosition: 'top center',
                display: 'block',
              }}
            />

            {/* Gradient overlay */}
            <div style={{
              position: 'absolute',
              inset: 0,
              background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)',
              pointerEvents: 'none',
            }} />

            {/* Artist info */}
            <div style={{
              position: 'absolute',
              bottom: '24px',
              left: '24px',
              right: '24px',
            }}>
              <p style={{
                fontFamily: 'DM Sans, sans-serif',
                fontSize: '11px',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: '#C9A84C',
                marginBottom: '8px',
              }}>
                {artist.medium}
              </p>
              <h3 style={{
                fontFamily: 'Cormorant Garamond, serif',
                fontSize: '36px',
                fontWeight: 300,
                fontStyle: 'italic',
                lineHeight: 1.15,
                color: '#FFFFFF',
                margin: 0,
              }}>
                {artist.name}
              </h3>
            </div>
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'rgba(201,168,76,0.2)',
      }}>
        <div
          ref={progressRef}
          style={{
            height: '100%',
            width: '0%',
            background: '#C9A84C',
            transition: 'width 0.05s linear',
          }}
        />
      </div>
    </section>
  )
}
