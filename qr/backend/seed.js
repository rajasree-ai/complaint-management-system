const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
require("dotenv").config();

const UserSchema = new mongoose.Schema({
  name: String,
  email: { type: String, unique: true },
  password: String,
  role: { type: String, enum: ["student", "teacher", "admin"], default: "student" }
});

const User = mongoose.model("User", UserSchema);

async function seedUser() {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log("Database connected");

    // Check if user exists
    const existingUser = await User.findOne({ email: "test@example.com" });
    if (existingUser) {
      console.log("Test user already exists");
      process.exit(0);
    }

    // Create test user
    const hashedPassword = await bcrypt.hash("password123", 10);
    const newUser = new User({
      name: "Test User",
      email: "test@example.com",
      password: hashedPassword,
      role: "admin"
    });

    await newUser.save();
    console.log("✅ Test user created!");
    console.log("Email: test@example.com");
    console.log("Password: password123");
    process.exit(0);
  } catch (err) {
    console.error("Error:", err);
    process.exit(1);
  }
}

seedUser();
