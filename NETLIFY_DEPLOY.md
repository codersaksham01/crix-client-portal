# Netlify Deployment

This project is a static `index.html` portal with one serverless email endpoint.

## Files added for Netlify

- `netlify.toml` tells Netlify to publish the project root and use `netlify/functions`.
- `netlify/functions/send-invoice-email.js` adapts the existing email handler to a Netlify Function.
- `/api/send-invoice-email` is redirected to the Netlify Function, so the app can keep using the same endpoint.

## Deploy Steps

1. Push this folder to a GitHub repository.
2. Open Netlify and choose **Add new project**.
3. Choose **Import an existing project**.
4. Connect your GitHub account and select this repository.
5. Use these build settings:
   - Build command: leave empty
   - Publish directory: `.`
6. Deploy the site.
7. In Netlify, open the deployed project and go to **Project configuration > Environment variables**.
8. Add these variables:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASS`
   - `SMTP_FROM`
9. Redeploy the site after adding the variables.
10. Test the portal email button from the live Netlify URL.

## Gmail SMTP Example

For Gmail, use an app password, not your normal Gmail password.

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-google-app-password
SMTP_FROM=your-email@gmail.com
```

## Notes

- Do not upload `.env.local` to GitHub or Netlify.
- The app keeps calling `/api/send-invoice-email`; Netlify redirects it to `/.netlify/functions/send-invoice-email`.
- If Netlify cannot render the full browser-generated PDF, the function falls back to a simple PDF attachment so email sending can still complete.
