export default function ArtistDetailSkeleton() {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0D0D0D',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div style={{
        width: '240px',
        height: '12px',
        background: 'rgba(201,168,76,0.2)',
        marginBottom: '24px',
      }} />
      <div style={{
        width: '480px',
        maxWidth: '80vw',
        height: '56px',
        background: 'rgba(250,249,246,0.08)',
      }} />
    </div>
  )
}
