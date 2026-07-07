const mongoose = require("mongoose");
const { MongoMemoryServer } = require("mongodb-memory-server");

let mongoServer;

const connectDB = async () => {
  const mongoUri = process.env.MONGO_URI?.trim();

  try {
    if (mongoUri) {
      await mongoose.connect(mongoUri);
      console.log("Database Connected");
      return;
    }

    throw new Error("MONGO_URI is not configured");
  } catch (error) {
    console.warn(
      "Primary MongoDB connection failed. Falling back to an in-memory MongoDB instance.",
      error.message
    );

    try {
      if (!mongoServer) {
        mongoServer = await MongoMemoryServer.create();
      }

      await mongoose.connect(mongoServer.getUri());
      console.log("Database Connected (in-memory MongoDB)");
    } catch (fallbackError) {
      console.error("Database connection failed:", fallbackError);
      process.exit(1);
    }
  }
};

module.exports = connectDB;