import { useEffect, useRef, useState } from 'react'
import { Link, useParams, Navigate } from 'react-router-dom'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Footer from '../sections/Footer'
import ArtistDetailSkeleton from '../components/ArtistDetailSkeleton'
import { useArtist, useRelatedArtists } from '../hooks/data'

gsap.registerPlugin(ScrollTrigger)

const modalLabelStyle = {
  fontFamily: 'DM Sans, sans-serif',
  fontSize: '13px',
  letterSpacing: '0.2em',
  textTransform: 'uppercase',
  color: '#C9A84C',
  margin: '48px 0 20px 0',
}

const modalYearStyle = {
  fontFamily: 'Cormorant Garamond, serif',
  fontSize: '20px',
  fontWeight: 400,
  color: '#FAF9F6',
  margin: '24px 0 8px 0',
}

const modalItemStyle = {
  fontFamily: 'DM Sans, sans-serif',
  fontSize: '14px',
  lineHeight: 1.7,
  color: '#FAF9F6',
  opacity: 0.75,
  margin: '0 0 4px 0',
  paddingLeft: '16px',
}

function WorkCard({ work }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      data-animate="work-card"
      style={{
        aspectRatio: '4/3',
        borderRadius: '2px',
        overflow: 'hidden',
        cursor: 'pointer',
        transition: 'transform 400ms ease',
        position: 'relative',
        transform: hovered ? 'scale(1.02)' : 'scale(1)',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <img
        src={work.image}
        alt={work.title}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block',
        }}
      />
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '20px 24px',
        background: 'linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%)',
        opacity: hovered ? 1 : 0,
        transition: 'opacity 400ms ease',
      }}>
        <p style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          color: '#FAF9F6',
          margin: 0,
          letterSpacing: '0.05em',
        }}>
          {work.title}
        </p>
      </div>
    </div>
  )
}

