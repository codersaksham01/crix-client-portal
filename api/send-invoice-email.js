try {
  require('dotenv').config({ path: '.env.local' });
} catch (_) {}

const nodemailer = require('nodemailer');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFile } = require('child_process');

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function money(value) {
  return `Rs. ${Number(value || 0).toLocaleString('en-IN')}`;
}

function formatDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function brandName(value) {
  const saved = String(value || '').trim();
  return !saved || /uday/i.test(saved) ? 'Crixy Ai' : saved;
}

function pdfEscape(value) {
  return String(value ?? '').replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
}

function findBrowserExecutable() {
  const candidates = [
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ].filter(Boolean);
  return candidates.find((candidate) => fs.existsSync(candidate));
}

function renderHtmlToPdfWithLocalBrowser(html, invoiceNumber, browser) {
  return new Promise((resolve, reject) => {

    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'crixy-invoice-'));
    const safeName = String(invoiceNumber || 'invoice').replace(/[^a-z0-9._-]/gi, '-');
    const htmlPath = path.join(dir, `${safeName}.html`);
    const pdfPath = path.join(dir, `${safeName}.pdf`);
    fs.writeFileSync(htmlPath, html, 'utf8');

    const args = [
      '--headless',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--no-sandbox',
      '--no-pdf-header-footer',
      '--print-to-pdf-no-header',
      `--print-to-pdf=${pdfPath}`,
      `file:///${htmlPath.replace(/\\/g, '/')}`,
    ];

    execFile(browser, args, { timeout: 45000 }, (error) => {
      try {
        if (error) throw error;
        if (!fs.existsSync(pdfPath)) throw new Error('Browser did not create the invoice PDF');
        const buffer = fs.readFileSync(pdfPath);
        if (!buffer.length) throw new Error('Browser created an empty invoice PDF');
        resolve(buffer);
      } catch (err) {
        reject(err);
      } finally {
        try { fs.rmSync(dir, { recursive: true, force: true }); } catch (_) {}
      }
    });
  });
}

async function renderHtmlToPdfWithChromium(html) {
  let browser;
  try {
    const chromium = require('@sparticuz/chromium');
    const puppeteer = require('puppeteer-core');
    browser = await puppeteer.launch({
      args: chromium.args,
      defaultViewport: chromium.defaultViewport,
      executablePath: await chromium.executablePath(),
      headless: chromium.headless,
    });

    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });
    return await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: { top: '0', right: '0', bottom: '0', left: '0' },
    });
  } finally {
    if (browser) await browser.close();
  }
}

async function renderHtmlToPdf(html, invoiceNumber) {
  const browser = findBrowserExecutable();
  if (browser) {
    return renderHtmlToPdfWithLocalBrowser(html, invoiceNumber, browser);
  }
  return renderHtmlToPdfWithChromium(html);
}

