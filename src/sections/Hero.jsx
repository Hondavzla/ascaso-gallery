import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import * as THREE from 'three'

/* ─── Three.js warm-tone drifting particles ─── */
function initParticles(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setSize(window.innerWidth, window.innerHeight)

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100)
  camera.position.z = 4

  const count = 600
  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  const speeds = new Float32Array(count)

  const palette = [
    new THREE.Color('#C9A84C'), // gold
    new THREE.Color('#D4C5A0'), // muted gold
    new THREE.Color('#E8DCC8'), // warm beige
    new THREE.Color('#B8A070'), // antique
  ]

  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 10
    positions[i * 3 + 1] = (Math.random() - 0.5) * 8
    positions[i * 3 + 2] = (Math.random() - 0.5) * 6
    const c = palette[Math.floor(Math.random() * palette.length)]
    colors[i * 3] = c.r
    colors[i * 3 + 1] = c.g
    colors[i * 3 + 2] = c.b
    speeds[i] = 0.2 + Math.random() * 0.5
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const material = new THREE.PointsMaterial({
    size: 0.02,
    vertexColors: true,
    transparent: true,
    opacity: 0.4,
    sizeAttenuation: true,
  })

  const points = new THREE.Points(geometry, material)
  scene.add(points)

  let frameId
  const clock = new THREE.Clock()

  function animate() {
    frameId = requestAnimationFrame(animate)
    const t = clock.getElapsedTime()
    const pos = geometry.attributes.position.array

    for (let i = 0; i < count; i++) {
      pos[i * 3 + 1] += Math.sin(t * speeds[i] + i) * 0.0004
      pos[i * 3] += Math.cos(t * speeds[i] * 0.5 + i) * 0.0003
    }
    geometry.attributes.position.needsUpdate = true

    points.rotation.y = t * 0.015
    points.rotation.x = Math.sin(t * 0.01) * 0.05

    renderer.render(scene, camera)
  }

  animate()

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  }
  window.addEventListener('resize', onResize)

  return () => {
    cancelAnimationFrame(frameId)
    window.removeEventListener('resize', onResize)
    renderer.dispose()
    geometry.dispose()
    material.dispose()
  }
}

/* ─── Hero Section ─── */
export default function Hero() {
  const canvasRef = useRef(null)
  const heroRef = useRef(null)

  /* Three.js background */
  useEffect(() => {
    if (!canvasRef.current) return
    const cleanup = initParticles(canvasRef.current)
    return cleanup
  }, [])

  /* GSAP entrance animations */
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.set('[data-animate="cta"]', { opacity: 0, y: 30 })

      const tl = gsap.timeline({ defaults: { ease: 'power3.out', duration: 1.4 } })

      tl.from('[data-animate="nav"]', {
        y: -30,
        opacity: 0,
        duration: 1,
      })
      .from('[data-animate="headline"]', {
        y: 60,
        opacity: 0,
      }, 0.3)
      .from('[data-animate="subline"]', {
        y: 40,
        opacity: 0,
      }, 0.6)
      .fromTo('[data-animate="cta"]', {
        y: 30,
        opacity: 0,
      }, {
        y: 0,
        opacity: 1,
        visibility: 'visible',
        duration: 1,
      }, 0.9)
      .from('[data-animate="artwork"]', {
        x: 80,
        opacity: 0,
        duration: 1.6,
      }, 0.5)
    }, heroRef)

    return () => ctx.revert()
  }, [])

  return (
    <section
      ref={heroRef}
      className="relative h-screen w-full overflow-hidden bg-cream"
    >
      {/* Three.js canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
      />

      {/* Fixed navigation */}
      <nav
        data-animate="nav"
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-6 md:px-12"
      >
        <a href="/" className="block">
          <img src="/logo.svg" alt="Ascaso Gallery" style={{height: '44px'}} />
        </a>
        <ul className="hidden md:flex items-center gap-10">
          {['Artists', 'Exhibitions', 'Contact'].map((link) => (
            <li key={link}>
              <a
                href={`#${link.toLowerCase()}`}
                className="font-body text-sm tracking-[0.12em] uppercase text-ink/70 hover:text-gold transition-colors duration-500"
              >
                {link}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Content grid */}
      <div className="relative z-10 h-full flex flex-col lg:flex-row items-center justify-start lg:justify-center px-8 md:px-16 lg:px-24 gap-6 lg:gap-20 pt-24 lg:pt-0">
        {/* Left — text */}
        <div className="flex-1 flex flex-col justify-center items-start max-w-xl">
          <h1
            data-animate="headline"
            className="font-display text-5xl md:text-6xl lg:text-7xl font-light leading-[1.1] tracking-tight text-ink"
          >
            Where Art Finds
            <br />
            Its Home
          </h1>

          <p
            data-animate="subline"
            className="mt-6 font-body text-base md:text-lg tracking-[0.2em] uppercase text-ink/50"
          >
            Miami &middot; Caracas
          </p>

          <button
            data-animate="cta"
            style={{
              marginTop: '48px',
              border: '1px solid #0D0D0D',
              background: 'transparent',
              padding: '14px 32px',
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '11px',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              cursor: 'pointer',
              color: '#0D0D0D',
              transition: 'all 0.5s ease'
            }}
          >View Current Exhibition</button>
        </div>

        {/* Right — artwork image */}
        <div
          data-animate="artwork"
          className="flex-1 flex items-center justify-center max-w-lg w-full min-h-0"
        >
          <div className="relative w-full aspect-[3/4] max-h-[50vh] lg:max-h-none rounded-sm overflow-hidden bg-[#FAF9F6]">
            <img
              src="/images/Hero-Artwork.jpg"
              alt="Featured Artwork"
              className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-black/[0.15]" />
          </div>
        </div>
      </div>
    </section>
  )
}
