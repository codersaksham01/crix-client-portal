const sendInvoiceEmail = require('../../api/send-invoice-email');

function parseBody(event) {
  if (!event.body) return {};
  const raw = event.isBase64Encoded
    ? Buffer.from(event.body, 'base64').toString('utf8')
    : event.body;
  return raw ? JSON.parse(raw) : {};
}

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
      body: '',
    };
  }

  return new Promise((resolve) => {
    const headers = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    let statusCode = 200;

    const req = {
      method: event.httpMethod,
      headers: event.headers || {},
      body: parseBody(event),
    };

    const res = {
      setHeader(name, value) {
        headers[name] = value;
      },
      status(code) {
        statusCode = code;
        return this;
      },
      json(body) {
        resolve({
          statusCode,
          headers: {
            ...headers,
            'Content-Type': 'application/json; charset=utf-8',
          },
          body: JSON.stringify(body),
        });
      },
    };

    Promise.resolve(sendInvoiceEmail(req, res)).catch((error) => {
      resolve({
        statusCode: 500,
        headers: {
          ...headers,
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({
          ok: false,
          error: error.message || 'Unable to send email',
        }),
      });
    });
  });
};
