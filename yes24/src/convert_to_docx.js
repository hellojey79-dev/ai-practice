/**
 * eda_report.md → eda_report.docx 변환 스크립트
 * docx npm 패키지를 이용해 Word 문서를 생성합니다.
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
// 공통 스타일 상수
// ───────────────────────────────────────────────────────────────────────────
const FONT_KO = "맑은 고딕";
const FONT_EN = "Calibri";
const TABLE_WIDTH = 9100; // DXA (약 16cm)
const COLOR_HEADER_BG = "1F4E79"; // 진한 파랑
const COLOR_HEADER_FG = "FFFFFF"; // 흰색
const COLOR_ROW_ALT = "D6E4F0"; // 연한 파랑 (짝수 행)
const COLOR_ACCENT = "2E74B5"; // 중간 파랑 (소제목)
const COLOR_BLOCKQUOTE = "404040"; // 인용 텍스트 색

// ───────────────────────────────────────────────────────────────────────────
// 헬퍼 함수
// ───────────────────────────────────────────────────────────────────────────

/** 빈 단락 생성 */
function emptyPara(spacing = 80) {
  return new Paragraph({ spacing: { after: spacing } });
}

/** 수평 구분선 (단락 하단 경계선) */
function hrLine() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E74B5" } },
    spacing: { after: 160 },
  });
}

/** 일반 텍스트 단락 */
function bodyPara(text, options = {}) {
  // **bold**, *italic* 간단 파싱
  const runs = parseInline(text, { size: 22, font: FONT_KO, ...options });
  return new Paragraph({
    children: runs,
    spacing: { after: 120 },
    alignment: options.alignment || AlignmentType.LEFT,
  });
}

/** 인라인 마크다운(**bold**, *italic*, `code`) 간단 파싱 */
function parseInline(text, baseOpts = {}) {
  const runs = [];
  // 패턴: **bold**, *italic*, `code`
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g;
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      runs.push(
        new TextRun({
          text: text.slice(lastIndex, match.index),
          font: baseOpts.font || FONT_KO,
          size: baseOpts.size || 22,
          color: baseOpts.color,
        })
      );
    }
    if (match[2]) {
      // **bold**
      runs.push(
        new TextRun({
          text: match[2],
          bold: true,
          font: baseOpts.font || FONT_KO,
          size: baseOpts.size || 22,
          color: baseOpts.color,
        })
      );
    } else if (match[3]) {
      // *italic*
      runs.push(
        new TextRun({
          text: match[3],
          italics: true,
          font: baseOpts.font || FONT_KO,
          size: baseOpts.size || 22,
          color: baseOpts.color,
        })
      );
    } else if (match[4]) {
      // `code`
      runs.push(
        new TextRun({
          text: match[4],
          font: "Consolas",
          size: 20,
          color: "C0392B",
        })
      );
    }
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    runs.push(
      new TextRun({
        text: text.slice(lastIndex),
        font: baseOpts.font || FONT_KO,
        size: baseOpts.size || 22,
        color: baseOpts.color,
      })
    );
  }
  return runs.length ? runs : [new TextRun({ text, font: baseOpts.font || FONT_KO, size: baseOpts.size || 22 })];
}

/** 인용 블록 (💡 분석가 해석) */
function blockquotePara(text) {
  // "> **💡 분석가 해석**:" 와 내용 분리
  const cleaned = text.replace(/^>\s*/, "").trim();
  return new Paragraph({
    children: parseInline(cleaned, { size: 20, font: FONT_KO, color: COLOR_BLOCKQUOTE }),
    indent: { left: 400 },
    border: { left: { style: BorderStyle.THICK, size: 12, color: "2E74B5" } },
    spacing: { after: 160 },
    shading: { type: ShadingType.CLEAR, fill: "EBF3FB" },
  });
}

/** 테이블 셀 생성 */
function makeCell(text, opts = {}) {
  const { bold = false, isHeader = false, width, align = AlignmentType.LEFT, colspan = 1 } = opts;
  const bgColor = isHeader ? COLOR_HEADER_BG : opts.bgColor || "FFFFFF";
  const fgColor = isHeader ? COLOR_HEADER_FG : opts.fgColor || "000000";
  const runs = parseInline(text, { bold: isHeader || bold, size: isHeader ? 20 : 19, font: FONT_KO, color: fgColor });
  return new TableCell({
    children: [
      new Paragraph({
        children: runs,
        alignment: align,
        spacing: { before: 60, after: 60 },
      }),
    ],
    shading: { type: ShadingType.CLEAR, fill: bgColor },
    width: width ? { size: width, type: WidthType.DXA } : undefined,
    columnSpan: colspan,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
  });
}

