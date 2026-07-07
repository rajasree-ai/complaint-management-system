const QRCode = require("qrcode");

exports.generateQR =
async(req,res)=>{

const classroom =
req.params.classroom;

const url =
`https://portal.college.com/${classroom}`;

const qr =
await QRCode.toDataURL(url);

res.json({qr});
};