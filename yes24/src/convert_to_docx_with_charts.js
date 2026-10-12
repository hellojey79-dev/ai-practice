/**
 * eda_report.md → eda_report.docx (차트 이미지 포함 버전)
 * 각 통계표 아래에 대응하는 차트 이미지를 삽입합니다.
 */

const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
  WidthType,
  AlignmentType,
  BorderStyle,
  ShadingType,
  PageBreak,
  ImageRun,
} = require("docx");
const fs = require("fs");
const path = require("path");

// ───────────────────────────────────────────────────────────────────────────
// 경로 설정
// ───────────────────────────────────────────────────────────────────────────
const BASE_DIR   = path.join(__dirname, "..");
const MD_PATH    = path.join(BASE_DIR, "docs", "eda_report.md");
const OUT_PATH   = path.join(BASE_DIR, "docs", "eda_report_with_charts.docx");
const IMG_DIR    = path.join(BASE_DIR, "images");

// 차트 번호 → 이미지 파일명 매핑
const CHART_IMAGES = {
  1:  "01_price_distribution.png",
  2:  "02_rating_distribution.png",
  3:  "03_sales_index_distribution.png",
  4:  "04_year_distribution.png",
  5:  "05_top30_publishers.png",
  6:  "06_top30_tags.png",
  7:  "07_tfidf_top30_keywords.png",
  8:  "08_publisher_price_sales_bivariate.png",
  9:  "09_price_bracket_sales_boxplot.png",
  10: "10_rating_vs_reviews_scatter.png",
  11: "11_correlation_matrix_heatmap.png",
  12: "12_year_price_sales_pivot_heatmap.png",
};

// ───────────────────────────────────────────────────────────────────────────
// 공통 스타일 상수
// ───────────────────────────────────────────────────────────────────────────
const FONT_KO       = "맑은 고딕";
const TABLE_WIDTH   = 9100;   // DXA
const COLOR_HDR_BG  = "1F4E79";
const COLOR_HDR_FG  = "FFFFFF";
const COLOR_ROW_ALT = "D6E4F0";
const COLOR_ACCENT  = "2E74B5";
const COLOR_QUOTE   = "404040";
// 이미지 최대 너비: A4 본문 여백 기준 (DXA → EMU 변환: 1 DXA = 914.4 EMU)
// 본문 너비 약 8720 DXA → px 기준 약 680px (96dpi 기준)
const IMG_MAX_W_PX  = 660;

// ───────────────────────────────────────────────────────────────────────────
// 헬퍼 함수
// ───────────────────────────────────────────────────────────────────────────
function emptyPara(spacing = 80) {
  return new Paragraph({ spacing: { after: spacing } });
}

function hrLine() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E74B5" } },
    spacing: { after: 160 },
  });
}