/** 마크다운 테이블 파싱 → docx Table */
function buildTable(lines) {
  // lines: 헤더행, 구분행, 데이터행...
  const rows = [];
  lines.forEach((line, i) => {
    if (i === 1) return; // 구분행(---)
    const cells = line
      .split("|")
      .slice(1, -1)
      .map((c) => c.trim());
    const isHeader = i === 0;
    const colWidth = Math.floor(TABLE_WIDTH / cells.length);
    const bgColor = !isHeader && i % 2 === 0 ? COLOR_ROW_ALT : "FFFFFF";
    rows.push(
      new TableRow({
        children: cells.map((cell) =>
          makeCell(cell, { isHeader, width: colWidth, bgColor: isHeader ? undefined : bgColor })
        ),
        tableHeader: isHeader,
      })
    );
  });

  return new Table({
    rows,
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: Array(rows[0]?.children?.length || 1).fill(
      Math.floor(TABLE_WIDTH / (rows[0]?.children?.length || 1))
    ),
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      right: { style: BorderStyle.SINGLE, size: 4, color: "2E74B5" },
      insideH: { style: BorderStyle.SINGLE, size: 2, color: "BDD7EE" },
      insideV: { style: BorderStyle.SINGLE, size: 2, color: "BDD7EE" },
    },
  });
}

