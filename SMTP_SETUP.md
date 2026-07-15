# SMTP Email Setup

The website now sends invoice emails through the backend endpoint:

`/api/send-invoice-email`

Keep SMTP credentials only in environment variables. Do not paste SMTP passwords into `index.html` or the admin settings page.

## Gmail Setup

1. Turn on 2-Step Verification for your Google account.
2. Create a Gmail App Password for Mail.
3. Add these environment variables to your hosting provider:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-16-character-app-password
SMTP_FROM=your-email@gmail.com
```

## Admin Panel Setting

In the portal admin settings, keep this value:

```text
/api/send-invoice-email
```

## Local Testing

Copy `.env.example` to `.env.local` and replace the placeholder values with your SMTP details.

```powershell
Copy-Item .env.example .env.local
```

For deployment, add the same variables in Vercel, Netlify, or your Node hosting dashboard.
