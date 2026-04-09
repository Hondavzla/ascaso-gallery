import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Intro from './components/Intro'
import Hero from './sections/Hero'
import Quote from './sections/Quote'
import Exhibition from './sections/Exhibition'
import Artists from './sections/Artists'
import News from './sections/News'
import ArtFair from './sections/ArtFair'
import Footer from './sections/Footer'
import CarlosMedina from './pages/CarlosMedina'

function LandingPage() {
  return (
    <>
      <Intro />
      <Hero />
      <Quote />
      <Exhibition />
      <Artists />
      <News />
      <ArtFair />
      <Footer />
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/artists/carlos-medina" element={<CarlosMedina />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
