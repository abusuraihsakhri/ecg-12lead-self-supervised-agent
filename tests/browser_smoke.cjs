/* Browser calculator regression test without external packages. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/i);
assert.ok(match, "Application script not found");

const elements = new Map();
for (const [id, value] of Object.entries({
  qt: "400", rr: "0.8", "lead-i": "8", "lead-avf": "6"
})) {
  elements.set(id, {value});
}
for (const id of ["qtc-result", "axis-result", "audit-result", "connection", "metrics"]) {
  elements.set(id, {textContent: ""});
}
for (const id of ["qtc-form", "axis-form", "audit-form"]) {
  elements.set(id, {
    addEventListener(event, handler) { this[event] = handler; }
  });
}
elements.set("audit-button", {disabled: true});
const context = {
  document: {getElementById(id) {
    const node = elements.get(id);
    assert.ok(node, "Unexpected DOM lookup: " + id);
    return node;
  }},
  location: {hostname: "example.github.io"},
  fetch() { throw new Error("Static site must not invoke the audit API"); },
};
vm.runInNewContext(match[1], context);
const submit = id => elements.get(id).submit({preventDefault() {}});

submit("qtc-form");
assert.match(elements.get("qtc-result").textContent, /Bazett: 447\.2 ms/);
assert.match(elements.get("qtc-result").textContent, /Framingham: 430\.8 ms/);
assert.match(elements.get("qtc-result").textContent, /Heart rate: 75\.0 bpm/);
submit("axis-form");
assert.match(elements.get("axis-result").textContent, /36\.9°/);
elements.get("lead-i").value = "0";
elements.get("lead-avf").value = "0";
submit("axis-form");
assert.match(elements.get("axis-result").textContent, /undefined/);
assert.equal(elements.get("audit-button").disabled, true);
assert.equal(elements.get("connection").textContent, "Unavailable on GitHub Pages");
console.log("Browser calculator smoke tests passed");
