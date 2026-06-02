export default function Input({ label, error, id, className = '', ...props }) {
  return (
    <div className={className}>
      {label && (
        <label htmlFor={id} className="label">
          {label}
        </label>
      )}
      <input id={id} className="input" {...props} />
      {error && <p className="mt-1 text-xs text-rose-500">{error}</p>}
    </div>
  )
}