function createSimpleInvoicePdf(payload) {
  const invoice = payload.invoice || {};
  const client = payload.client || {};
  const payment = payload.payment || {};
  const lines = [
    `${brandName(payload.fromName)} - Invoice`,
    `Invoice No: ${invoice.number || '-'}`,
    `Client: ${client.name || 'Client'}`,
    client.company ? `Company: ${client.company}` : '',
    client.email ? `Email: ${client.email}` : '',
    `Description: ${invoice.description || 'Service'}`,
    `Total: ${money(invoice.total)}`,
    `Paid: ${money(invoice.paid)}`,
    `Balance Due: ${money(invoice.balance)}`,
    `Due Date: ${invoice.dueDate || '-'}`,
    '',
    'Payment Details',
    `UPI ID: ${payment.upi || ''}`,
    `Payee: ${payment.payee || ''}`,
    `Reference: ${payment.reference || invoice.number || ''}`,
    payload.portalLink ? `Portal: ${payload.portalLink}` : '',
  ].filter(Boolean);

  const content = [
    'BT',
    '/F1 24 Tf',
    '50 780 Td',
    `(INVOICE) Tj`,
    '/F1 11 Tf',
    '0 -36 Td',
    ...lines.map((line) => [`(${pdfEscape(line)}) Tj`, '0 -18 Td']).flat(),
    'ET',
  ].join('\n');

  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    `<< /Length ${Buffer.byteLength(content, 'utf8')} >>\nstream\n${content}\nendstream`,
  ];

  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(Buffer.byteLength(pdf, 'utf8'));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = Buffer.byteLength(pdf, 'utf8');
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (let i = 1; i < offsets.length; i += 1) {
    pdf += `${String(offsets[i]).padStart(10, '0')} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return Buffer.from(pdf, 'utf8');
}

async function createInvoicePdf(payload) {
  const hasDocumentPayload = Boolean(payload.invoice || payload.quotation || payload.kind === 'quotation');
  if (hasDocumentPayload && !payload.pdfHtml) {
    throw new Error('Premium PDF HTML was not received. Refresh the deployed site and confirm Admin Settings uses /api/send-invoice-email.');
  }

  if (payload.pdfHtml) {
    try {
      const number = payload.invoice?.number || payload.quotation?.number || payload.quotation?.quoteNumber || 'document';
      const buffer = await renderHtmlToPdf(payload.pdfHtml, number);
      return { buffer, source: 'premium-html' };
    } catch (error) {
      throw new Error(`Premium PDF render failed: ${error.message}`);
    }
  }
  return { buffer: createSimpleInvoicePdf(payload), source: 'simple-fallback' };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  try {
    const payload = req.body || {};
    const client = payload.client || {};
    const to = String(payload.to || client.email || '').trim();
    if (!to || !to.includes('@')) {
      return res.status(400).json({ ok: false, error: 'Recipient email is missing or invalid. Add the client email before sending.' });
    }

    const host = process.env.SMTP_HOST;
    const port = Number(process.env.SMTP_PORT || 587);
    const user = process.env.SMTP_USER;
    const pass = process.env.SMTP_PASS;
    const from = process.env.SMTP_FROM || user;

    if (!host || !user || !pass || !from) {
      return res.status(500).json({ ok: false, error: 'SMTP environment variables are missing' });
    }

    const transporter = nodemailer.createTransport({
      host,
      port,
      secure: port === 465,
      auth: { user, pass },
    });

    const isQuotation = payload.kind === 'quotation' || payload.quotation;
    const invoice = isQuotation ? (payload.quotation || {}) : (payload.invoice || {});
    const payment = payload.payment || {};
    const senderName = brandName(payload.fromName);
    const docLabel = isQuotation ? 'Quotation' : 'Invoice';
    const docNumber = invoice.number || invoice.quoteNumber || '';
    const subject = String(payload.subject || `${docLabel} ${docNumber}`).replace(/Uday Technologies/gi, senderName).replace(/\bUday\b/gi, 'Crixy');
    const text = String(payload.body || '').replace(/Uday Technologies/gi, senderName).replace(/\bUday\b/gi, 'Crixy');
    const balanceDue = Number(invoice.balance || 0);
    const statusLabel = String(invoice.status || (isQuotation ? 'draft' : (balanceDue <= 0 ? 'paid' : 'sent'))).replace(/^\w/, (letter) => letter.toUpperCase());
    const portalButton = payload.portalLink
      ? `<a href="${escapeHtml(payload.portalLink)}" style="display:inline-block;background:#111827;color:#ffffff;text-decoration:none;padding:12px 18px;border-radius:8px;font-weight:700;margin-top:6px">Open Client Portal</a>`
      : '';
    const amountLabel = isQuotation ? 'Quoted Amount' : 'Total Amount';
    const introCopy = isQuotation
      ? `Greetings from <strong>${escapeHtml(senderName)}</strong>. Please find the quotation summary below. The original detailed quotation PDF is attached with the complete service scope, business growth plan, validity, terms, and signature area.`
      : `Greetings from <strong>${escapeHtml(senderName)}</strong>. Please find the invoice summary below. The original detailed invoice PDF is attached with the complete layout, QR code, payment details, tax summary, terms, and signature area.`;
    const amountRows = isQuotation ? `
              <tr>
                <td style="padding:14px;color:#111827;font-size:13px;font-weight:800;text-transform:uppercase">${amountLabel}</td>
                <td style="padding:14px;text-align:right;color:#111827;font-size:18px;font-weight:900">${money(invoice.total || invoice.amount)}</td>
              </tr>
    ` : `
              <tr>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">${amountLabel}</td>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right;font-weight:700">${money(invoice.total)}</td>
              </tr>
              <tr style="background:#f9fafb">
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">Amount Paid</td>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right;color:#047857;font-weight:700">${money(invoice.paid)}</td>
              </tr>
              <tr>
                <td style="padding:14px;color:#111827;font-size:13px;font-weight:800;text-transform:uppercase">Balance Due</td>
                <td style="padding:14px;text-align:right;color:${balanceDue > 0 ? '#b91c1c' : '#047857'};font-size:18px;font-weight:900">${money(invoice.balance)}</td>
              </tr>
    `;
    const paymentBlock = isQuotation ? '' : `
            <div style="background:#111827;color:#ffffff;border-radius:10px;padding:18px 20px;margin:18px 0;word-break:break-word">
              <div style="font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#a3a3a3;font-weight:800;margin-bottom:10px">Payment Details</div>
              <div style="line-height:1.8">
                <strong>UPI ID:</strong> ${escapeHtml(payment.upi || '')}<br>
                <strong>Payee:</strong> ${escapeHtml(payment.payee || '')}<br>
                <strong>Reference:</strong> ${escapeHtml(payment.reference || docNumber || '')}
              </div>
            </div>
    `;
    const html = `
      <div style="margin:0;padding:24px;background:#f3f4f6;font-family:Arial,sans-serif;color:#111827">
        <div style="max-width:680px;margin:0 auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden">
          <div style="background:#050505;color:#ffffff;padding:22px 26px">
            <div style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#a3a3a3;font-weight:700">${docLabel} Shared</div>
            <h1 style="margin:6px 0 0;font-size:24px;line-height:1.25">${escapeHtml(subject)}</h1>
          </div>
          <div style="padding:26px">
            <p style="margin:0 0 12px;font-size:15px">Dear ${escapeHtml(client.name || 'Client')},</p>
            <p style="margin:0 0 18px;line-height:1.7;color:#374151">
              ${introCopy}
            </p>

            <table style="border-collapse:collapse;width:100%;margin:18px 0;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;table-layout:fixed">
              <tr style="background:#f9fafb">
                <td style="width:42%;padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">${docLabel} No.</td>
                <td style="width:58%;padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right;font-weight:700;word-break:break-word">${escapeHtml(docNumber || '-')}</td>
              </tr>
              <tr>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">Description</td>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right;word-break:break-word">${escapeHtml(invoice.description || 'Service')}</td>
              </tr>
              <tr style="background:#f9fafb">
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">Issue Date</td>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right">${escapeHtml(formatDate(invoice.issueDate))}</td>
              </tr>
              <tr>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">${isQuotation ? 'Valid Until' : 'Due Date'}</td>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right">${escapeHtml(formatDate(invoice.dueDate || invoice.validUntil))}</td>
              </tr>
              <tr style="background:#f9fafb">
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:12px;font-weight:700;text-transform:uppercase">Status</td>
                <td style="padding:12px 14px;border-bottom:1px solid #e5e7eb;text-align:right;font-weight:700;word-break:break-word">${escapeHtml(statusLabel)}</td>
              </tr>
              ${amountRows}
            </table>

            ${paymentBlock}

            ${portalButton}

            <p style="margin:22px 0 0;line-height:1.7;color:#374151">
              For sales and support, contact <strong>sales@usecrixy.com</strong>.<br>
              For official inquiries, contact <strong>sakshamsingh@usecrixy.com</strong>.<br>
              Website: <strong>www.usecrixy.com</strong>
            </p>

            <p style="margin:22px 0 0">Regards,<br><strong>${escapeHtml(senderName)}</strong></p>
          </div>
        </div>
      </div>
    `;

    const pdf = await createInvoicePdf(payload);

    await transporter.sendMail({
      from: `"${senderName}" <${from}>`,
      to,
      subject,
      text,
      html,
      attachments: [
        {
          filename: `${docNumber || (isQuotation ? 'quotation' : 'invoice')}.pdf`,
          content: pdf.buffer,
          contentType: 'application/pdf',
        },
      ],
    });

    return res.status(200).json({ ok: true, pdf: pdf.source, version: 'premium-pdf-2026-07-16' });
  } catch (error) {
    return res.status(500).json({ ok: false, error: error.message || 'Unable to send email' });
  }
};
