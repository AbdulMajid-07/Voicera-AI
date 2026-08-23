import { BrandMark } from "./icons.jsx";

export default function Nav() {
  return (
    <nav>
      <div className="nav-inner">
        <a className="brand" href="#top">
          <BrandMark />
          Voicera AI
        </a>
        <div className="nav-links">
          <a href="#demo">Live demo</a>
          <a href="#why">Why Voicera</a>
          <a href="#how">How it works</a>
        </div>
        <a className="btn btn-primary btn-sm" href="#demo">
          Book a demo
        </a>
      </div>
    </nav>
  );
}
