import { Link } from "react-router-dom";

function Home() {
  return (
    <section className="page">
      <div className="simple-hero">
        <div className="simple-hero-copy">
          <span className="eyebrow">Leavify</span>
          <h1>Sign in or create an account.</h1>
          <p>
            Employees can register directly. Managers can register too, but
            only with a valid authorization code.
          </p>

          <div className="hero-actions hero-actions-centered">
            <Link className="button-primary" to="/login">
              Sign in
            </Link>
            <Link className="button-secondary" to="/register">
              Register
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Home;
