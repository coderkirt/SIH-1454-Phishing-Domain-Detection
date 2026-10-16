import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { message: "" };
  }

  static getDerivedStateFromError(error) {
    return { message: error?.message || "The app failed to open." };
  }

  render() {
    if (this.state.message) {
      return (
        <div style={{ minHeight: "100vh", padding: 24, background: "#080808", color: "#f5f5f5" }}>
          <p style={{ letterSpacing: "0.12em", textTransform: "uppercase", fontSize: 12, color: "#ff0000" }}>PhishEye</p>
          <h1 style={{ fontSize: 28 }}>Could not open the screen</h1>
          <p>{this.state.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}
