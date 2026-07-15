try {
  require('dotenv').config({ path: '.env.local' });
} catch (_) {}

const nodemailer = require('nodemailer');

async function main() {
  const required = ['SMTP_HOST', 'SMTP_USER', 'SMTP_PASS'];
  const missing = required.filter((key) => !process.env[key]);
  if (missing.length) {
    throw new Error(`Missing env keys: ${missing.join(', ')}`);
  }

  const port = Number(process.env.SMTP_PORT || 587);
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port,
    secure: port === 465,
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });

  await transporter.verify();
  console.log('SMTP login verified successfully.');
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
