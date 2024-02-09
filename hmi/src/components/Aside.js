import React from "react";
import { NavLink } from "react-router-dom";

export default function Aside() {
  return (
    <aside className="content main-sidebar sidebar-dark-primary elevation-4">
      {/* Brand Logo */}
      <a href="index3.html" className="brand-link">
        <img
          src="dist/img/AdminLTELogo.png"
          alt="AdminLTE Logo"
          className="brand-image img-circle elevation-3"
          style={{ opacity: ".8" }}
        />
        <span className="brand-text font-weight-light">ProNode</span>
      </a>
      {/* Sidebar */}
      <div className="sidebar">
        {/* Sidebar Menu */}
        <nav className="mt-2">
          <ul
            className="nav nav-pills nav-sidebar flex-column"
            data-widget="treeview"
            role="menu"
            data-accordion="false"
          >
            {/* <li className="nav-item">
              <a href="pages/widgets.html" className="nav-link">
                <i className="nav-icon fas fa-th" />
                <p>
                  Monitor
                  <span className="right badge badge-danger">New</span>
                </p>
              </a>
            </li> */}
            <li className="nav-item">
              <NavLink
                exact
                to="/"
                className={"nav-link"}
                style={({ isActive }) => ({
                  color: isActive ? "greenyellow" : "white",
                })}
              >
                <i className="nav-icon fas fa-th" />
                <p>
                  Monitor
                  <span className="right badge badge-danger">New</span>
                </p>
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/Tags"
                className={"nav-link"}
                style={({ isActive }) => ({
                  color: isActive ? "greenyellow" : "white",
                })}
              >
                <i className="nav-icon fas fa-th" />
                <p>
                  Tags
                  <span className="right badge badge-danger">New</span>
                </p>
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/Alarms"
                className={"nav-link"}
                style={({ isActive }) => ({
                  color: isActive ? "greenyellow" : "white",
                })}
              >
                <i className="nav-icon fas fa-th" />
                <p>
                  Alarms
                  <span className="right badge badge-danger">New</span>
                </p>
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink
                exact
                to="/Opcua"
                className={"nav-link"}
                style={({ isActive }) => ({
                  color: isActive ? "greenyellow" : "white",
                })}
              >
                <i className="nav-icon fas fa-th" />
                <p>
                  OPCUA
                  <span className="right badge badge-danger">New</span>
                </p>
              </NavLink>
            </li>
            <li className="nav-header">Deployment</li>
            <li className="nav-item">
              <NavLink
                exact
                to="/Configuration"
                className={"nav-link"}
                style={({ isActive }) => ({
                  color: isActive ? "greenyellow" : "white",
                })}
              >
                <i className="nav-icon fas fa-th" />
                <p>
                  Configuration
                  <span className="right badge badge-danger">New</span>
                </p>
              </NavLink>
            </li>
          </ul>
        </nav>
        {/* /.sidebar-menu */}
      </div>
      {/* /.sidebar */}
    </aside>
  );
}
