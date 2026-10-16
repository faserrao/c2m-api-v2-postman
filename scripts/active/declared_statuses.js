/**
 * declared_statuses.js — D7: the HTTP statuses each OpenAPI operation declares.
 *
 * Shared by add_tests.js and add_tests_jwt.js, so every request's Newman status
 * assertion lists exactly its own operation's responses (from the spec, which is
 * generated from the DD and the auth overlay) instead of one global list.
 * validate_pipeline_consistency.py checks the result (B-TEST-STATUS-ASSERTION).
 */

const fs = require('fs');
const yaml = require('js-yaml');

const HTTP_METHODS = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'];

/** {"POST /static": [200, 400, ...]} for every operation in the spec at specPath. */
function loadDeclaredStatuses(specPath) {
  const spec = yaml.load(fs.readFileSync(specPath, 'utf-8'));
  const table = {};
  for (const [p, pathItem] of Object.entries(spec.paths || {})) {
    for (const method of HTTP_METHODS) {
      const op = (pathItem || {})[method];
      if (!op) continue;
      const codes = Object.keys(op.responses || {})
        .filter(code => /^\d{3}$/.test(code))
        .map(Number)
        .sort((a, b) => a - b);
      if (codes.length === 0) {
        throw new Error(`${method.toUpperCase()} ${p} declares no numeric response statuses`);
      }
      table[`${method.toUpperCase()} ${p}`] = codes;
    }
  }
  if (Object.keys(table).length === 0) {
    throw new Error(`no operations found in ${specPath}`);
  }
  return table;
}

/** "POST /auth/tokens/{tokenId}/revoke" for a Postman request (":tokenId" → "{tokenId}"). */
function operationKey(request) {
  const url = request.url || {};
  const segments = Array.isArray(url.path) ? url.path : [];
  const p = '/' + segments.join('/');
  return `${(request.method || '').toUpperCase()} ${p.replace(/\/:([A-Za-z_]\w*)/g, '/{$1}')}`;
}

/** The statuses declared for this request's operation; throws if the spec has no such operation. */
function statusesForRequest(request, table) {
  const key = operationKey(request);
  const codes = table[key];
  if (!codes) {
    throw new Error(`${key} is not an operation in the spec — cannot tell which statuses it may return`);
  }
  return codes;
}

/** The Newman test line asserting the response status is one the operation declares. */
function statusTest(codes) {
  const list = codes.join(',');
  return `pm.test("Status code is one this operation declares (${list})", function () { pm.expect([${list}]).to.include(pm.response.code); });`;
}

module.exports = { loadDeclaredStatuses, operationKey, statusesForRequest, statusTest };