// ───────────────────────────────────────────────────────────────────────────
// 마크다운 파싱 → docx 요소 배열
// ───────────────────────────────────────────────────────────────────────────
function mdToDocx(mdText) {
  const lines = mdText.split("\n");
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // 제목 1
    if (/^#\s+/.test(line)) {
      elements.push(
        new Paragraph({
          text: line.replace(/^#\s+/, "").replace(/[📊]/g, "").trim(),
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 240, after: 120 },
        })
      );
      i++;
      continue;
    }

    // 제목 2
    if (/^##\s+/.test(line)) {
      elements.push(
        new Paragraph({
          text: line.replace(/^##\s+/, "").trim(),
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 240, after: 80 },
        })
      );
      i++;
      continue;
    }

    // 제목 3
    if (/^###\s+/.test(line)) {
      elements.push(
        new Paragraph({
          text: line.replace(/^###\s+/, "").trim(),
          heading: HeadingLevel.HEADING_3,
          spacing: { before: 160, after: 60 },
        })
      );
      i++;
      continue;
    }

    // 제목 4
    if (/^####\s+/.test(line)) {
      elements.push(
        new Paragraph({
          children: [
            new TextRun({
              text: line.replace(/^####\s+/, "").trim(),
              bold: true,
              size: 22,
              font: FONT_KO,
              color: COLOR_ACCENT,
            }),
          ],
          spacing: { before: 120, after: 60 },
        })
      );
      i++;
      continue;
    }

    // 수평선 ---
    if (/^---+\s*$/.test(line)) {
      elements.push(hrLine());
      i++;
      continue;
    }

    // 마크다운 테이블 감지 (|로 시작하는 행 묶음)
    if (/^\|/.test(line)) {
      const tableLines = [];
      while (i < lines.length && /^\|/.test(lines[i])) {
        tableLines.push(lines[i]);
        i++;
      }
      try {
        elements.push(buildTable(tableLines));
        elements.push(emptyPara(120));
      } catch (e) {
        // 테이블 파싱 실패 시 텍스트로
        tableLines.forEach((tl) => elements.push(bodyPara(tl)));
      }
      continue;
    }

    // 인용 블록 > (연속된 라인 묶기)
    if (/^>\s*/.test(line)) {
      const quoteLines = [];
      while (i < lines.length && /^>\s*/.test(lines[i])) {
        quoteLines.push(lines[i].replace(/^>\s*/, ""));
        i++;
      }
      const fullText = quoteLines.join(" ").trim();
      elements.push(blockquotePara(fullText));
      continue;
    }

    // 이미지 참조 (차트 이미지) - 텍스트로 표시
    if (/^!\[/.test(line)) {
      const altMatch = line.match(/^!\[([^\]]+)\]/);
      const altText = altMatch ? altMatch[1] : "차트 이미지";
      elements.push(
        new Paragraph({
          children: [
            new TextRun({
              text: `[차트: ${altText}]`,
              italics: true,
              color: "888888",
              size: 20,
              font: FONT_KO,
            }),
          ],
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
        })
      );
      i++;
      continue;
    }

    // 순서 없는 목록 -
    if (/^(\s*)[-*]\s+/.test(line)) {
      const indent = (line.match(/^(\s*)/)[1].length / 2) * 360;
      const text = line.replace(/^(\s*)[-*]\s+/, "").trim();
      elements.push(
        new Paragraph({
          children: parseInline(text, { size: 22, font: FONT_KO }),
          bullet: { level: indent > 0 ? 1 : 0 },
          spacing: { after: 60 },
          indent: { left: 360 + indent, hanging: 360 },
        })
      );
      i++;
      continue;
    }

    // 번호 목록 1.
    if (/^\d+\.\s+/.test(line)) {
      const text = line.replace(/^\d+\.\s+/, "").trim();
      elements.push(
        new Paragraph({
          children: parseInline(text, { size: 22, font: FONT_KO }),
          numbering: { reference: "numbered", level: 0 },
          spacing: { after: 60 },
        })
      );
      i++;
      continue;
    }

    // 메타 정보 줄 (**작성자**: ...)
    if (/^\*\*[^*]+\*\*:/.test(line)) {
      elements.push(bodyPara(line));
      i++;
      continue;
    }

    // 빈 줄
    if (line.trim() === "") {
      elements.push(emptyPara(60));
      i++;
      continue;
    }

    // 일반 텍스트
    elements.push(bodyPara(line));
    i++;
  }

  return elements;
}

// ───────────────────────────────────────────────────────────────────────────
// 표지 섹션 생성
// ───────────────────────────────────────────────────────────────────────────
function makeCoverSection() {
  return [
    emptyPara(600),
    new Paragraph({
      children: [
        new TextRun({
          text: "yes24 IT/테크 베스트셀러",
          bold: true,
          size: 52,
          font: FONT_KO,
          color: COLOR_HEADER_BG,
        }),
      ],
      alignment: AlignmentType.CENTER,
      spacing: { after: 80 },
    }),
    new Paragraph({
      children: [
        new TextRun({
          text: "심층 탐색적 데이터 분석(EDA) 보고서",
          bold: true,
          size: 40,
          font: FONT_KO,
          color: COLOR_ACCENT,
        }),
      ],
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
    new Paragraph({
      children: [new PageBreak()],
    }),
  ];
}

// ───────────────────────────────────────────────────────────────────────────
// 번호 목록 설정
// ───────────────────────────────────────────────────────────────────────────
const numberingConfig = {
  config: [
    {
      reference: "numbered",
      levels: [
        {
          level: 0,
          format: "decimal",
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: { indent: { left: 720, hanging: 360 } },
            run: { font: FONT_KO, size: 22 },
          },
        },
      ],
    },
  ],
};

// ───────────────────────────────────────────────────────────────────────────
// 메인 실행
// ───────────────────────────────────────────────────────────────────────────
async function main() {
  const mdPath = path.join(__dirname, "../docs/eda_report.md");
  const outPath = path.join(__dirname, "../docs/eda_report.docx");

  if (!fs.existsSync(mdPath)) {
    console.error(`❌ 파일을 찾을 수 없습니다: ${mdPath}`);
    process.exit(1);
  }

  const mdText = fs.readFileSync(mdPath, "utf-8");
  console.log(`✅ 마크다운 파일 로드 완료 (${mdText.length}자)`);

  const bodyElements = mdToDocx(mdText);
  const coverElements = makeCoverSection();

  const doc = new Document({
    numbering: numberingConfig,
    styles: {
      default: {
        document: {
          run: { font: FONT_KO, size: 22 },
        },
      },
      paragraphStyles: [
        {
          id: "Heading1",
          name: "Heading 1",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: FONT_KO, size: 36, bold: true, color: COLOR_HEADER_BG },
          paragraph: {
            spacing: { before: 240, after: 120 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E74B5" } },
          },
        },
        {
          id: "Heading2",
          name: "Heading 2",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: FONT_KO, size: 28, bold: true, color: COLOR_ACCENT },
          paragraph: { spacing: { before: 200, after: 80 } },
        },
        {
          id: "Heading3",
          name: "Heading 3",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { font: FONT_KO, size: 24, bold: true, color: "1A5276" },
          paragraph: { spacing: { before: 160, after: 60 } },
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: 12240, height: 15840 }, // A4
            margin: { top: 1080, bottom: 1080, left: 1260, right: 1260 },
          },
        },
        children: [...coverElements, ...bodyElements],
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buffer);

  const stats = fs.statSync(outPath);
  console.log(`✅ 변환 완료: ${outPath}`);
  console.log(`📄 파일 크기: ${(stats.size / 1024).toFixed(1)} KB`);
}

main().catch((err) => {
  console.error("❌ 변환 중 오류 발생:", err);
  process.exit(1);
});
