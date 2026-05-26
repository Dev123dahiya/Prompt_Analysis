function LeavifyLogo({ compact = false }) {
  return (
    <div className={compact ? "leavify-logo leavify-logo-compact" : "leavify-logo"}>
      <div className="leavify-mark" aria-hidden="true">
        <span className="leavify-ring" />
        <span className="leavify-hand leavify-hand-short" />
        <span className="leavify-hand leavify-hand-long" />
        <span className="leavify-center" />
      </div>

      <div className="leavify-wordmark">
        <strong>Leavify</strong>
        <span>Leave Management System</span>
      </div>
    </div>
  );
}

export default LeavifyLogo;
