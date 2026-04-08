import { useEffect, useRef } from 'react'
import gsap from 'gsap'

export default function Intro() {
  const overlayRef = useRef(null)

  useEffect(() => {
    const tl = gsap.timeline()

    tl.fromTo(
      '[data-animate="intro-logo"]',
      { scale: 0.8, opacity: 0 },
      { scale: 1, opacity: 1, duration: 2, ease: 'power2.out' }
    )
    .to(overlayRef.current, {
      y: '-100%',
      opacity: 0,
      duration: 1.2,
      ease: 'power3.inOut',
      delay: 1.5,
      onComplete: () => {
        if (overlayRef.current) {
          overlayRef.current.style.display = 'none'
        }
      },
    })
  }, [])

  return (
    <div
      ref={overlayRef}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: '#0D0D0D',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <img
        data-animate="intro-logo"
        src="/logo.svg"
        alt="Ascaso Gallery"
        style={{
          height: '60px',
          filter: 'invert(1) brightness(2)',
          opacity: 0,
        }}
      />
    </div>
  )
}
