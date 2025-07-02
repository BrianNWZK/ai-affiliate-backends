const express = require("express")
const cors = require("cors")
const neuralRoutes = require("./routes/neural")

const app = express()
const PORT = process.env.PORT || 3000

// Middleware
app.use(cors())
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// Routes
app.use("/api/neural", neuralRoutes)

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  })
})

// Demo endpoint
app.get("/api/demo", (req, res) => {
  res.json({
    message: "ArielMatrix Backend API",
    version: "1.0.0",
    endpoints: [
      "/api/neural/predict",
      "/api/neural/deploy-agent",
      "/api/neural/activities",
      "/api/neural/quantum-optimize",
    ],
  })
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack)
  res.status(500).json({
    success: false,
    error: "Internal server error",
  })
})

// 404 handler
app.use("*", (req, res) => {
  res.status(404).json({
    success: false,
    error: "Route not found",
  })
})

app.listen(PORT, () => {
  console.log(`ArielMatrix Backend running on port ${PORT}`)
})

module.exports = app