/** 인라인 마크다운(**bold**, *italic*, `code`) 파싱 */
function parseInline(text, baseOpts = {}) {
  const runs = [];
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let lastIndex = 0;
  let m;
  while ((m = regex.exec(text)) !== null) {
    if (m.index > lastIndex) {
      runs.push(new TextRun({
        text: text.slice(lastIndex, m.index),
        font: baseOpts.font || FONT_KO,
        size: baseOpts.size || 22,
        color: baseOpts.color,
      }));
    }
    if (m[2]) {
      runs.push(new TextRun({ text: m[2], bold: true, font: baseOpts.font || FONT_KO, size: baseOpts.size || 22, color: baseOpts.color }));
    } else if (m[3]) {
      runs.push(new TextRun({ text: m[3], italics: true, font: baseOpts.font || FONT_KO, size: baseOpts.size || 22, color: baseOpts.color }));
    } else if (m[4]) {
      runs.push(new TextRun({ text: m[4], font: "Consolas", size: 20, color: "C0392B" }));
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    runs.push(new TextRun({
      text: text.slice(lastIndex),
      font: baseOpts.font || FONT_KO,
      size: baseOpts.size || 22,
      color: baseOpts.color,
    }));
  }
  return runs.length
    ? runs
    : [new TextRun({ text, font: baseOpts.font || FONT_KO, size: baseOpts.size || 22 })];
}

function bodyPara(text, opts = {}) {
  return new Paragraph({
    children: parseInline(text, { size: 22, font: FONT_KO, ...opts }),
    spacing: { after: 120 },
    alignment: opts.alignment || AlignmentType.LEFT,
  });
}

function blockquotePara(text) {
  const cleaned = text.replace(/^>\s*/gm, "").trim();
  return new Paragraph({
    children: parseInline(cleaned, { size: 20, font: FONT_KO, color: COLOR_QUOTE }),
    indent: { left: 400 },
    border: { left: { style: BorderStyle.THICK, size: 12, color: "2E74B5" } },
    spacing: { after: 160 },
    shading: { type: ShadingType.CLEAR, fill: "EBF3FB" },
  });
}

function makeCell(text, opts = {}) {
  const { isHeader = false, width, align = AlignmentType.LEFT, bgColor } = opts;
  const bg = isHeader ? COLOR_HDR_BG : (bgColor || "FFFFFF");
  const fg = isHeader ? COLOR_HDR_FG : "000000";
  return new TableCell({
    children: [new Paragraph({
      children: parseInline(text, { bold: isHeader, size: isHeader ? 20 : 19, font: FONT_KO, color: fg }),
      alignment: align,
      spacing: { before: 60, after: 60 },
    })],
    shading: { type: ShadingType.CLEAR, fill: bg },
    width: width ? { size: width, type: WidthType.DXA } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
  });
}

function buildTable(lines) {
  const rows = [];
  lines.forEach((line, i) => {
    if (i === 1) return; // 구분행(---)
    const cells = line.split("|").slice(1, -1).map(c => c.trim());
    const isHeader = i === 0;
    const colW = Math.floor(TABLE_WIDTH / cells.length);
    const bgColor = !isHeader && i % 2 === 0 ? COLOR_ROW_ALT : "FFFFFF";
    rows.push(new TableRow({
      children: cells.map(cell => makeCell(cell, { isHeader, width: colW, bgColor: isHeader ? undefined : bgColor })),
      tableHeader: isHeader,
    }));
  });
  return new Table({
    rows,
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: Array(rows[0].children.length).fill(Math.floor(TABLE_WIDTH / rows[0].children.length)),
    borders: {
      top:     { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      bottom:  { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      left:    { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      right:   { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      insideH: { style: BorderStyle.SINGLE, size: 2, color: "BDD7EE" },
      insideV: { style: BorderStyle.SINGLE, size: 2, color: "BDD7EE" },
    },
  });
}

// ───────────────────────────────────────────────────────────────────────────
// 이미지 삽입 헬퍼
// ───────────────────────────────────────────────────────────────────────────
function getImageSize(imgPath) {
  // PNG 헤더에서 너비/높이 읽기 (IHDR 청크: 바이트 16~23)
  const buf = fs.readFileSync(imgPath);
  const w = buf.readUInt32BE(16);
  const h = buf.readUInt32BE(20);
  return { width: w, height: h };
}

function makeImagePara(chartNum) {
  const filename = CHART_IMAGES[chartNum];
  if (!filename) return null;
  const imgPath = path.join(IMG_DIR, filename);
  if (!fs.existsSync(imgPath)) {
    console.warn(`  ⚠️  이미지 없음: ${filename}`);
    return null;
  }
  const imgBuf = fs.readFileSync(imgPath);
  const { width: origW, height: origH } = getImageSize(imgPath);

  // 최대 너비에 맞게 비율 조정
  const scale = Math.min(1, IMG_MAX_W_PX / origW);
  const dispW = Math.round(origW * scale);
  const dispH = Math.round(origH * scale);

  console.log(`  📊 차트 ${chartNum} 삽입: ${filename} (${dispW}×${dispH}px)`);

  return new Paragraph({
    children: [
      new ImageRun({
        data: imgBuf,
        transformation: { width: dispW, height: dispH },
        type: "png",
      }),
    ],
    alignment: AlignmentType.CENTER,
    spacing: { before: 80, after: 200 },
  });
}

// ───────────────────────────────────────────────────────────────────────────
// 마크다운 파싱 → docx 요소 배열
// ───────────────────────────────────────────────────────────────────────────
function mdToDocx(mdText) {
  const lines   = mdText.split("\n");
  const elements = [];
  let i = 0;
  let currentChartNum = null; // 현재 처리 중인 차트 번호

  while (i < lines.length) {
    const line = lines[i];

    // H1
    if (/^#\s+/.test(line)) {
      elements.push(new Paragraph({
        text: line.replace(/^#\s+/, "").replace(/[📊]/g, "").trim(),
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 240, after: 120 },
      }));
      i++; continue;
    }

    // H2
    if (/^##\s+/.test(line)) {
      elements.push(new Paragraph({
        text: line.replace(/^##\s+/, "").trim(),
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 240, after: 80 },
      }));
      i++; continue;
    }

    // H3 — 차트 번호 감지
    if (/^###\s+/.test(line)) {
      const h3Text = line.replace(/^###\s+/, "").trim();
      // "차트 N." 패턴에서 번호 추출
      const chartMatch = h3Text.match(/차트\s+(\d+)[.\s]/);
      currentChartNum = chartMatch ? parseInt(chartMatch[1]) : null;
      elements.push(new Paragraph({
        text: h3Text,
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 160, after: 60 },
      }));
      i++; continue;
    }

    // H4
    if (/^####\s+/.test(line)) {
      elements.push(new Paragraph({
        children: [new TextRun({
          text: line.replace(/^####\s+/, "").trim(),
          bold: true, size: 22, font: FONT_KO, color: COLOR_ACCENT,
        })],
        spacing: { before: 120, after: 60 },
      }));
      i++; continue;
    }

    // 수평선
    if (/^---+\s*$/.test(line)) {
      elements.push(hrLine());
      i++; continue;
    }

    // 마크다운 이미지 참조 → 실제 이미지 삽입
    if (/^!\[/.test(line)) {
      if (currentChartNum !== null) {
        const imgPara = makeImagePara(currentChartNum);
        if (imgPara) elements.push(imgPara);
      }
      i++; continue;
    }

    // 마크다운 테이블 (| 로 시작하는 연속 행)
    if (/^\|/.test(line)) {
      const tableLines = [];
      while (i < lines.length && /^\|/.test(lines[i])) {
        tableLines.push(lines[i]);
        i++;
      }
      try {
        elements.push(buildTable(tableLines));
        elements.push(emptyPara(100));
      } catch (e) {
        tableLines.forEach(tl => elements.push(bodyPara(tl)));
      }
      continue;
    }

    // 인용 블록 > (연속 행 묶기)
    if (/^>\s*/.test(line)) {
      const qLines = [];
      while (i < lines.length && /^>\s*/.test(lines[i])) {
        qLines.push(lines[i]);
        i++;
      }
      elements.push(blockquotePara(qLines.join("\n")));
      continue;
    }

    // 순서 없는 목록
    if (/^(\s*)[-*]\s+/.test(line)) {
      const indent = (line.match(/^(\s*)/)[1].length / 2) * 360;
      const text   = line.replace(/^(\s*)[-*]\s+/, "").trim();
      elements.push(new Paragraph({
        children: parseInline(text, { size: 22, font: FONT_KO }),
        bullet: { level: indent > 0 ? 1 : 0 },
        spacing: { after: 60 },
        indent: { left: 360 + indent, hanging: 360 },
      }));
      i++; continue;
    }

    // 번호 목록
    if (/^\d+\.\s+/.test(line)) {
      const text = line.replace(/^\d+\.\s+/, "").trim();
      elements.push(new Paragraph({
        children: parseInline(text, { size: 22, font: FONT_KO }),
        numbering: { reference: "numbered", level: 0 },
        spacing: { after: 60 },
      }));
      i++; continue;
    }

    // 빈 줄
    if (line.trim() === "") {
      elements.push(emptyPara(60));
      i++; continue;
    }

    // 일반 텍스트
    elements.push(bodyPara(line));
    i++;
  }

  return elements;
}

// ───────────────────────────────────────────────────────────────────────────
// 표지 섹션
// ───────────────────────────────────────────────────────────────────────────
function makeCoverSection() {
  return [
    emptyPara(600),
    new Paragraph({
      children: [new TextRun({ text: "yes24 IT/테크 베스트셀러", bold: true, size: 52, font: FONT_KO, color: COLOR_HDR_BG })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
    }),
    new Paragraph({
      children: [new TextRun({ text: "심층 탐색적 데이터 분석(EDA) 보고서", bold: true, size: 40, font: FONT_KO, color: COLOR_ACCENT })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),
    hrLine(),
    new Paragraph({
      children: [
        new TextRun({ text: "작성자: ", bold: true, size: 24, font: FONT_KO }),
        new TextRun({ text: "20년차 수석 데이터 분석가", size: 24, font: FONT_KO }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
    }),
    new Paragraph({
      children: [
        new TextRun({ text: "대상 데이터셋: ", bold: true, size: 24, font: FONT_KO }),
        new TextRun({ text: "yes24/data/yes24_bestseller.csv (총 1,000권)", size: 24, font: "Consolas" }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
    }),
    new Paragraph({
      children: [
        new TextRun({ text: "분석 환경: ", bold: true, size: 24, font: FONT_KO }),
        new TextRun({ text: "Python 3.12 | Matplotlib | Scikit-learn (TF-IDF)", size: 24, font: FONT_KO }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { after: 600 },
    }),
    new Paragraph({ children: [new PageBreak()] }),
  ];
}

// ───────────────────────────────────────────────────────────────────────────
// 번호 목록 설정
// ───────────────────────────────────────────────────────────────────────────
const numberingConfig = {
  config: [{
    reference: "numbered",
    levels: [{
      level: 0,
      format: "decimal",
      text: "%1.",
      alignment: AlignmentType.LEFT,
      style: {
        paragraph: { indent: { left: 720, hanging: 360 } },
        run: { font: FONT_KO, size: 22 },
      },
    }],
  }],
};

// ───────────────────────────────────────────────────────────────────────────
// 메인
// ───────────────────────────────────────────────────────────────────────────
async function main() {
  if (!fs.existsSync(MD_PATH)) {
    console.error(`❌ 파일 없음: ${MD_PATH}`);
    process.exit(1);
  }

  const mdText = fs.readFileSync(MD_PATH, "utf-8");
  console.log(`✅ 마크다운 로드 완료 (${mdText.length}자)`);
  console.log(`📁 이미지 폴더: ${IMG_DIR}`);
  console.log("━".repeat(50));

  const coverElements = makeCoverSection();
  const bodyElements  = mdToDocx(mdText);

  console.log("━".repeat(50));
  console.log(`📝 총 docx 요소: ${coverElements.length + bodyElements.length}개`);

  const doc = new Document({
    numbering: numberingConfig,
    styles: {
      default: {
        document: { run: { font: FONT_KO, size: 22 } },
      },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { font: FONT_KO, size: 36, bold: true, color: COLOR_HDR_BG },
          paragraph: {
            spacing: { before: 240, after: 120 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E74B5" } },
          },
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { font: FONT_KO, size: 28, bold: true, color: COLOR_ACCENT },
          paragraph: { spacing: { before: 200, after: 80 } },
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { font: FONT_KO, size: 24, bold: true, color: "1A5276" },
          paragraph: { spacing: { before: 160, after: 60 } },
        },
      ],
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 }, // A4
          margin: { top: 1080, bottom: 1080, left: 1260, right: 1260 },
        },
      },
      children: [...coverElements, ...bodyElements],
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(OUT_PATH, buffer);
  const stats = fs.statSync(OUT_PATH);
  console.log(`\n✅ 변환 완료: ${OUT_PATH}`);
  console.log(`📄 파일 크기: ${(stats.size / 1024).toFixed(1)} KB`);
}

main().catch(err => {
  console.error("❌ 변환 오류:", err);
  process.exit(1);
});
