import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useLatestNews } from '../hooks/data'
import { formatNewsDate } from '../utils/formatDate'

gsap.registerPlugin(ScrollTrigger)

export default function News() {
  const { data: news } = useLatestNews(3)
  const sectionRef = useRef(null)

  useEffect(() => {
    if (!news.length) return
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="news-card"]', {
        y: 50,
        opacity: 0,
        stagger: 0.15,
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 75%',
          end: 'top 25%',
          scrub: 0.5,
        },
      })
    }, sectionRef)

    return () => ctx.revert()
  }, [news.length])

  return (
    <section ref={sectionRef} style={{ background: '#FAF9F6' }}>
      {/* Section header */}
      <div style={{ paddingLeft: '10vw', paddingTop: '80px', paddingBottom: '48px' }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
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
            key={item.slug}
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
              {formatNewsDate(item.date)}
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
