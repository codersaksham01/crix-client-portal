require('dotenv').config({ path: '.env.local' });

const http = require('http');
const fs = require('fs');
const path = require('path');
const sendInvoiceEmail = require('./api/send-invoice-email');

const port = Number(process.env.PORT || 3000);
const root = __dirname;

const types = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
};

function sendJson(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

function makeRes(res) {
  return {
    setHeader: (...args) => res.setHeader(...args),
    status(code) {
      this.statusCode = code;
      return this;
    },
    json(body) {
      sendJson(res, this.statusCode || 200, body);
    },
  };
}

function readJson(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => {
      data += chunk;
      if (data.length > 10_000_000) {
        reject(new Error('Request body too large'));
        req.destroy();
      }
    });
    req.on('end', () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (error) {
        reject(error);
      }
    });
    req.on('error', reject);
  });
}

function serveFile(req, res) {
  let urlPath = '/';
  try {
    urlPath = decodeURIComponent((req.url || '/').split('?')[0]);
  } catch (_) {
    res.writeHead(400);
    res.end('Bad request');
    return;
  }
  const safePath = path.normalize(urlPath).replace(/^(\.\.[/\\])+/, '');
  let filePath = path.join(root, safePath === '/' ? 'index.html' : safePath);
  const resolvedRoot = path.resolve(root);
  const resolvedFilePath = path.resolve(filePath);

  if (resolvedFilePath !== resolvedRoot && !resolvedFilePath.startsWith(resolvedRoot + path.sep)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
    filePath = path.join(root, 'index.html');
  }

  const ext = path.extname(filePath).toLowerCase();
  res.writeHead(200, { 'Content-Type': types[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
}

const server = http.createServer(async (req, res) => {
  if (req.url && req.url.startsWith('/api/send-invoice-email')) {
    try {
      req.body = await readJson(req);
      await sendInvoiceEmail(req, makeRes(res));
    } catch (error) {
      sendJson(res, 500, { ok: false, error: error.message || 'Server error' });
    }
    return;
  }

  serveFile(req, res);
});

server.listen(port, () => {
  console.log(`Crixy portal running at http://localhost:${port}`);
});
