import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const news = [
  {
    image: '/images/news-1.jpg',
    date: 'October 15, 2025',
    title: 'Muestra colectiva en Miami honra el legado de Julio Larraz',
    excerpt: 'Collective Exhibition in Miami Honors the Legacy of Julio Larraz. Ascaso Gallery presents Reciprocity, a living tribute.',
  },
  {
    image: '/images/news-2.jpg',
    date: 'October 1, 2025',
    title: 'Reciprocity at Ascaso Gallery Bridges Generation Gap',
    excerpt: 'Artist Julio Larraz Exhibits Alongside Emerging Artists in Miami.',
  },
  {
    image: '/images/news-3.jpg',
    date: 'October 1, 2025',
    title: 'Reciprocity: Julio Larraz and the Next Generation of Artistic Freedom',
    excerpt: 'Julio Larraz and the Next Generation of Artistic Freedom. Source: ArtDaily.',
  },
]

export default function News() {
  const sectionRef = useRef(null)

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="news-card"]', {
        y: 50,
        opacity: 0,
        duration: 1.2,
        ease: 'power3.out',
        stagger: 0.2,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 70%',
        },
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [])

  return (
    <section ref={sectionRef} style={{ background: '#FAF9F6' }}>
      {/* Section header */}
      <div style={{ paddingLeft: '10vw', paddingTop: '80px', paddingBottom: '48px' }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '10px',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: '#C9A84C',
          marginBottom: '16px',
        }}>
          Latest News
        </p>
        <h2 style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '64px',
          fontWeight: 300,
          lineHeight: 1.1,
          color: '#0D0D0D',
          margin: 0,
        }}>
          From the Gallery
        </h2>
      </div>

      {/* Cards grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '32px',
        padding: '0 10vw 80px',
      }}>
        {news.map((item) => (
          <article
            key={item.title}
            data-animate="news-card"
            style={{
              borderBottom: '1px solid rgba(13,13,13,0.1)',
              paddingBottom: '32px',
            }}
          >
            {/* Image */}
            <div style={{ overflow: 'hidden', height: '300px', marginBottom: '24px' }}>
              <img
                src={item.image}
                alt={item.title}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  display: 'block',
                }}
              />
            </div>

            {/* Date */}
            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '11px',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: '#C9A84C',
              marginBottom: '12px',
            }}>
              {item.date}
            </p>

            {/* Title */}
            <h3 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: '28px',
              fontWeight: 400,
              lineHeight: 1.25,
              color: '#0D0D0D',
              margin: '0 0 12px 0',
            }}>
              {item.title}
            </h3>

            {/* Excerpt */}
            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '14px',
              fontWeight: 400,
              lineHeight: 1.6,
              color: 'rgba(13,13,13,0.6)',
              margin: '0 0 20px 0',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}>
              {item.excerpt}
            </p>

            {/* CTA link */}
            <a
              href="#"
              style={{
                fontFamily: 'DM Sans, sans-serif',
                fontSize: '11px',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: '#0D0D0D',
                textDecoration: 'none',
                transition: 'color 0.3s ease',
              }}
            >
              Continue Reading &rarr;
            </a>
          </article>
        ))}
      </div>
    </section>
  )
}
