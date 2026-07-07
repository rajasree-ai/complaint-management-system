require('dotenv').config();
const mongoose = require('mongoose');
const User = require('./models/User');

async function run(){
  try{
    const uri = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/qr_classroom';
    await mongoose.connect(uri);
    console.log('Connected to', uri);
    const user = await User.findOne({ email: 'test@example.com' }).lean();
    if(!user){
      console.log('User not found');
    } else {
      console.log('User found:');
      // remove password hash from output
      user.password = user.password ? '<hidden>' : undefined;
      console.log(JSON.stringify(user, null, 2));
    }
    await mongoose.disconnect();
  }catch(err){
    console.error('Error:', err.message);
    process.exit(1);
  }
}

run();
