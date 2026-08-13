require('dotenv').config();
const express = require('express');
const session = require('express-session');
const path = require('path');
const authRoutes = require('./routes/auth');

const app = express();
const PORT = process.env.PORT || 3000;

// --- Middleware ---
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(session({
  secret: process.env.SESSION_SECRET || 'dev_secret_change_me',
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    // secure: true, // enable this once you're running behind HTTPS in production
    maxAge: 1000 * 60 * 60 * 2, // 2 hours
  },
}));

// Serve frontend files (login.html, signup.html, dashboard.html, etc.)
app.use(express.static(path.join(__dirname, 'public')));

// --- Routes ---
app.use('/api', authRoutes);

// Example protected route
app.get('/api/dashboard-data', (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated.' });
  }
  res.json({ message: `Welcome, ${req.session.email}!` });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
