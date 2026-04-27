const fs = require("fs");
const zlib = require("zlib");

const pdfPath = "C:\\Users\\hp\\Downloads\\bda_project.pdf";
const outPath = "C:\\Users\\hp\\Desktop\\BDA-PROJECT\\pdf_extracted.txt";

const bytes = fs.readFileSync(pdfPath);
const text = bytes.toString("latin1");

function cleanText(input) {
  return input
    .replace(/\\\(/g, "(")
    .replace(/\\\)/g, ")")
    .replace(/\\\\/g, "\\")
    .replace(/\\([0-7]{3})/g, (_, oct) => String.fromCharCode(parseInt(oct, 8)));
}

const objectRegex = /(\d+)\s+0\s+obj([\s\S]*?)endobj/g;
const out = [];
let match;

while ((match = objectRegex.exec(text)) !== null) {
  const objNum = match[1];
  const body = match[2];

  if (!body.includes("stream") || !body.includes("/FlateDecode")) continue;

  const streamIdx = body.indexOf("stream");
  let streamText = body.slice(streamIdx + 6).replace(/^\r?\n/, "");
  const endIdx = streamText.indexOf("endstream");
  if (endIdx < 0) continue;
  streamText = streamText.slice(0, endIdx).replace(/\r?\n$/, "");

  let decoded;
  try {
    decoded = zlib.inflateSync(Buffer.from(streamText, "latin1")).toString("latin1");
  } catch {
    continue;
  }

  const parts = [];
  const tjArrayRegex = /\[(.*?)\]\s*TJ/gs;
  let tjArray;
  while ((tjArray = tjArrayRegex.exec(decoded)) !== null) {
    const segRegex = /\((?:\\.|[^\\)])*\)/g;
    const segments = tjArray[1].match(segRegex) || [];
    for (const seg of segments) {
      parts.push(cleanText(seg.slice(1, -1)));
    }
  }

  const tjRegex = /\((?:\\.|[^\\)])*\)\s*Tj/gs;
  let tj;
  while ((tj = tjRegex.exec(decoded)) !== null) {
    const value = tj[0];
    const open = value.indexOf("(");
    const close = value.lastIndexOf(")");
    parts.push(cleanText(value.slice(open + 1, close)));
  }

  const joined = parts.join("").replace(/\s{2,}/g, " ").trim();
  if (joined) {
    out.push(`===== OBJECT ${objNum} =====\n${joined}\n`);
  }
}

fs.writeFileSync(outPath, out.join("\n"), "utf8");
console.log(`Wrote ${outPath}`);