export default function ArtistDetail() {
  const { slug } = useParams()
  const { data: artist, isLoading, error } = useArtist(slug)
  const { data: related } = useRelatedArtists(slug)

  const [scrolled, setScrolled] = useState(false)
  const [navLight, setNavLight] = useState(true)
  const [bioModalOpen, setBioModalOpen] = useState(false)
  const heroRef = useRef(null)
  const relatedRef = useRef(null)
  const bioRef = useRef(null)
  const worksRef = useRef(null)
  const quoteRef = useRef(null)
  const modalRef = useRef(null)

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    if (!artist) return
    const triggers = []

    if (heroRef.current) {
      triggers.push(ScrollTrigger.create({
        trigger: heroRef.current,
        start: 'top top',
        end: 'bottom top',
        onEnter: () => setNavLight(true),
        onLeave: () => setNavLight(false),
        onLeaveBack: () => setNavLight(true),
      }))
    }

    if (relatedRef.current) {
      triggers.push(ScrollTrigger.create({
        trigger: relatedRef.current,
        start: 'top top',
        end: 'bottom top',
        onEnter: () => setNavLight(true),
        onLeave: () => setNavLight(true),
        onEnterBack: () => setNavLight(true),
        onLeaveBack: () => setNavLight(false),
      }))
    }

    return () => triggers.forEach((t) => t.kill())
  }, [artist])

  useEffect(() => {
    if (!artist) return
    const ctx = gsap.context(() => {
      gsap.from('[data-animate="page-nav"]', {
        y: -60,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      })

      gsap.from('[data-animate="back-link"]', {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.out',
        delay: 0.2,
      })

      gsap.from('[data-animate="artist-label"]', {
        y: 20,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        delay: 0.3,
      })

      gsap.from('[data-animate="artist-name"]', {
        y: 40,
        opacity: 0,
        duration: 1.4,
        ease: 'power3.out',
        delay: 0.6,
      })
    })

    return () => ctx.revert()
  }, [artist])

  useEffect(() => {
    if (!artist) return
    const ctx = gsap.context(() => {
      if (bioRef.current) {
        gsap.from(bioRef.current, {
          y: 40,
          opacity: 0,
          scrollTrigger: {
            trigger: bioRef.current,
            start: 'top 75%',
            end: 'top 25%',
            scrub: 0.5,
          },
        })
      }

      if (quoteRef.current) {
        gsap.from(quoteRef.current, {
          y: 30,
          opacity: 0,
          scrollTrigger: {
            trigger: quoteRef.current,
            start: 'top 75%',
            end: 'top 25%',
            scrub: 0.5,
          },
        })
      }

      const cards = document.querySelectorAll('[data-animate="work-card"]')
      if (cards.length) {
        gsap.from(cards, {
          y: 30,
          opacity: 0,
          stagger: 0.1,
          scrollTrigger: {
            trigger: worksRef.current,
            start: 'top 75%',
            end: 'top 25%',
            scrub: 0.5,
          },
        })
      }
    })

    return () => ctx.revert()
  }, [artist])

  const openModal = () => {
    setBioModalOpen(true)
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => {
      if (modalRef.current) {
        gsap.fromTo(modalRef.current,
          { y: '100%' },
          { y: '0%', duration: 0.6, ease: 'power3.out' }
        )
      }
    })
  }

  const closeModal = () => {
    if (modalRef.current) {
      gsap.to(modalRef.current, {
        y: '100%',
        duration: 0.5,
        ease: 'power3.in',
        onComplete: () => {
          setBioModalOpen(false)
          document.body.style.overflow = ''
        },
      })
    }
  }

  if (isLoading) return <ArtistDetailSkeleton />
  if (error || !artist) return <Navigate to="/" replace />

  return (
    <>
      {/* Navigation */}
      <nav data-animate="page-nav" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '24px 48px',
        background: scrolled
          ? navLight ? 'rgba(13,13,13,0.95)' : 'rgba(250,249,246,0.95)'
          : 'transparent',
        backdropFilter: scrolled ? 'blur(8px)' : 'none',
        WebkitBackdropFilter: scrolled ? 'blur(8px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(13,13,13,0.08)' : '1px solid transparent',
        transition: 'background 0.3s ease, border-bottom 0.3s ease',
      }}>
        <Link to="/" style={{ display: 'block' }}>
          <img
            src="/logo.svg"
            alt="Ascaso Gallery"
            style={{
              height: '44px',
              filter: navLight ? 'brightness(0) invert(1)' : 'none',
              transition: 'filter 0.3s ease',
            }}
          />
        </Link>
        <ul style={{
          display: 'flex',
          alignItems: 'center',
          gap: '40px',
          listStyle: 'none',
          margin: 0,
          padding: 0,
        }}>
          {['Artists', 'Exhibitions', 'Contact'].map((link) => (
            <li key={link}>
              <a
                href={`/#${link.toLowerCase()}`}
                style={{
                  fontFamily: 'DM Sans, sans-serif',
                  fontSize: '14px',
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  textDecoration: 'none',
                  color: navLight ? '#FAF9F6' : 'rgba(13,13,13,0.7)',
                  transition: 'color 0.3s ease',
                }}
              >
                {link}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Back link */}
      <Link data-animate="back-link" to="/" style={{
        position: 'fixed',
        top: '90px',
        left: '48px',
        zIndex: 49,
        fontFamily: 'DM Sans, sans-serif',
        fontSize: '12px',
        color: '#C9A84C',
        textDecoration: 'none',
        transition: 'opacity 0.3s ease',
      }}>
        &larr; Back
      </Link>

      {/* Section 1 — Hero banner */}
      <section ref={heroRef} style={{
        height: '60vh',
        background: '#0D0D0D',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <p data-animate="artist-label" style={{
          fontFamily: 'DM Sans, sans-serif',
          fontSize: '13px',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: '#C9A84C',
          marginBottom: '24px',
        }}>
          {artist.eyebrow}
        </p>
        <h1 data-animate="artist-name" style={{
          fontFamily: 'Cormorant Garamond, serif',
          fontSize: '80px',
          fontWeight: 300,
          color: '#FAF9F6',
          margin: 0,
          textAlign: 'center',
        }}>
          {artist.name}
        </h1>
      </section>

      {/* Section 2 — Bio */}
      <section ref={bioRef} style={{
        background: '#FAF9F6',
        padding: '100px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
          display: 'flex',
          gap: '80px',
          alignItems: 'flex-start',
        }}>
          <div style={{
            flex: '0 0 45%',
            maxWidth: '45%',
            height: '600px',
            overflow: 'hidden',
          }}>
            <img
              src={artist.heroImage}
              alt={artist.name}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
                objectPosition: 'top center',
                display: 'block',
              }}
            />
          </div>

          <div style={{
            flex: '0 0 55%',
            maxWidth: '55%',
            paddingLeft: '40px',
          }}>
            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '13px',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              color: '#C9A84C',
              marginBottom: '24px',
            }}>
              About the Artist
            </p>

            <p style={{
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '16px',
              lineHeight: 1.9,
              color: '#0D0D0D',
              opacity: 0.75,
              marginBottom: '24px',
            }}>
              {artist.bio.short}
            </p>

            <button
              onClick={openModal}
              style={{
                background: 'none',
                border: 'none',
                padding: 0,
                fontFamily: 'DM Sans, sans-serif',
                fontSize: '13px',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: '#C9A84C',
                cursor: 'pointer',
                marginBottom: '40px',
              }}
            >
              Read More +
            </button>

            <br />

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
              Download Catalog
            </button>
          </div>
        </div>
      </section>

      {/* Quote strip */}
      <section ref={quoteRef} style={{
        background: '#0D0D0D',
        padding: '80px 0',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}>
        <div style={{
          maxWidth: '800px',
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
            {artist.quote.eyebrow}
          </p>
          <p style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '48px',
            fontWeight: 300,
            fontStyle: 'italic',
            lineHeight: 1.4,
            color: '#FAF9F6',
            margin: 0,
          }}>
            {artist.quote.text}
          </p>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            color: '#C9A84C',
            marginTop: '24px',
          }}>
            — {artist.quote.attribution}
          </p>
        </div>
      </section>

      {/* Section 3 — Works grid */}
      <section ref={worksRef} style={{
        background: '#FAF9F6',
        padding: '80px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
        }}>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#C9A84C',
            marginBottom: '16px',
          }}>
            Obra
          </p>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '56px',
            fontWeight: 300,
            lineHeight: 1.1,
            color: '#0D0D0D',
            margin: '0 0 48px 0',
          }}>
            Selected Works
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '24px',
          }}>
            {artist.works.map((work) => (
              <WorkCard key={work.slug} work={work} />
            ))}
          </div>
        </div>
      </section>

      {/* Section 4 — Related Artists */}
      <section ref={relatedRef} style={{
        background: '#0D0D0D',
        padding: '100px 0',
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '0 64px',
        }}>
          <p style={{
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '13px',
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: '#C9A84C',
            marginBottom: '16px',
          }}>
            También te puede interesar
          </p>
          <h2 style={{
            fontFamily: 'Cormorant Garamond, serif',
            fontSize: '48px',
            fontWeight: 300,
            lineHeight: 1.1,
            color: '#FAF9F6',
            margin: '0 0 48px 0',
          }}>
            Related Artists
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '24px',
          }}>
            {related.map((r) => (
              <div
                key={r.slug}
                style={{
                  height: '320px',
                  borderRadius: '2px',
                  overflow: 'hidden',
                  position: 'relative',
                }}
              >
                <img
                  src={r.image}
                  alt={r.name}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    objectPosition: 'top center',
                    display: 'block',
                  }}
                />
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 60%)',
                  pointerEvents: 'none',
                }} />
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
                    {r.medium}
                  </p>
                  <h3 style={{
                    fontFamily: 'Cormorant Garamond, serif',
                    fontSize: '28px',
                    fontWeight: 300,
                    fontStyle: 'italic',
                    lineHeight: 1.15,
                    color: '#FFFFFF',
                    margin: 0,
                  }}>
                    {r.name}
                  </h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />

      {/* Bio Modal Overlay */}
      {bioModalOpen && (
        <div
          ref={modalRef}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            background: 'rgba(13,13,13,0.97)',
            overflowY: 'auto',
            transform: 'translateY(100%)',
          }}
        >
          <button
            onClick={closeModal}
            style={{
              position: 'fixed',
              top: '32px',
              right: '48px',
              zIndex: 10000,
              background: 'none',
              border: 'none',
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '32px',
              color: '#C9A84C',
              cursor: 'pointer',
              lineHeight: 1,
            }}
          >
            &times;
          </button>

          <div style={{
            maxWidth: '800px',
            margin: '0 auto',
            padding: '80px 48px 120px',
          }}>
            <h2 style={{
              fontFamily: 'Cormorant Garamond, serif',
              fontSize: '48px',
              fontWeight: 300,
              color: '#FAF9F6',
              margin: '0 0 16px 0',
            }}>
              {artist.name}
            </h2>
            {artist.bio.full.map((paragraph, i) => (
              <p key={i} style={{
                fontFamily: 'DM Sans, sans-serif',
                fontSize: '14px',
                lineHeight: 1.8,
                color: '#FAF9F6',
                opacity: 0.75,
                marginBottom: '8px',
              }}>
                {paragraph}
              </p>
            ))}

            <h3 style={modalLabelStyle}>Exhibitions &amp; Events</h3>
            {artist.exhibitions.map((group) => (
              <div key={group.year}>
                <p style={modalYearStyle}>{group.year}</p>
                {group.items.map((item, i) => (
                  <p key={i} style={modalItemStyle}>{item}</p>
                ))}
              </div>
            ))}

            <h3 style={modalLabelStyle}>Public Monumental Works</h3>
            {artist.monumentalWorks.map((group) => (
              <div key={group.year}>
                <p style={modalYearStyle}>{group.year}</p>
                {group.items.map((item, i) => (
                  <p key={i} style={modalItemStyle}>{item}</p>
                ))}
              </div>
            ))}

            <h3 style={modalLabelStyle}>Awards Selection</h3>
            {artist.awards.map((item) => (
              <p key={item} style={modalItemStyle}>{item}</p>
            ))}

            <h3 style={modalLabelStyle}>Collection</h3>
            {artist.collections.map((item) => (
              <p key={item} style={modalItemStyle}>{item}</p>
            ))}
          </div>
        </div>
      )}
    </>
  )
}
