import { Cloud } from "lucide-react";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">

        <div className="navbar-icon">
          <Cloud size={22} />
        </div>

        <div>
          <h2>CloudOpt</h2>
          <span>Resource Optimization</span>
        </div>

      </div>

      <div className="navbar-status">
        <span className="status-dot"></span>
        System Online
      </div>
    </nav>
  );
}

export default Navbar;