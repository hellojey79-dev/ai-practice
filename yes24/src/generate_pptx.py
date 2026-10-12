"""
yes24 IT/테크 베스트셀러 심층 EDA 보고서 기반 30페이지 PPTX 슬라이드 생성 스크립트
디자인 스타일: Nordic Minimalism 인포그래픽
폰트: 제목(G마켓 산스 Bold), 본문(나눔고딕)
슬라이드 노트: 전 슬라이드 2분 분량(약 450~600자) 구어체 대본 수록
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 1. 디자인 컬러 팔레트 (Nordic Minimalism)
COLOR_BG_LIGHT = RGBColor(0xF4, 0xF1, 0xEC)       # Warm Cream 배경
COLOR_BG_WHITE = RGBColor(0xFC, 0xFA, 0xF7)       # Soft White 카드 배경
COLOR_BG_DARK = RGBColor(0x25, 0x2B, 0x26)        # Deep Pine Forest 간지 배경
COLOR_TEXT_MAIN = RGBColor(0x3D, 0x35, 0x30)      # Deep Warm Charcoal 본문
COLOR_TEXT_MUTED = RGBColor(0x7A, 0x6F, 0x66)     # Taupe 보조 텍스트
COLOR_PRIMARY = RGBColor(0x26, 0x21, 0x1D)        # 짙은 타이틀
COLOR_ACCENT = RGBColor(0x5A, 0x6B, 0x5C)         # Nordic Sage Green 강조
COLOR_ACCENT_DARK = RGBColor(0x38, 0x46, 0x3A)    # Deep Sage Green
COLOR_BORDER = RGBColor(0xDD, 0xD6, 0xCC)         # 연한 베이지 경계선
COLOR_CARD_HEADER = RGBColor(0xEA, 0xE4, 0xDA)    # 카드 헤더 틴트
COLOR_BADGE_BG = RGBColor(0xE2, 0xDB, 0xD0)       # 배지 배경
COLOR_CALLOUT_BG = RGBColor(0xEB, 0xE6, 0xDF)     # 인사이트 박스 배경

# 2. 타이포그래피 설정
FONT_TITLE = "G마켓 산스 Bold"
FONT_TITLE_FALLBACK = "Gmarket Sans Bold"
FONT_BODY = "나눔고딕"
FONT_BODY_FALLBACK = "NanumGothic"

def set_font(run, font_name, size_pt, bold=False, color=COLOR_TEXT_MAIN):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = color

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # 헬퍼 함수들
    def add_bg(slide, color=COLOR_BG_LIGHT):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text=None, is_dark=False):
        if category_text:
            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(2.2), Inches(0.35))
            badge.fill.solid()
            badge.fill.fore_color.rgb = COLOR_ACCENT if is_dark else COLOR_BADGE_BG
            badge.line.fill.background()
            p = badge.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = category_text
            set_font(r, FONT_TITLE, 11, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC) if is_dark else COLOR_TEXT_MAIN)
            badge.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.85 if category_text else 0.5), Inches(11.733), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = title_text
        set_font(r, FONT_TITLE, 26, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC) if is_dark else COLOR_PRIMARY)

        # 미니멀 구분선
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.65 if category_text else 1.3), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_ACCENT if is_dark else COLOR_ACCENT
        line.line.fill.background()

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    def add_card(slide, left, top, width, height, bg_color=COLOR_BG_WHITE, border_color=COLOR_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    def add_callout(slide, left, top, width, height, text_title, text_body):
        card = add_card(slide, left, top, width, height, bg_color=COLOR_CALLOUT_BG, border_color=COLOR_ACCENT)
        # 왼쪽 세이지 그린 세로 액센트 바
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.12), Inches(height))
        bar.fill.solid()
        bar.fill.fore_color.rgb = COLOR_ACCENT
        bar.line.fill.background()

        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.1), Inches(width - 0.4), Inches(height - 0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"💡 {text_title}\n"
        set_font(r, FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)
        
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = text_body
        set_font(r2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    def add_stat_box(slide, left, top, width, height, label, value, subtext=None):
        card = add_card(slide, left, top, width, height, bg_color=COLOR_BG_WHITE, border_color=COLOR_BORDER)
        tb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.12), Inches(width - 0.3), Inches(height - 0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = label + "\n"
        set_font(r, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MUTED)

        p2 = tf.add_paragraph()
        p2.space_before = Pt(2)
        r2 = p2.add_run()
        r2.text = value + ("\n" if subtext else "")
        set_font(r2, FONT_TITLE, 22, bold=True, color=COLOR_ACCENT_DARK)

        if subtext:
            p3 = tf.add_paragraph()
            p3.space_before = Pt(2)
            r3 = p3.add_run()
            r3.text = subtext
            set_font(r3, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    # ==========================================
    # SLIDE 1: 표지 (Title Slide)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, COLOR_BG_LIGHT)
    
    # 상단 장식 배지
    badge1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.666), Inches(1.3), Inches(4.0), Inches(0.45))
    badge1.fill.solid()
    badge1.fill.fore_color.rgb = COLOR_BADGE_BG
    badge1.line.fill.background()
    p = badge1.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "EXPLORATORY DATA ANALYSIS REPORT"
    set_font(r, FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)

    # 메인 타이틀 박스
    tb1 = s1.shapes.add_textbox(Inches(1.5), Inches(2.1), Inches(10.333), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "IT/테크 베스트셀러\n"
    set_font(r, FONT_TITLE, 40, bold=True, color=COLOR_PRIMARY)
    
    p2 = tf1.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(8)
    r2 = p2.add_run()
    r2.text = "심층 탐색적 데이터 분석(EDA) 보고서"
    set_font(r2, FONT_TITLE, 34, bold=True, color=COLOR_ACCENT)

    # 서브타이틀
    p3 = tf1.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(16)
    r3 = p3.add_run()
    r3.text = "1,000권 베스트셀러 데이터로 도출한 도서 가격 구조, 독자 반응 및 생성형 AI 시장 인사이트"
    set_font(r3, FONT_BODY, 16, bold=False, color=COLOR_TEXT_MUTED)

    # 메타정보 인포그래픽 카드 3개
    add_stat_box(s1, 2.5, 4.8, 2.5, 1.4, "대상 데이터셋", "1,000권", "yes24 IT 베스트셀러 전수")
    add_stat_box(s1, 5.4, 4.8, 2.5, 1.4, "분석 페르소나", "수석 분석가", "20년차 데이터 사이언티스트")
    add_stat_box(s1, 8.3, 4.8, 2.5, 1.4, "엔지니어링 환경", "Python 3.12", "uv (.venv) / Matplotlib / TF-IDF")

    add_notes(s1, """안녕하십니까, 여러분. 오늘 'IT/테크 베스트셀러 심층 탐색적 데이터 분석 보고서' 발표를 맡은 수석 데이터 분석가입니다.
최근 생성형 AI 기술이 급격히 발전하면서, 국내 IT 및 컴퓨터 관련 출판 시장은 그 어느 때보다 역동적인 격변기를 겪고 있습니다. 과거의 파이썬 기초나 웹 개발 중심의 출판 문법에서 벗어나, 이제는 클로드 코드, 바이브 코딩, 자율 에이전트와 같은 최첨단 패러다임이 독자들의 선택을 좌우하고 있습니다.
본 보고서는 대한민국 대표 온라인 서점인 yes24의 IT/테크 분야 베스트셀러 1,000권의 전수 데이터를 기반으로 기획되었습니다. 단순히 '어떤 책이 많이 팔렸는가'를 나열하는 일차원적 정리를 넘어, 가격 책정의 심리적 저항선, 독자 평점과 리뷰가 판매지수에 미치는 인과적 메커니즘, 주요 출판사들의 점유율 구조, 그리고 텍스트 마이닝을 통한 차세대 기술 키워드까지 20년 데이터 분석 노하우를 집약해 다각도로 분석했습니다.
오늘 발표를 통해 출판 기획자, 마케터, 그리고 저자 여러분께서 향후 성공적인 도서 기획과 최적의 비즈니스 의사결정을 내리실 수 있는 실질적인 정량 가이드라인을 전달해 드리겠습니다.""")

    # ==========================================
    # SLIDE 2: 목차 (Agenda)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, COLOR_BG_LIGHT)
    add_header(s2, "목차 (Agenda)", "프레젠테이션 개요")

    agenda_items = [
        ("Part 1. 분석 개요 및 데이터 무결성", "데이터 신뢰성 확보 및 파이프라인 구축", ["분석 배경 및 5대 핵심 목적", "데이터 수집 및 16개 변수 스키마", "데이터 무결성 5단계 종합 검증"]),
        ("Part 2. 핵심 변수 일변량 심층 분석", "단일 핵심 변수의 분포 형상 및 통계 특성", ["도서 판매가 분포 및 가격 저항선", "평점 분포 및 고득점 수렴 메커니즘", "판매지수 멱법칙(Log10) 및 출판연도 분석"]),
        ("Part 3. 범주형 & 텍스트 마이닝 분석", "출판 생태계 점검 및 텍스트 트렌드 규명", ["상위 30대 출판사 과점 구조 점검", "주요 구매 및 플랫폼 태그 30선 분석", "Scikit-learn TF-IDF 핵심 키워드 마이닝"]),
        ("Part 4. 다변량 관계 및 비즈니스 제언", "변수 간 입체적 상호작용 및 실행 전략", ["출판사별 가격-판매지수 매트릭스", "가격대별 상자그림 및 평점-리뷰 산점도", "20년차 수석 분석가의 3대 비즈니스 제언"])
    ]

    for i, (title, sub, bullets) in enumerate(agenda_items):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 5.95
        y = 1.9 + row * 2.55
        card = add_card(s2, x, y, 5.75, 2.35)
        
        # 카드 상단 라벨 바
        hbar = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x + 0.2), Inches(y + 0.2), Inches(5.35), Inches(0.4))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        hbar.line.fill.background()
        p = hbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = title
        set_font(r, FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)
        hbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s2.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.7), Inches(5.25), Inches(1.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p_sub = tf.paragraphs[0]
        r_sub = p_sub.add_run()
        r_sub.text = f"• {sub}\n"
        set_font(r_sub, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.space_before = Pt(3)
            r_b = p_b.add_run()
            r_b.text = f"  - {b}"
            set_font(r_b, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MUTED)

    add_notes(s2, """오늘 발표의 전체 목차를 간략히 짚어드리겠습니다. 본 보고서는 논리적인 데이터 흐름에 따라 총 4개의 파트로 나누어 진행됩니다.
첫 번째 파트에서는 본 분석의 문제의식과 목적, 그리고 1,000권의 데이터셋이 분석하기에 충분한 무결성을 갖추었는지를 철저히 검증하는 5단계 기초 검증 결과를 공유합니다.
두 번째 파트에서는 도서 시장의 기초 체력이라 할 수 있는 핵심 변수들, 즉 가격, 평점, 판매지수, 출판연도에 대한 일변량 분포를 짚어봅니다. 특히 판매지수가 나타내는 극단적인 멱법칙 현상을 규명합니다.
세 번째 파트에서는 범주형 데이터와 비정형 텍스트 데이터를 깊이 있게 파고듭니다. 상위 30개 출판사의 점유율과 독자 반응 태그, 그리고 형태소 분석기 없이 Scikit-learn의 TF-IDF로 추출한 핵심 기술 어휘들을 확인합니다.
마지막 네 번째 파트에서는 변수들 간의 다변량 관계를 입체적으로 조명합니다. 출판사별 가격 전략, 가격대별 판매 성과 상자그림, 평점과 리뷰수의 산점도, 그리고 최근 4개년 피봇 분석을 종합하여 수석 분석가 관점의 3대 핵심 비즈니스 액션 플랜을 제언해 드리겠습니다.""")

    # ==========================================
    # SLIDE 3: [간지 1] Part 1
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, COLOR_BG_DARK)
    
    # 대형 간지 박스
    c3 = add_card(s3, 1.2, 1.2, 10.933, 5.1, bg_color=COLOR_BG_DARK, border_color=COLOR_ACCENT)
    
    badge_s3 = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.8), Inches(2.0), Inches(0.45))
    badge_s3.fill.solid()
    badge_s3.fill.fore_color.rgb = COLOR_ACCENT
    badge_s3.line.fill.background()
    p = badge_s3.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "SECTION 01"
    set_font(r, FONT_TITLE, 13, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    tb3 = s3.shapes.add_textbox(Inches(1.8), Inches(2.5), Inches(9.5), Inches(3.2))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    r = p.add_run()
    r.text = "분석 개요 및 데이터 무결성 검증\n"
    set_font(r, FONT_TITLE, 34, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    p2 = tf3.add_paragraph()
    p2.space_before = Pt(16)
    r2 = p2.add_run()
    r2.text = "IT 출판 시장의 패러다임 변화를 추적하기 위한 데이터 수집 파이프라인 구축 및\n1,000권 베스트셀러 데이터셋의 결측치, 중복, 수치·범주형 기본 무결성 검증"
    set_font(r2, FONT_BODY, 16, bold=False, color=RGBColor(0xC5, 0xBC, 0xB2))

    add_notes(s3, """첫 번째 파트, '분석 개요 및 데이터 무결성 검증'입니다.
본격적인 통계 시각화에 들어가기에 앞서, 데이터 분석에서 가장 중요하고 선행되어야 할 작업은 바로 '데이터가 신뢰할 수 있는가'를 입증하는 것입니다. 아무리 화려한 차트와 고급 머신러닝 기법을 적용하더라도, 수집된 원천 데이터에 노이즈나 결측, 중복이 통제되지 않았다면 그 결과는 완전히 왜곡된 결론으로 이어질 수밖에 없습니다.
이번 파트에서는 본 연구가 어떠한 문제의식에서 출발했는지 5대 분석 목적을 먼저 살펴보고, 이어서 데이터 수집 파이프라인과 16개 변수의 구조를 점검합니다.
그리고 분석가가 반드시 거쳐야 할 5단계 기초 무결성 검증 과정을 통해, 최상위 도서와 하위 도서의 샘플링, 결측치 패턴의 비즈니스적 원인, 중복 검증, 그리고 수치형 및 범주형 변수의 기초 통계량을 투명하게 공유해 드리겠습니다. 이를 통해 우리가 다룰 데이터셋의 기본 신뢰성을 확고히 확인하실 수 있을 것입니다.""")

    # ==========================================
    # SLIDE 4: 분석 배경 및 5대 핵심 목적
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, COLOR_BG_LIGHT)
    add_header(s4, "분석 배경 및 5대 핵심 목적", "Part 1. 분석 개요")

    # 상단 배경 설명 카드
    add_callout(s4, 0.8, 1.85, 11.733, 1.1, "분석 배경", 
                "생성형 AI(ChatGPT, Claude, Gemini) 혁신 이후 IT/프로그래밍 출판 시장의 패러다임이 급변하고 있습니다. 단순 문법 교재의 공급 과잉 속에서 독자의 실질적 구매를 이끌어내는 정량적 성공 방정식을 규명하고자 합니다.")

    # 5대 목적 카드 가로 배치
    purposes = [
        ("01. 가격 구조 분석", "독자의 심리적 저항선 및 최적 마진 구간(Sweet Spot) 규명"),
        ("02. 독자 반응 규명", "평점 및 리뷰수가 판매지수에 미치는 인과적 메커니즘 검증"),
        ("03. 출판 생태계 점검", "대형 IT 전문 출판사의 과점 구조 및 브랜드 파워 분석"),
        ("04. 기술 키워드 마이닝", "TF-IDF를 통한 독자 니즈 및 차세대 에이전틱 코딩 파악"),
        ("05. 비즈니스 가이드라인", "차기 도서 기획, 가격 책정, 마케팅 액션 플랜 수립")
    ]
    for i, (title, desc) in enumerate(purposes):
        x = 0.8 + i * 2.38
        card = add_card(s4, x, 3.2, 2.25, 3.6, bg_color=COLOR_BG_WHITE)
        # 상단 넘버링 헤더
        num_bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(3.2), Inches(2.25), Inches(0.45))
        num_bar.fill.solid()
        num_bar.fill.fore_color.rgb = COLOR_CARD_HEADER
        num_bar.line.fill.background()
        p = num_bar.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = title.split(".")[0]
        set_font(r, FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)
        num_bar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s4.shapes.add_textbox(Inches(x + 0.15), Inches(3.8), Inches(1.95), Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = title.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = desc
        set_font(r2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_notes(s4, """본격적으로 분석 배경과 목적을 말씀드리겠습니다. 최근 몇 년간 IT 업계는 생성형 AI의 등장으로 엄청난 지각변동을 겪었습니다. 단순히 새로운 프로그래밍 언어나 프레임워크가 등장한 수준이 아니라, 개발 방식 자체가 '사람이 직접 코딩하는 시대'에서 'AI와 협업하여 코딩을 지시하는 에이전틱 바이브 코딩의 시대'로 진화했습니다.
이러한 거대한 전환기 속에서 yes24의 IT/테크 베스트셀러 순위 역시 급변하고 있습니다. 수많은 신간이 쏟아져 나오는 상황에서, 독자들의 선택을 받는 도서들에는 어떤 공통적인 데이터 패턴이 존재하는지 밝혀내는 것이 본 프로젝트의 출발점입니다.
저희는 크게 5가지 목적을 설정했습니다. 첫째, 독자들이 지갑을 여는 최적의 가격 구간과 심리적 마지노선을 찾고, 둘째, 평점과 리뷰 수가 실제 판매 성과에 어떤 기여를 하는지 상관관계를 분석하며, 셋째, 한빛미디어나 길벗 같은 대형 출판사들의 점유율 구조를 파악하고, 넷째, 도서명 텍스트에서 최신 기술 키워드를 추출하며, 마지막으로 출판 현장에서 바로 활용할 수 있는 현실적인 비즈니스 가이드라인을 도출하고자 합니다.""")

    # ==========================================
    # SLIDE 5: 데이터 수집 및 엔지니어링 파이프라인
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, COLOR_BG_LIGHT)
    add_header(s5, "데이터 수집 및 엔지니어링 파이프라인", "Part 1. 분석 개요")

    # 3단계 프로세스 카드
    steps = [
        ("STEP 1. 데이터 수집 & 스키마 정의", "yes24 IT/테크 베스트셀러 1,000권 전수 수집\n• 16개 핵심 변수 체계적 추출\n• 서지(도서명, 저자, 출판사, 발행일)\n• 가격(정가, 판매가, 할인율, 가격대)\n• 성과(평점, 리뷰수, 판매지수, 태그)"),
        ("STEP 2. 무결성 검증 & 전처리 파이프라인", "5단계 엄격한 엔지니어링 검증 완료\n• 1,000행 × 16열 고유성 100% (중복 0건)\n• 비즈니스 맥락 기반 결측치 정밀 통제\n• 무평점 신간(206건) 결측치 분리 보존\n• uv (.venv) 단일 가상환경 재현성 확보"),
        ("STEP 3. 다차원 분석 & 텍스트 마이닝", "통계 분석 및 고해상도 시각화 완성\n• Matplotlib 기반 12종 순수 차트 작성\n• koreanize-matplotlib 한글 폰트 적용\n• Scikit-learn TF-IDF 키워드 벡터화\n• images/ 및 docs/ 분리 아키텍처 준수")
    ]
    for i, (stitle, sbody) in enumerate(steps):
        x = 0.8 + i * 3.98
        card = add_card(s5, x, 1.9, 3.8, 5.0)
        # 상단 타이틀 바
        tbar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.55))
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = COLOR_ACCENT if i == 0 else (COLOR_ACCENT_DARK if i == 1 else COLOR_CARD_HEADER)
        tbar.line.fill.background()
        p = tbar.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = stitle
        set_font(r, FONT_TITLE, 13, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC) if i < 2 else COLOR_TEXT_MAIN)
        tbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s5.shapes.add_textbox(Inches(x + 0.2), Inches(2.6), Inches(3.4), Inches(4.1))
        tf = tb.text_frame
        tf.word_wrap = True
        for line in sbody.split("\n"):
            p_l = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            p_l.space_before = Pt(6) if line.startswith("•") else Pt(2)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 12, bold=not line.startswith("•"), color=COLOR_TEXT_MAIN if not line.startswith("•") else COLOR_TEXT_MUTED)

    add_notes(s5, """이번 장에서는 수집된 데이터셋의 프로파일과 기술적인 분석 환경을 설명드리겠습니다. 분석에 활용된 원천 데이터는 yes24 IT/테크 분야의 베스트셀러 상위 1,000권 전수 데이터입니다.
스키마는 총 16개의 컬럼으로 구성되어 있습니다. 도서명과 저자, 출판사 같은 기본 서지 정보부터 정가, 판매가, 할인율과 같은 가격 지표, 그리고 평점, 리뷰수, 그리고 yes24 고유의 누적 판매 지표인 '판매지수'까지 풍부한 변수들이 포함되어 있습니다.
분석 파이프라인은 높은 재현성과 안정성을 보장하기 위해 워크스페이스 공통 uv 가상환경인 .venv를 기반으로 구축되었습니다. 또한 시각화 과정에서는 Seaborn의 기본 글로벌 스타일링을 철저히 배제하고, 순수 Matplotlib을 활용하여 모든 축 라벨과 범례, 그리드를 300DPI 수준의 고해상도로 정밀하게 커스텀했습니다. 한글 폰트 깨짐을 원천 차단하기 위해 koreanize-matplotlib 라이브러리를 적용했으며, 모든 파일은 images와 docs 폴더로 철저히 분리하여 상대경로 기반으로 관리되고 있습니다.""")

    # ==========================================
    # SLIDE 6: 데이터 무결성 검증 (1) 상위 vs 하위 도서
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, COLOR_BG_LIGHT)
    add_header(s6, "데이터 무결성 검증: 상위 및 하위 도서 샘플링", "Part 1. 데이터 무결성")

    # 좌측 Top 5 카드
    c_top = add_card(s6, 0.8, 1.9, 5.75, 4.2)
    tb_top = s6.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(5.35), Inches(3.9))
    tf_top = tb_top.text_frame
    tf_top.word_wrap = True
    p = tf_top.paragraphs[0]
    r = p.add_run()
    r.text = "🏆 최상위 베스트셀러 (Top 1 ~ 5)\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    top_books = [
        ("1위. 클로드 코드 제대로 시작하기", "길벗 | 28,800원 | 평점 9.8 | 지수 42,450"),
        ("2위. 뚝딱 바로 써먹는 AI 3대장", "안경다리BOOKS | 19,800원 | 평점 9.9 | 지수 39,180"),
        ("3위. 혼공 바이브 코딩 with 클로드", "한빛미디어 | 27,000원 | 평점 9.8 | 지수 79,938"),
        ("4위. 모두를 위한 AI (챗GPT·제미나이·클로드)", "시프트 | 19,800원 | 평점 9.5 | 지수 24,354"),
        ("5위. 기술노트", "지식오름 | 29,700원 | 평점 9.4 | 지수 15,489")
    ]
    for b_title, b_sub in top_books:
        p_t = tf_top.add_paragraph()
        p_t.space_before = Pt(6)
        r_t = p_t.add_run()
        r_t.text = f"{b_title}\n"
        set_font(r_t, FONT_BODY, 12, bold=True, color=COLOR_PRIMARY)
        r_s = p_t.add_run()
        r_s.text = f"  └ {b_sub}"
        set_font(r_s, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    # 우측 하위 5권 카드
    c_bot = add_card(s6, 6.75, 1.9, 5.75, 4.2)
    tb_bot = s6.shapes.add_textbox(Inches(6.95), Inches(2.05), Inches(5.35), Inches(3.9))
    tf_bot = tb_bot.text_frame
    tf_bot.word_wrap = True
    p = tf_bot.paragraphs[0]
    r = p.add_run()
    r.text = "📉 하위 베스트셀러 (Top 996 ~ 1000)\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_TEXT_MUTED)

    bot_books = [
        ("996위. 나의 첫 코딩 수업 with 파이썬", "판매가 18,900원 | 판매지수 84"),
        ("997위. Do it! IT 네트워크 기초", "판매가 19,800원 | 판매지수 606"),
        ("998위. 파이썬 머신러닝 판다스 데이터 분석", "판매가 27,000원 | 판매지수 492"),
        ("999위. 드론 바이블", "판매가 26,820원 | 판매지수 930"),
        ("1000위. 알고리즘 이야기", "판매가 12,150원 | 판매지수 678")
    ]
    for b_title, b_sub in bot_books:
        p_t = tf_bot.add_paragraph()
        p_t.space_before = Pt(6)
        r_t = p_t.add_run()
        r_t.text = f"{b_title}\n"
        set_font(r_t, FONT_BODY, 12, bold=True, color=COLOR_TEXT_MAIN)
        r_s = p_t.add_run()
        r_s.text = f"  └ {b_sub}"
        set_font(r_s, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    # 하단 분석가 콜아웃
    add_callout(s6, 0.8, 6.25, 11.733, 0.95, "시니어 분석가 샘플링 인사이트",
                "최상위 5권 중 4권이 클로드(Claude) 및 멀티 AI 실습 도서로 최신 트렌드가 상위 매출을 전면 견인하고 있으며, 상위권과 하위권 간 판매지수 격차가 최대 1,000배에 달하는 극단적 쏠림이 초기 검증에서 확인되었습니다.")

    add_notes(s6, """데이터의 실제 행을 들여다보는 첫 번째 검증 단계로, 1위부터 5위까지의 최상위 도서와 996위부터 1,000위까지의 하위 도서를 샘플링하여 대조해 보았습니다.
이 샘플링 결과는 현 출판 시장의 트렌드를 아주 극명하게 대변하고 있습니다. 보시는 바와 같이 상위 1위부터 4위까지의 도서가 모두 '클로드 코드', 'AI 3대장', '바이브 코딩' 등 생성형 AI를 실무에 직접 활용하는 도서들로 채워져 있습니다. 특히 3위에 랭크된 한빛미디어의 '바이브 코딩' 도서는 판매지수가 무려 79,938에 달하여 최상위권의 폭발적인 수요를 입증합니다.
반면 하위권인 996위부터 1000위 도서들을 보면 기초 파이썬 코딩, 네트워크 입문서, 드론 같은 전통적 하드웨어 실습서들이 위치해 있으며, 판매지수는 두 자릿수에서 수백 점 수준에 머무르고 있습니다. 즉, 최상위권의 판매 파워가 하위권에 비해 수십 배에서 수백 배에 달하는 거대한 격차가 실존하고 있음을 첫 샘플링 단계에서부터 확인할 수 있었습니다.""")

    # ==========================================
    # SLIDE 7: 데이터 무결성 검증 (2) 결측치 및 고유성
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, COLOR_BG_LIGHT)
    add_header(s7, "데이터 무결성 검증: 결측치 및 고유성 점검", "Part 1. 데이터 무결성")

    # 상단 요약 지표 카드 3개
    add_stat_box(s7, 0.8, 1.9, 3.75, 1.3, "전체 데이터 규모", "1,000 × 16", "1,000개 행 / 16개 열")
    add_stat_box(s7, 4.79, 1.9, 3.75, 1.3, "중복 데이터 검증", "0건 (100%)", "중복 없는 완전 고유성 확보")
    add_stat_box(s7, 8.78, 1.9, 3.75, 1.3, "핵심 변수 결측치", "0건 (PASS)", "도서명, 저자, 출판사, 판매가 등")

    # 4개 결측치 비즈니스 분석 박스
    missings = [
        ("부제목 (263건 결측 / 26.3%)", "부제목이 별도로 없는 명확한 단독 브랜드 도서군으로, 서지 정보의 정상적 표현 방식입니다."),
        ("할인율 (166건 결측 / 16.6%)", "도서정가제 외 정가 100% 그대로 판매되는 대학 전공서 및 특수 학술 교재의 비할인 정책입니다."),
        ("평점 & 리뷰수 (각 206건 / 20.6%)", "최근 1~2개월 내 출간되어 아직 독자 리뷰와 평점이 누적되지 않은 극초기 신간입니다."),
        ("태그 (357건 결측 / 35.7%)", "yes24 시스템 등록 시점 마케팅 부가 태그가 부여되지 않은 일반 단행본 서적군입니다.")
    ]
    for i, (m_title, m_desc) in enumerate(missings):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 5.95
        y = 3.4 + row * 1.55
        c = add_card(s7, x, y, 5.75, 1.4)
        tb = s7.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.15), Inches(5.35), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = f"• {m_title}\n"
        set_font(r, FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        r2 = p2.add_run()
        r2.text = m_desc
        set_font(r2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s7, 0.8, 6.45, 11.733, 0.75, "전처리 원칙", 
                "무평점 신간(206건)은 평점 왜곡을 차단하기 위해 결측으로 분리 보존하고, 가격과 판매지수는 1,000건 전수를 활용합니다.")

    add_notes(s7, """다음은 결측치와 중복 데이터에 대한 정합성 검증입니다. 데이터셋 1,000개 행 전체에 대해 중복 검사를 수행한 결과, 중복 데이터는 단 한 건도 없는 0건으로 고유성 100%를 확인했습니다.
결측치의 경우, 일부 컬럼에서 결측이 관찰되었으나 이는 데이터 오류가 아닌 출판 및 도서 유통의 비즈니스적 특성에 기인한 정상적인 결측이었습니다.
예를 들어 부제목 컬럼의 263건 결측은 부제목이 아예 없는 단독 제목 서적이었고, 할인율 166건 결측은 할인이 적용되지 않고 정가로만 판매되는 학술 교재였습니다. 평점과 리뷰수의 206건 결측은 출간된 지 얼마 되지 않아 아직 독자 리뷰가 쌓이지 않은 극초기 신간들이었습니다.
가장 핵심적인 서지 지표인 도서명, 저자, 출판사, 판매가, 정가, 그리고 판매지수는 결측치가 단 1건도 없이 완전성 100%를 충족했습니다. 따라서 저희는 신간의 평점 왜곡을 방지하기 위해 무평점 도서는 통계적 결측치로 안전하게 처리한 후 분석을 진행했습니다.""")

    # ==========================================
    # SLIDE 8: 수치형 변수 종합 기술통계
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, COLOR_BG_LIGHT)
    add_header(s8, "핵심 수치형 변수 종합 기술통계", "Part 1. 데이터 기술통계")

    # 상단 4개 하이라이트 KPI 카드
    add_stat_box(s8, 0.8, 1.9, 2.75, 1.3, "평균 도서 판매가", "23,727원", "중앙값: 22,500원 (Q1: 1.89만 / Q3: 2.79만)")
    add_stat_box(s8, 3.79, 1.9, 2.75, 1.3, "평균 독자 평점", "9.60점", "중앙값: 9.80점 (표본 75%가 9.6점 이상)")
    add_stat_box(s8, 6.78, 1.9, 2.75, 1.3, "평균 판매지수", "2,865", "중앙값: 1,284 (평균이 중앙값의 2.2배)")
    add_stat_box(s8, 9.77, 1.9, 2.75, 1.3, "평균 출판연도", "2024.8년", "2025~2026년 출간작이 전체의 75.8%")

    # 하단 전체 기술통계 테이블 카드
    c_tbl = add_card(s8, 0.8, 3.4, 11.733, 2.8)
    tb_tbl = s8.shapes.add_textbox(Inches(1.0), Inches(3.55), Inches(11.333), Inches(2.5))
    tf_tbl = tb_tbl.text_frame
    tf_tbl.word_wrap = True
    
    rows_data = [
        "지표           판매가(원)   정가(원)    할인율(%)  평점(10점)  리뷰수      판매지수     출판연도",
        "─────────────────────────────────────────────────────────────────────────────────",
        "데이터 수      1,000        1,000       834        794         794         1,000        1,000",
        "평균 (Mean)    23,727       25,855      10.0%      9.60점      41.2건      2,865        2024.8년",
        "표준편차       7,772        8,334       0.4%       0.87점      89.5건      6,303        2.0년",
        "최소값 (Min)   5,625        6,250       5.0%       2.0점       1건         12           2009.0년",
        "중앙값 (50%)   22,500       25,000      10.0%      9.80점      20.0건      1,284        2026.0년",
        "최대값 (Max)   67,000       67,000      15.0%      10.0점      1,240건     79,938       2026.0년"
    ]
    for r_line in rows_data:
        p = tf_tbl.add_paragraph() if tf_tbl.paragraphs[0].text else tf_tbl.paragraphs[0]
        p.space_before = Pt(2)
        r = p.add_run()
        r.text = r_line
        set_font(r, "Consolas", 10, bold=r_line.startswith("지표") or r_line.startswith("중앙값"), color=COLOR_PRIMARY if r_line.startswith("중앙값") else COLOR_TEXT_MAIN)

    add_callout(s8, 0.8, 6.35, 11.733, 0.85, "기술통계 시사점",
                "판매가는 2만원대 초중반에 매우 안정적인 중심축을 형성하는 반면, 판매지수는 평균이 중앙값의 2.2배에 달해 소수의 초대형 히트작이 전체 지수를 견인하는 멱법칙 분포를 보입니다.")

    add_notes(s8, """이번 장은 데이터셋 내 7대 핵심 수치형 변수의 기술통계 요약표입니다. 이 표 하나만으로도 IT 도서 시장의 가격과 반응 지표의 전반적인 골격을 파악할 수 있습니다.
먼저 가격을 보시면, 판매가의 평균은 약 23,727원, 중앙값은 22,500원입니다. 1사분위수가 18,900원이고 3사분위수가 약 28,000원이므로, 시중 IT 도서의 절반 이상이 약 19,000원에서 28,000원 사이에 촘촘하게 모여 있음을 알 수 있습니다.
할인율은 법적 도서정가제의 영향으로 평균과 중앙값이 모두 정확히 10%에 고정되어 있습니다.
평점의 경우 평균 9.6점, 중앙값 9.8점으로 매우 높게 형성되어 있으며, 리뷰수는 평균 41건이지만 최대 1,240건에 달하는 초대형 스테디셀러가 존재합니다.
여기서 가장 주목하셔야 할 지표는 '판매지수'입니다. 평균은 2,865인데 중앙값은 1,284에 불과합니다. 평균이 중앙값의 2배가 넘는다는 것은, 소수의 초대형 베스트셀러가 전체 평균을 강하게 끌어올리고 있는 전형적인 양의 왜도(Right-Skewed) 분포를 의미합니다.""")

    # ==========================================
    # SLIDE 9: 범주형 변수 종합 기술통계
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, COLOR_BG_LIGHT)
    add_header(s9, "핵심 범주형 변수 종합 기술통계", "Part 1. 데이터 기술통계")

    cat_cards = [
        ("출판사 (Publisher)", "188개 고유 출판사", "1위: 한빛미디어 (153권 / 15.3%)\n2위: 길벗 (85권 / 8.5%)\n3위: 이지스퍼블리싱 (54권 / 5.4%)\n• 상위 5개사가 전체의 39.2% 과점"),
        ("저자 (Author)", "875명 고유 저자", "최다 배출: 서지영 저자 (8권 / 0.8%)\n• 단독 저자 집중도 극히 낮음\n• 소수 스타 저자 의존이 아닌\n  다품종 전문 실무진의 롱테일 구조"),
        ("출판월 (Publish Month)", "94개 고유 출판월", "최빈 출판월: 2026년 09월 (84권 / 8.4%)\n• 최신 신간 집중 출판 사이클\n• 기술 도서의 급격한 진부화에 대응하는\n  출판계의 신속한 신간 발행 기조"),
        ("가격대 구간 (Price Tier)", "6개 가격 구간", "1위: 1.5만~2만원 (285권 / 28.5%)\n2위: 2만~2.5만원 (268권 / 26.8%)\n3위: 2.5만~3만원 (215권 / 21.5%)\n• 1.5만~2.5만 구간이 전체의 55.3%")
    ]
    for i, (title, highlight, details) in enumerate(cat_cards):
        col = i % 2
        row = i // 2
        x = 0.8 + col * 5.95
        y = 1.9 + row * 2.5
        c = add_card(s9, x, y, 5.75, 2.3)
        
        hbar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(5.75), Inches(0.42))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        hbar.line.fill.background()
        p = hbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = f"  {title} — {highlight}"
        set_font(r, FONT_TITLE, 12, bold=True, color=COLOR_ACCENT_DARK)
        hbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s9.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.55), Inches(5.35), Inches(1.65))
        tf = tb.text_frame
        tf.word_wrap = True
        for line in details.split("\n"):
            p_l = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            p_l.space_before = Pt(3)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=not line.startswith("•"), color=COLOR_TEXT_MAIN)

    add_notes(s9, """수치형에 이어 범주형 변수의 기술통계 결과를 살펴보겠습니다.
출판사의 경우 총 188개의 출판사가 베스트셀러 목록에 이름을 올렸는데, 이 중 최빈 출판사는 '한빛미디어'로 무려 153권을 배출하며 단일 출판사로 15.3%의 압도적인 점유율을 기록했습니다.
반면 저자의 고유값은 875명에 달합니다. 1,000권의 도서 중 저자가 875명이라는 것은, 최다 도서를 배출한 저자(서지영 저자, 8권)조차 비중이 0.8%에 불과할 정도로 IT 출판 시장의 저자 풀은 극도로 분산된 롱테일(Long-tail) 구조임을 보여줍니다. 즉 소수의 스타 저자에게 의존하기보다는 다양한 전문 실무진이 집필하고 있습니다.
출판 시점은 최근 월에 집중되어 있으며, 가격대 구간은 1.5만원에서 2만원 구간이 285권(28.5%)으로 가장 많고, 2만~2.5만원 구간이 268권으로 그 뒤를 잇고 있어 이 두 구간이 전체의 55% 이상을 차지하는 주력 시장임을 확인했습니다.""")

    # ==========================================
    # SLIDE 10: [간지 2] Part 2
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, COLOR_BG_DARK)
    c10 = add_card(s10, 1.2, 1.2, 10.933, 5.1, bg_color=COLOR_BG_DARK, border_color=COLOR_ACCENT)
    
    badge_s10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.8), Inches(2.0), Inches(0.45))
    badge_s10.fill.solid()
    badge_s10.fill.fore_color.rgb = COLOR_ACCENT
    badge_s10.line.fill.background()
    p = badge_s10.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "SECTION 02"
    set_font(r, FONT_TITLE, 13, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    tb10 = s10.shapes.add_textbox(Inches(1.8), Inches(2.5), Inches(9.5), Inches(3.2))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    p = tf10.paragraphs[0]
    r = p.add_run()
    r.text = "핵심 변수 일변량 심층 분석\n"
    set_font(r, FONT_TITLE, 34, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    p2 = tf10.add_paragraph()
    p2.space_before = Pt(16)
    r2 = p2.add_run()
    r2.text = "도서 판매가, 평점, 판매지수, 출판연도 등 핵심 단일 변수의 통계적 분포 형상과\n독자 지불 용의선, 고평점 수렴 메커니즘, 판매지수 멱법칙의 정량적 규명"
    set_font(r2, FONT_BODY, 16, bold=False, color=RGBColor(0xC5, 0xBC, 0xB2))

    add_notes(s10, """이제 두 번째 파트인 '핵심 변수 일변량 심층 분석'으로 넘어가겠습니다.
일변량 분석은 각 변수가 가지고 있는 고유한 데이터 형태와 내재된 확률 분포를 단독으로 면밀히 관찰하는 단계입니다.
이번 파트에서는 우리가 궁금해하는 핵심 질문 4가지에 답을 제시합니다.
첫째, 독자들은 도서 가격에 대해 어느 정도의 심리적 저항선을 형성하고 있는가? 둘째, 베스트셀러 도서들의 평점은 왜 일반적인 정규분포가 아닌 극단적인 고평점에 몰려 있는가? 셋째, 베스트셀러 순위를 가르는 판매지수는 어떤 수학적 법칙을 따르는가? 넷째, 출판 연도별로 볼 때 IT 도서의 트렌드 교체 주기는 얼마나 빠르며 스테디셀러는 어떻게 생존하는가?
각 질문에 대해 시각화 차트와 이에 대응하는 통계표, 그리고 심층 해석을 차례대로 짚어드리겠습니다.""")

    # ==========================================
    # SLIDE 11: 베스트셀러 도서 판매가 분포 (차트 1)
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11, COLOR_BG_LIGHT)
    add_header(s11, "베스트셀러 도서 판매가 분포", "Part 2. 일변량 분석")

    # 좌측: 통계표 및 인포그래픽 요약
    c11_l = add_card(s11, 0.8, 1.9, 5.3, 5.1)
    tb11 = s11.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    p = tf11.paragraphs[0]
    r = p.add_run()
    r.text = "📊 도서 판매가 핵심 기술통계\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    stats11 = [
        ("데이터 수", "1,000권 (전수 결측 0건)"),
        ("평균 판매가", "23,727.1원 (표준편차: 7,772.1원)"),
        ("최소값 ~ 최대값", "5,625원 ~ 67,000원 (12배 격차)"),
        ("25% (Q1)", "18,900원"),
        ("중앙값 (50%)", "22,500원 (구매 중심축)"),
        ("75% (Q3)", "27,925원 (주력 도서 75% 커버)")
    ]
    for k, v in stats11:
        p_s = tf11.add_paragraph()
        p_s.space_before = Pt(4)
        r_k = p_s.add_run()
        r_k.text = f"• {k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MUTED)

    # 추가 관찰 포인트
    p_obs = tf11.add_paragraph()
    p_obs.space_before = Pt(12)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 핵심 관찰 포인트\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf11.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "15,000원~25,000원 구간에 전체 도서의 55.3%가 집중되어 있으며, 25,000원 초과 시 빈도가 완만하게 감소하는 우측 꼬리(Right-Skewed) 분포를 형성합니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    # 우측: 차트 이미지
    img1_path = "yes24/images/01_price_distribution.png"
    if os.path.exists(img1_path):
        s11.shapes.add_picture(img1_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s11, """보시는 슬라이드는 베스트셀러 도서 1,000권의 실제 판매가 분포를 히스토그램과 커널 밀도 추정 곡선으로 시각화한 차트입니다. 오른쪽 그래프를 보시면 20,000원과 25,000원 부근에서 아주 거대한 봉우리를 형성하고 있고, 그 이후로는 오른쪽으로 완만하게 꼬리가 길어지는 양의 왜도 형태를 뚜렷하게 보이고 있습니다.
왼쪽의 핵심 통계표를 보시면 전체 표본 1,000권의 평균 판매가는 23,727원, 표준편차는 약 7,772원입니다. 1사분위수가 18,900원, 중앙값이 22,500원, 3사분위수가 27,925원으로, 전체 도서의 75%가 28,000원 미만에 집중되어 있습니다. 최소 판매가는 5,625원인 소형 문고본부터 최대 67,000원에 달하는 고가 전문 서적까지 폭넓은 스펙트럼이 존재하지만, 시장의 중심축은 명확히 2만원대 초중반에 형성되어 있음을 직관적으로 확인하실 수 있습니다.""")

    # ==========================================
    # SLIDE 12: 판매가 분포 심층 분석 및 가격 심리선
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12, COLOR_BG_LIGHT)
    add_header(s12, "도서 판매가 분포 심층 분석 및 가격 심리선", "Part 2. 가격 정책 분석")

    price_cards = [
        ("01. 우측 꼬리가 긴 분포 (Right-Skewed)", "대중적 실용서의 전형적 가격 구조", 
         "• 15,000원 ~ 25,000원 구간에 전체 도서의 55% 이상이 집중 밀집\n• 중앙값 22,500원을 정점으로 좌우 대칭이 아닌 고가 영역으로 길게 늘어짐\n• 일반 독자층의 일상적 도서 구매 지출 한도가 2만원대 초반에 고정됨"),
        ("02. 심리적 저항선: 25,000원의 벽", "출판 기획 시 반드시 통제할 임계 가격", 
         "• 25,000원을 초과하여 30,000원대로 진입할 때 도서 출현 빈도가 절반 이하로 급감\n• 단순 입문서나 교양서는 25,000원 초과 책정 시 판매량 급락 위험\n• 2만원대 후반 가격 책정 시 분량과 실습 프로젝트의 압도적 품질 보증 필수"),
        ("03. 50,000원 이상 고가 전문서 시장", "가격 비탄력적 틈새 시장의 존재", 
         "• 5만원 이상 서적은 총 6권(0.6%)으로 소수이나 안정적 베스트셀러 순위 수성\n• 클라우드 아키텍처, 엔터프라이즈 시스템 구축, 기술 자격증 수험서 영역\n• 타깃 독자의 지불 용의가 명확한 전문 도서의 높은 마진율 입증")
    ]
    for i, (ptitle, psub, pdesc) in enumerate(price_cards):
        x = 0.8 + i * 3.98
        c = add_card(s12, x, 1.9, 3.8, 4.3)
        pbar = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        pbar.fill.solid()
        pbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        pbar.line.fill.background()
        p = pbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = ptitle.split(".")[0] + " " + psub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        pbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s12.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = ptitle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in pdesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s12, 0.8, 6.35, 11.733, 0.85, "20년차 분석가 결론",
                "판매가 분포는 1.5만~2.5만원 구간에 과반 이상이 밀집되어 일반 독자의 심리적 저항선이 2만원대 초중반에 위치함을 명확히 보여줍니다. 신규 도서 기획 시 타깃 독자층의 가격 민감도에 맞춘 차별화된 프라이싱 전략이 필수적입니다.")

    add_notes(s12, """앞서 보신 판매가 분포 그래프에 대한 심층 비즈니스 해석입니다.
분석 결과, 독자들의 도서 구매 심리선은 매우 뚜렷하게 나뉘고 있었습니다. 전체 도서의 55% 이상이 15,000원에서 25,000원 사이에 빽빽하게 밀집되어 있습니다. 이는 독자들이 일반적인 IT 실용서나 입문서를 구매할 때 기대하는 가격대가 바로 이 2만원 안팎이라는 점을 의미합니다.
특히 25,000원을 넘어 30,000원대로 진입하게 되면 도서의 출현 빈도가 절반 이하로 급감합니다. 독자들의 1차 심리적 저항선이 25,000원 선에 형성되어 있는 것입니다.
하지만 50,000원 이상의 초고가 영역을 보면 도서 수는 6권에 불과하지만 이들 역시 베스트셀러 순위를 당당히 유지하고 있습니다. 이는 전문 클라우드 아키텍처나 기술 자격증 수험서의 경우, 독자들이 가격에 구애받지 않고 콘텐츠의 전문성만 있다면 기꺼이 높은 비용을 지불한다는 '가격 비탄력적 틈새 시장'이 존재함을 증명합니다.""")

    # ==========================================
    # SLIDE 13: 베스트셀러 도서 평점 분포 (차트 2)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    add_bg(s13, COLOR_BG_LIGHT)
    add_header(s13, "베스트셀러 도서 평점 분포", "Part 2. 일변량 분석")

    c13_l = add_card(s13, 0.8, 1.9, 5.3, 5.1)
    tb13 = s13.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf13 = tb13.text_frame
    tf13.word_wrap = True
    p = tf13.paragraphs[0]
    r = p.add_run()
    r.text = "⭐ 독자 평점 핵심 기술통계\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    stats13 = [
        ("유효 표본 수", "794권 (신간 206건 분리 보존)"),
        ("평균 평점", "9.60점 (10점 만점 기준)"),
        ("표준편차", "0.87점 (극히 좁은 산포도)"),
        ("1사분위 (25%)", "9.60점 (하위 25% 도서조차 9.6점)"),
        ("중앙값 (50%)", "9.80점 (과반 도서가 9.8점 이상)"),
        ("만점 도서 비중", "30% 이상 (10.0점 집중)")
    ]
    for k, v in stats13:
        p_s = tf13.add_paragraph()
        p_s.space_before = Pt(4)
        r_k = p_s.add_run()
        r_k.text = f"• {k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf13.add_paragraph()
    p_obs.space_before = Pt(12)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 핵심 관찰 포인트\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf13.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "정규분포와는 정반대로 9.5~10.0점 구간에 데이터가 폭포수처럼 쏟아지는 극단적인 좌측 왜도(Left-Skewed)를 보이며, 베스트셀러 진입 도서들의 압도적 품질 보증 효과를 입증합니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img2_path = "yes24/images/02_rating_distribution.png"
    if os.path.exists(img2_path):
        s13.shapes.add_picture(img2_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s13, """다음은 베스트셀러 도서들의 평점 분포 차트입니다. 오른쪽 그래프를 보시면 일반적인 정규분포와는 정반대로, 9.5점에서 10.0점 구간에 데이터가 폭포수처럼 쏟아져 있는 극단적인 좌측 왜도를 나타냅니다.
왼쪽 표를 보시면 평균 평점이 무려 9.60점이며, 중앙값은 9.8점입니다. 심지어 1사분위수인 하위 25% 지점의 평점조차 9.6점입니다. 즉 베스트셀러 목록에 든 책 4권 중 3권은 평점이 9.6점 이상이라는 뜻입니다. 최소 평점이 2.0점인 도서도 극소수 존재하지만, 표준편차가 0.87로 극히 작아 대다수 도서가 9점대 후반에 빽빽하게 몰려 있음을 알 수 있습니다.""")

    # ==========================================
    # SLIDE 14: 평점 심층 분석 및 고득점 수렴 메커니즘
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    add_bg(s14, COLOR_BG_LIGHT)
    add_header(s14, "평점 심층 분석 및 고득점 수렴 메커니즘", "Part 2. 독자 반응 분석")

    rating_cards = [
        ("01. 출판 품질 사전 검증 필터", "출간 전 철저한 베타리딩 효과",
         "• 베스트셀러 1,000위권 진입 도서는 출판사의 엄격한 코드 검증 및 베타테스트 완비\n• 초보자 실습 시 오류 발생률이 통제된 고품질 서적만이 순위권에 진입\n• 기본 콘텐츠 충실도가 9점 이상의 고평점을 지탱하는 1차 방어선"),
        ("02. 초기 팬덤의 선순환 효과", "얼리어답터 독자의 우호적 평가",
         "• 출간 직후 책을 구매하는 충성 독자층이 초기에 자발적으로 10점 만점 부여\n• 높은 초기 평점이 탐색 중인 일반 독자들의 구매 전환율을 견인\n• 판매량 증가와 긍정 리뷰 누적이 결합되는 강력한 마케팅 선순환 유도"),
        ("03. 평점 인플레이션과 생존 조건", "9.5점 미만 도서의 신속한 도태",
         "• 평점이 9.0점 미만으로 하락할 경우 온라인 전환율이 급감하여 순위권 밖으로 밀려남\n• 9.5점이라는 점수는 탁월함의 지표가 아니라 생존을 위한 필수 '기본 자격'\n• 독자들은 이제 9.5점 이상 평점 도서만을 선별적으로 검토하여 구매")
    ]
    for i, (rtitle, rsub, rdesc) in enumerate(rating_cards):
        x = 0.8 + i * 3.98
        c = add_card(s14, x, 1.9, 3.8, 4.3)
        rbar = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        rbar.fill.solid()
        rbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        rbar.line.fill.background()
        p = rbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = rtitle.split(".")[0] + " " + rsub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        rbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s14.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = rtitle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in rdesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s14, 0.8, 6.35, 11.733, 0.85, "분석가 인사이트",
                "베스트셀러 도서의 평균 9.6점 형성은 품질 검증 효과와 함께 초기 충성 독자의 긍정 평가가 판매 선순환을 만든 결과입니다. 따라서 출간 초기 9.5점 이상의 평점 방어가 도서 롱런의 핵심 선결 과제입니다.")

    add_notes(s14, """이 평점 분포의 배후에 숨겨진 비즈니스 메커니즘을 해석해 드리겠습니다.
왜 이렇게 평점이 높을까요? 첫 번째 원인은 '베스트셀러 후광 효과'와 '품질 검증'입니다. 1,000위 안에 드는 도서들은 이미 출판사의 꼼꼼한 베타리딩과 편집 과정을 거쳐 검증된 콘텐츠입니다. 또한 출간 초기에 책을 가장 먼저 구매하는 독자들은 해당 저자나 주제에 깊은 애정을 가진 팬덤층일 확률이 높아 초기 평가가 우호적으로 형성됩니다.
두 번째는 '평점 인플레이션'의 필터링 효과입니다. 평점이 9점 미만으로 떨어지는 도서는 독자들의 구매 전환율이 급락하면서 베스트셀러 순위권 밖으로 빠르게 밀려납니다. 즉, 베스트셀러 목록에 살아남아 있다는 사실 자체가 이미 평점 9.5점 이상을 유지하고 있다는 방증입니다.
따라서 출판 마케팅 관점에서 볼 때 9.5점이라는 점수는 특별한 우수함이 아니라, 시장에서 살아남기 위한 '필수 기본값'으로 작용하고 있습니다.""")

    # ==========================================
    # SLIDE 15: 판매지수 Log10 스케일 분포 (차트 3)
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    add_bg(s15, COLOR_BG_LIGHT)
    add_header(s15, "베스트셀러 판매지수 Log10 스케일 분포", "Part 2. 일변량 분석")

    c15_l = add_card(s15, 0.8, 1.9, 5.3, 5.1)
    tb15 = s15.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf15 = tb15.text_frame
    tf15.word_wrap = True
    p = tf15.paragraphs[0]
    r = p.add_run()
    r.text = "📈 원본 vs Log10 변환 통계표\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    stats15 = [
        ("최소값 (Min)", "12 → Log 1.079 (하위 롱테일)"),
        ("25% (Q1)", "540 → Log 2.732"),
        ("중앙값 (50%)", "1,284 → Log 3.109 (대칭축 중심)"),
        ("평균 (Mean)", "2,865 → Log 3.089 (정규분포 일치)"),
        ("75% (Q3)", "2,723 → Log 3.435"),
        ("최대값 (Max)", "79,938 → Log 4.903 (메가 히트작)")
    ]
    for k, v in stats15:
        p_s = tf15.add_paragraph()
        p_s.space_before = Pt(4)
        r_k = p_s.add_run()
        r_k.text = f"• {k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf15.add_paragraph()
    p_obs.space_before = Pt(12)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 수학적 모델링 인사이트\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf15.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "원본 상태에서 6,661배에 달했던 극단적 왜도가 Log10 변환 시 완벽한 종형 곡선으로 변환되어, 향후 판매량 예측 회귀 모델 구축 시 로그 스케일 적용이 필수적임을 입증합니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img3_path = "yes24/images/03_sales_index_distribution.png"
    if os.path.exists(img3_path):
        s15.shapes.add_picture(img3_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s15, """이번 차트는 본 분석에서 통계학적으로 가장 흥미로운 발견 중 하나인 '판매지수 Log10 분포'입니다.
오른쪽 그래프를 보시면 원본 상태에서는 왜도가 극심했던 데이터가, 상용로그(Log10) 변환을 적용하자 완벽한 정규분포 종형 곡선으로 탈바꿈한 것을 보실 수 있습니다.
왼쪽 표를 보시면 원본 상태에서는 평균(2,865)과 중앙값(1,284)이 2배 넘게 차이가 났지만, 로그 변환 후에는 평균 3.089와 중앙값 3.109로 소수점 둘째 자리까지 거의 완벽하게 일치합니다. 이는 출판 시장의 도서 판매량이 멱급수 및 로그 정규분포를 철저히 따르고 있음을 통계적으로 입증한 것입니다.""")

    # ==========================================
    # SLIDE 16: 판매지수 멱법칙 및 파레토 법칙 해석
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    add_bg(s16, COLOR_BG_LIGHT)
    add_header(s16, "판매지수 멱법칙(Power Law) 및 파레토 법칙 해석", "Part 2. 판매 성과 분석")

    power_cards = [
        ("01. 멱법칙(Power Law)의 실증", "극단적인 승자 독식 시장 구조",
         "• 최소 12부터 최대 79,938까지 무려 6,661배의 거대한 판매지수 격차 실존\n• 베스트셀러 순위표 내에서도 상위 1% 도서의 독점력이 압도적임\n• 일반 선형 모델이 아닌 거듭제곱 법칙이 출판 시장을 지배함을 확인"),
        ("02. 파레토 법칙 (80:20 Rule)", "상위 5%가 전체 매출 볼륨 견인",
         "• 상위 5%에 불과한 단 50권의 메가 히트작이 전체 1,000권 합산 지수의 35% 장악\n• 소수의 텐트폴 도서가 온라인 서점 및 출판사의 전체 매출을 강력 견인\n• 베스트셀러 순위 진입을 넘어 상위 50위권 안착이 비즈니스 성패의 핵심 분수령"),
        ("03. 출판사 텐트폴 포트폴리오 전략", "안정적 롱테일과 메가 히트작의 결합",
         "• 지수 1,000 내외의 다수 롱테일 실용서로 회사의 고정비와 손익분기점 방어\n• 연 1~2권 출간되는 초대형 킬러 콘텐츠로 영업이익을 폭발시키는 구조\n• 단일 베스트셀러 의존 위험을 분산하는 다각화된 출판 기획 포트폴리오 필수")
    ]
    for i, (pwtitle, pwsub, pwdesc) in enumerate(power_cards):
        x = 0.8 + i * 3.98
        c = add_card(s16, x, 1.9, 3.8, 4.3)
        pwbar = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        pwbar.fill.solid()
        pwbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        pwbar.line.fill.background()
        p = pwbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = pwtitle.split(".")[0] + " " + pwsub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        pwbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s16.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = pwtitle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in pwdesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s16, 0.8, 6.35, 11.733, 0.85, "전략적 시사점",
                "출판 시장은 전형적인 파레토 멱법칙이 작동하는 슈퍼스타 시장입니다. 다수의 안정적인 스테디 교재로 손익분기점을 방어하고 최신 AI 텐트폴 도서로 이익을 극대화하는 포트폴리오 관리가 요구됩니다.")

    add_notes(s16, """이 멱법칙(Power Law) 결과가 출판 비즈니스에 던지는 시사점은 매우 심오합니다.
출판 시장은 전형적인 '승자 독식' 혹은 '슈퍼스타 시장'입니다. 상위 5%에 해당하는 단 50권의 메가 히트 도서가 전체 1,000권 합산 판매지수의 35% 이상을 혼자서 견인하고 있습니다.
이러한 파레토 법칙 구조는 출판사들의 포트폴리오 전략에 결정적인 교훈을 줍니다. 출판사는 매년 수십 권의 책을 출간하지만, 모든 책이 베스트셀러가 될 수는 없습니다. 지수 1,000 안팎의 안정적인 롱테일 도서들로 회사의 고정비와 손익분기점을 방어하고, 1년에 1~2권씩 터져 나오는 초대형 텐트폴(Tentpole) 도서로 전체 영업이익을 폭발시키는 포트폴리오 모델이 작동하고 있는 것입니다.
향후 데이터 기반 판매량 예측이나 출판 성과 분석 모델을 구축할 때도, 원본 지수가 아닌 반드시 로그 변환된 지표를 종속변수로 활용해야 모델의 왜곡을 방지할 수 있습니다.""")

    # ==========================================
    # SLIDE 17: 출판연도별 베스트셀러 점유 현황 (차트 4)
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    add_bg(s17, COLOR_BG_LIGHT)
    add_header(s17, "출판연도별 베스트셀러 점유 현황", "Part 2. 일변량 분석")

    c17_l = add_card(s17, 0.8, 1.9, 5.3, 5.1)
    tb17 = s17.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf17 = tb17.text_frame
    tf17.word_wrap = True
    p = tf17.paragraphs[0]
    r = p.add_run()
    r.text = "📅 연도별 점유율 현황표\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    stats17 = [
        ("2026년 출간", "505권 (50.91%) | 에이전틱 코딩, Claude"),
        ("2025년 출간", "247권 (24.90%) | 생성형 AI 실무 적용"),
        ("2024년 출간", "113권 (11.39%) | 프롬프트 엔지니어링"),
        ("2023년 출간", "45권 (4.54%) | ChatGPT 초기 기본서"),
        ("2021~2022년", "53권 (5.35%) | 파이썬 기본 문법"),
        ("2020년 이전", "37권 (3.00%) | 네트워크/CS 불멸 스테디")
    ]
    for k, v in stats17:
        p_s = tf17.add_paragraph()
        p_s.space_before = Pt(4)
        r_k = p_s.add_run()
        r_k.text = f"• {k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf17.add_paragraph()
    p_obs.space_before = Pt(12)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 신간 쏠림 구조\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf17.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "최근 2개년(2025~2026년) 신간이 전체의 75.8%를 장악하여 IT 도서의 수명이 1년 안팎으로 극도로 단축되었음을 보여줍니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img4_path = "yes24/images/04_year_distribution.png"
    if os.path.exists(img4_path):
        s17.shapes.add_picture(img4_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s17, """이번 차트는 베스트셀러 1,000권의 출판 연도별 점유 현황을 분석한 막대그래프입니다.
오른쪽 그래프를 보시면 데이터가 최근 1~2년으로 극단적으로 쏠려 있는 것을 한눈에 확인하실 수 있습니다. 왼쪽 표에 정리된 것처럼 2026년에 출간된 도서가 505권으로 전체의 절반이 넘는 50.9%를 차지하고 있으며, 2025년 출간 도서 247권을 합치면 최근 2개년 출간 도서의 비중이 무려 75.8%에 달합니다. 4권 중 3권이 최신 신간인 셈입니다.
하지만 그래프의 가장 왼쪽, 2020년 이전 영역을 보시면 2009년 출간작을 포함하여 총 37권의 도서가 여전히 베스트셀러 순위표를 굳건히 지키고 있습니다. 이 양극화된 시간 분포가 무엇을 의미하는지 다음 장에서 자세히 살펴보겠습니다.""")

    # ==========================================
    # SLIDE 18: IT 도서의 빠른 트렌드 교체 주기와 스테디셀러
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    add_bg(s18, COLOR_BG_LIGHT)
    add_header(s18, "IT 도서의 빠른 트렌드 교체 주기와 스테디셀러의 가치", "Part 2. 콘텐츠 수명주기")

    life_cards = [
        ("01. 빠른 진부화 주기 (75.8%)", "신간 중심의 초단기 라이프사이클",
         "• AI/소프트웨어 프레임워크의 업데이트 주기가 6개월~1년 단위로 단축\n• 2년 전 출간된 도서는 이미 구버전 문법으로 간주되어 독자 외면\n• 출판 기획팀의 신속한 개정판 및 신규 AI 도서 기획 파이프라인 필수"),
        ("02. 고전 스테디셀러의 불멸성 (3%)", "컴퓨터 과학 기초 원리의 영속성",
         "• 2020년 이전(심지어 2009년 출간작) 37권이 5~10년 이상 베스트셀러 유지\n• 자료구조, 네트워크, 컴퓨터 아키텍처, 객체지향, 클린코드 등 기초 불변의 지식\n• 감가상각 없이 10년 이상 지속적인 현금흐름을 창출하는 황금 자산"),
        ("03. 듀얼 트랙(Dual-Track) 출판 전략", "단기 폭발력과 장기 안정성의 조화",
         "• 트랙 A (신간): Claude, Vibe 코딩 등 최신 트렌드로 단기 매출 극대화\n• 트랙 B (고전): CS 기초 전공서 및 표준 입문서로 영구적 캐시카우 확보\n• 시장 변동성에 흔들리지 않는 균형 잡힌 출판 포트폴리오 완성")
    ]
    for i, (ltitle, lsub, ldesc) in enumerate(life_cards):
        x = 0.8 + i * 3.98
        c = add_card(s18, x, 1.9, 3.8, 4.3)
        lbar = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        lbar.fill.solid()
        lbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        lbar.line.fill.background()
        p = lbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = ltitle.split(".")[0] + " " + lsub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        lbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s18.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = ltitle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in ldesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s18, 0.8, 6.35, 11.733, 0.85, "수석 분석가 제언",
                "IT 출판 생태계는 극도로 빠른 신간 쏠림과 고전 스테디셀러의 영속성이 공존합니다. 출판사는 트렌드 신간과 기초 원리서라는 양날의 검을 모두 쥐는 듀얼 트랙 기획을 확립해야 합니다.")

    add_notes(s18, """출판 연도 분석은 IT 도서 생태계의 두 가지 상반된 생존 법칙을 보여줍니다.
첫 번째는 '극도로 빠른 진부화 주기'입니다. 인공지능과 클라우드 도서는 버전 업데이트와 새로운 툴의 등장 주기가 6개월에서 1년에 불과합니다. 2년 전 책은 이미 낡은 기술이 되어 독자의 외면을 받기 때문에, 출판사는 시장의 최신 요구를 기민하게 포착하여 신속하게 개정판이나 신간을 출시해야만 합니다.
두 번째는 정반대에 위치한 '고전 스테디셀러의 영속성'입니다. 5년, 심지어 10년이 넘은 도서들이 아직도 베스트셀러에 머무는 이유는 무엇일까요? 바로 자료구조, 컴퓨터 구조, 네트워크 기초, 리팩터링, 객체지향 설계와 같은 컴퓨터 과학의 '기초 원리'는 유행을 타지 않기 때문입니다.
따라서 출판사는 '트렌드 신간을 통한 단기 매출 폭발'과 '기초 원리 교재를 통한 10년 캐시카우 구축'이라는 투 트랙(Dual-track) 전략을 반드시 병행해야 지속 가능한 성장을 달성할 수 있습니다.""")

    # ==========================================
    # SLIDE 19: [간지 3] Part 3
    # ==========================================
    s19 = prs.slides.add_slide(blank_layout)
    add_bg(s19, COLOR_BG_DARK)
    c19 = add_card(s19, 1.2, 1.2, 10.933, 5.1, bg_color=COLOR_BG_DARK, border_color=COLOR_ACCENT)
    
    badge_s19 = s19.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.8), Inches(2.0), Inches(0.45))
    badge_s19.fill.solid()
    badge_s19.fill.fore_color.rgb = COLOR_ACCENT
    badge_s19.line.fill.background()
    p = badge_s19.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "SECTION 03"
    set_font(r, FONT_TITLE, 13, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    tb19 = s19.shapes.add_textbox(Inches(1.8), Inches(2.5), Inches(9.5), Inches(3.2))
    tf19 = tb19.text_frame
    tf19.word_wrap = True
    p = tf19.paragraphs[0]
    r = p.add_run()
    r.text = "범주형 & 텍스트 마이닝 분석\n"
    set_font(r, FONT_TITLE, 34, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    p2 = tf19.add_paragraph()
    p2.space_before = Pt(16)
    r2 = p2.add_run()
    r2.text = "출판사별 베스트셀러 과점 구조와 독자들의 실용적 부가 구매 태그 패턴 규명,\nScikit-learn TF-IDF 벡터라이저를 통한 상위 30대 핵심 도서 키워드 추출"
    set_font(r2, FONT_BODY, 16, bold=False, color=RGBColor(0xC5, 0xBC, 0xB2))

    add_notes(s19, """세 번째 파트인 '범주형 및 텍스트 마이닝 분석'을 시작하겠습니다.
지금까지 숫자로 된 수치형 변수들을 살펴보았다면, 이제는 텍스트와 레이블 데이터 속에 숨겨진 정성적 맥락과 시장의 목소리를 분석할 차례입니다.
이 파트에서는 크게 3가지 차원을 조명합니다.
첫째, 188개 출판사 중 시장을 실질적으로 지배하고 있는 상위 30개 출판사의 랭킹과 과점 구조를 파악합니다.
둘째, 독자들의 구매를 촉진하는 핵심 태그(#청년패스, #분철 등)의 출현 빈도를 통해 온·오프라인 소비 행태의 결합 방식을 분석합니다.
셋째, 형태소 분석기의 인위적 오류를 배제하고 Scikit-learn의 순수 TF-IDF 알고리즘을 활용하여 1,000권의 도서명과 부제목에서 추출한 상위 30개 핵심 기술 키워드를 시각화하고, 왜 독자들이 지금 '에이전트'와 '자동화'에 열광하는지 규명하겠습니다.""")

    # ==========================================
    # SLIDE 20: 출판사별 베스트셀러 빈도 Top 30 (차트 5)
    # ==========================================
    s20 = prs.slides.add_slide(blank_layout)
    add_bg(s20, COLOR_BG_LIGHT)
    add_header(s20, "출판사별 베스트셀러 배출 빈도 Top 30", "Part 3. 범주형 분석")

    c20_l = add_card(s20, 0.8, 1.9, 5.3, 5.1)
    tb20 = s20.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf20 = tb20.text_frame
    tf20.word_wrap = True
    p = tf20.paragraphs[0]
    r = p.add_run()
    r.text = "🏢 상위 10대 출판사 점유율표\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    pubs20 = [
        ("1위. 한빛미디어", "153권 (15.3%) | 압도적 1위"),
        ("2위. 길벗", "85권 (8.5%) | 실무 AI 도서 강세"),
        ("3위. 이지스퍼블리싱", "54권 (5.4%) | 'Do it!' 시리즈 파워"),
        ("4위. 골든래빗", "50권 (5.0%) | 전문 개발서 약진"),
        ("5위. 제이펍", "50권 (5.0%) | 번역 전문서 강세"),
        ("6위. 한빛아카데미", "38권 (3.8%) | 대학 전공 교재"),
        ("7위. 위키북스", "30권 (3.0%) | 오픈소스/데이터"),
        ("8위. 앤써북", "29권 (2.9%) | 실용 코딩 가성비")
    ]
    for k, v in pubs20:
        p_s = tf20.add_paragraph()
        p_s.space_before = Pt(3)
        r_k = p_s.add_run()
        r_k.text = f"{k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf20.add_paragraph()
    p_obs.space_before = Pt(8)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 시장 과점 구조\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf20.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "상위 5개 출판사(한빛, 길벗, 이지스, 골든래빗, 제이펍)가 전체의 39.2%를 과점하고 있으며, 상위 10개사가 전체의 과반(54.4%)을 장악하고 있습니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img5_path = "yes24/images/05_top30_publishers.png"
    if os.path.exists(img5_path):
        s20.shapes.add_picture(img5_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s20, """베스트셀러를 가장 많이 배출한 상위 30개 출판사의 빈도 차트입니다.
오른쪽 그래프와 왼쪽 표를 함께 보시면, 1위는 153권을 기록한 한빛미디어입니다. 전체 1,000권 중 15.3%라는 압도적인 점유율로 시장을 주도하고 있습니다.
2위는 길벗으로 85권(8.5%), 3위는 이지스퍼블리싱으로 54권(5.4%), 4위와 5위는 골든래빗과 제이펍이 각각 50권(5.0%)으로 뒤를 잇고 있습니다.
상위 5개 출판사의 도서 수를 합치면 392권으로, 전체 베스트셀러의 약 40%를 단 5개 출판사가 점유하고 있는 명확한 과점 체제가 형성되어 있습니다. 그 아래로 한빛아카데미, 위키북스, 앤써북 등이 20~30권대의 견고한 허리 라인을 구성하고 있습니다.""")

    # ==========================================
    # SLIDE 21: 대형 IT 출판사 과점 구조 및 브랜드 신뢰
    # ==========================================
    s21 = prs.slides.add_slide(blank_layout)
    add_bg(s21, COLOR_BG_LIGHT)
    add_header(s21, "대형 IT 출판사 과점 구조 및 브랜드 신뢰 효과", "Part 3. 출판 생태계")

    pub_insights = [
        ("01. 출판 브랜드의 신뢰 보증 기제", "코드 오류 리스크와 매몰 비용 회피",
         "• IT 도서는 코드 오류나 설명 부실 시 독자가 겪는 학습 비용과 좌절감이 심각\n• 독자들은 저자 개인의 명성보다 '믿고 사는 출판사 브랜드'를 안전판으로 선택\n• 대형 출판사의 품질 검증 시스템이 강력한 구매 전환 트리거로 작동"),
        ("02. 검증된 시리즈 브랜드 라인업", "시리즈 팬덤의 지속적 구매 연계",
         "• 한빛미디어의 '혼자 공부하는' 시리즈, 길벗의 '코딩 자율학습', 이지스의 'Do it!'\n• 하나의 성공적인 시리즈 브랜딩이 후속 신간의 마케팅 비용을 획기적으로 절감\n• 초보자부터 중급자까지 이어지는 체계적 커리큘럼 락인(Lock-in) 효과"),
        ("03. 신흥 전문 출판사의 기동성", "골든래빗, 제이펍, 위키북스의 약진",
         "• 골든래빗(50권), 제이펍(50권) 등 IT 전문 출판사들이 빠른 기획력으로 상위권 안착\n• 최신 LLM 아키텍처, 딥러닝 실무 등 고난도 기술 도서를 신속하게 번역/기획\n• 대형 출판사와 전문 출판사 간의 건전한 양강 구도 형성")
    ]
    for i, (pititle, pisub, pidesc) in enumerate(pub_insights):
        x = 0.8 + i * 3.98
        c = add_card(s21, x, 1.9, 3.8, 4.3)
        pibar = s21.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        pibar.fill.solid()
        pibar.fill.fore_color.rgb = COLOR_CARD_HEADER
        pibar.line.fill.background()
        p = pibar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = pititle.split(".")[0] + " " + pisub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        pibar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s21.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = pititle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in pidesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s21, 0.8, 6.35, 11.733, 0.85, "비즈니스 결론",
                "IT 출판 시장은 브랜드 신뢰가 구매 결정의 50% 이상을 좌우합니다. 신규 출판사나 저자는 독자적인 단행본보다 강력한 시리즈 브랜드를 기획하거나 신뢰도 높은 기존 출판 브랜드와 협업하는 것이 유리합니다.")

    add_notes(s21, """출판사 점유율이 시사하는 바는 바로 '출판 브랜드가 제공하는 신뢰 보증 기제'입니다.
소설이나 에세이 같은 일반 단행본은 저자의 인지도나 스토리가 구매의 절대적인 기준이 되지만, IT 기술 도서는 구매 메커니즘이 사뭇 다릅니다. IT 도서는 책에 오탈자가 있거나 예제 코드가 실행되지 않을 경우 독자가 겪는 시간적 매몰 비용과 고통이 엄청납니다.
따라서 독자들은 '믿고 살 수 있는 출판사 브랜드', 예를 들어 한빛미디어의 '혼자 공부하는' 시리즈나 길벗의 '코딩 자율학습', 이지스퍼블리싱의 'Do it!'과 같은 검증된 시리즈 라인업을 우선적으로 선택하게 됩니다.
결국 대형 IT 출판사들은 수년간 구축해 온 탄탄한 베타리더 시스템, 코드 검증 프로세스, 그리고 대형 서점 마케팅 역량을 진입 장벽으로 삼아 강력한 시장 지배력을 유지하고 있음을 확인할 수 있습니다.""")

    # ==========================================
    # SLIDE 22: 베스트셀러 주요 태그 빈도 분포 (차트 6)
    # ==========================================
    s22 = prs.slides.add_slide(blank_layout)
    add_bg(s22, COLOR_BG_LIGHT)
    add_header(s22, "베스트셀러 주요 태그 빈도 분포", "Part 3. 범주형 분석")

    c22_l = add_card(s22, 0.8, 1.9, 5.3, 5.1)
    tb22 = s22.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf22 = tb22.text_frame
    tf22.word_wrap = True
    p = tf22.paragraphs[0]
    r = p.add_run()
    r.text = "🏷️ 주요 태그 상위 빈도 순위표\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    tags22 = [
        ("1위. #청년패스", "488회 (43.1%) | 청년 문화비 지원 정책"),
        ("2위. #분철", "147회 (13.0%) | 180도 스프링 제본 선호"),
        ("3위. #크레마클럽에있어요", "129회 (11.4%) | 전자책 구독 탐색 연계"),
        ("4위. #인공지능", "14회 (1.2%) | AI 총괄 키워드"),
        ("5위. #AI", "12회 (1.1%) | 영문 AI 키워드"),
        ("6위. #파이썬", "11회 (1.0%) | 유일한 상위권 언어"),
        ("7위. #컴퓨터공학과", "11회 (1.0%) | 전공 필수 도서"),
        ("8위. #일잘러업무스킬", "10회 (0.9%) | 직장인 실무 생산성")
    ]
    for k, v in tags22:
        p_s = tf22.add_paragraph()
        p_s.space_before = Pt(3)
        r_k = p_s.add_run()
        r_k.text = f"{k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf22.add_paragraph()
    p_obs.space_before = Pt(8)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 구매 행태의 실용성\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf22.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "상위 1~3위 태그가 모두 플랫폼 혜택 및 제본 옵션(#청년패스, #분철, #크레마클럽)으로 전체의 67.5%를 장악하여, 독자들의 극히 실용적인 구매 패턴을 반영합니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img6_path = "yes24/images/06_top30_tags.png"
    if os.path.exists(img6_path):
        s22.shapes.add_picture(img6_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s22, """이번 차트는 yes24 상세 페이지에 등록된 도서 태그의 상위 30개 빈도 분포입니다.
오른쪽 그래프를 보시면 1위부터 3위까지의 태그가 기술 이름이 아니라 유통 및 구매 옵션 태그라는 점이 명확히 드러납니다.
왼쪽 표를 보시면 1위는 `#청년패스`로 무려 488회(43.1%) 출현했고, 2위는 스프링 제본 옵션인 `#분철`로 147회(13.0%), 3위는 전자책 구독 서비스인 `#크레마클럽에있어요`가 129회(11.4%)를 기록했습니다. 이 세 가지 옵션 태그가 전체 태그 점유율의 67% 이상을 차지하고 있습니다. 그 뒤를 이어 기술 영역에서는 `#인공지능`, `#AI`, `#파이썬`, `#일잘러업무스킬` 순으로 나타납니다.""")

    # ==========================================
    # SLIDE 23: 도서 구매 옵션 혜택과 생성형 AI의 결합
    # ==========================================
    s23 = prs.slides.add_slide(blank_layout)
    add_bg(s23, COLOR_BG_LIGHT)
    add_header(s23, "도서 구매 옵션 혜택과 생성형 AI 관심사의 결합", "Part 3. 독자 소비 행동")

    tag_insights = [
        ("01. 정부 정책과 연계된 '#청년패스'", "청년 문화비 지원의 구매 트리거",
         "• 청년 문화예술패스 지원금 적용 여부가 2030 세대의 실질 구매 전환 촉진\n• IT 실습서 및 수험서 구매 시 정부 지원금을 적극 활용하는 소비 행태\n• 출판사 및 서점 유통 시 청년패스 지정 도서 등록이 필수 마케팅 요소"),
        ("02. 학습 환경 최적화 '#분철' 선호", "코딩 실습 독자의 독특한 니즈",
         "• 500~700페이지의 두꺼운 IT 교재를 180도 펼쳐놓고 양손으로 키보드 타건\n• 일반 무선 제본보다 추가 비용을 지불하고 스프링 분철 옵션을 적극 선택\n• 출판 기획 시 판형과 제본 편의성을 고려한 편집 디자인의 중요성 대두"),
        ("03. '#크레마클럽' 전자책 교차 소비", "구독 탐색 후 실물 종이책 소장",
         "• 전자책 구독으로 목차와 초반 실습을 훑어본 뒤 만족 시 실물 소장용 구매\n• 전자책과 종이책이 카니발라이제이션이 아닌 상호 보완재로 작동\n• 기술 키워드는 AI와 파이썬이 독점하며 직장인 '일잘러' 키워드와 결합")
    ]
    for i, (ttitle, tsub, tdesc) in enumerate(tag_insights):
        x = 0.8 + i * 3.98
        c = add_card(s23, x, 1.9, 3.8, 4.3)
        tbar = s23.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = COLOR_CARD_HEADER
        tbar.line.fill.background()
        p = tbar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = ttitle.split(".")[0] + " " + tsub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        tbar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s23.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = ttitle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in tdesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s23, 0.8, 6.35, 11.733, 0.85, "유통 전략 제언",
                "온라인 서점 유통 시 분철 옵션 지원과 청년패스 지정 등록, 전자책 구독과의 연계 프로모션이 도서 판매량을 견인하는 3대 실용 유통 트리거로 확인되었습니다.")

    add_notes(s23, """이 태그 데이터가 보여주는 독자들의 소비 패턴은 매우 실용적입니다.
첫째, 정부와 지자체의 청년 문화비 지원 정책인 '청년패스' 적용 여부가 독자들의 실제 도서 구매 전환에 매우 결정적인 기폭제로 작용하고 있습니다.
둘째, '분철' 태그의 높은 빈도는 IT 학습자들의 독특한 독서 행태를 드러냅니다. 코딩 실습서는 모니터 옆에 책을 180도로 완전히 펼쳐놓고 키보드를 쳐야 하기 때문에, 수험생과 실무자들은 기꺼이 추가 비용을 내고 스프링 분철 옵션을 선택합니다.
셋째, 크레마클럽 구독을 통해 책의 일부를 전자책으로 훑어본 뒤 마음에 들면 종이책으로 구매하는 '크로스 플랫폼 독서' 행태가 일상화되었습니다.
기술 키워드로는 AI와 파이썬이 완벽히 시장을 지배하고 있으며, 직장인들의 실용성을 대변하는 '일잘러업무스킬'이 강세를 보이고 있습니다.""")

    # ==========================================
    # SLIDE 24: 도서명 및 부제목 TF-IDF 핵심 키워드 (차트 7)
    # ==========================================
    s24 = prs.slides.add_slide(blank_layout)
    add_bg(s24, COLOR_BG_LIGHT)
    add_header(s24, "도서명 및 부제목 TF-IDF 핵심 키워드", "Part 3. 텍스트 마이닝")

    c24_l = add_card(s24, 0.8, 1.9, 5.3, 5.1)
    tb24 = s24.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf24 = tb24.text_frame
    tf24.word_wrap = True
    p = tf24.paragraphs[0]
    r = p.add_run()
    r.text = "🔤 TF-IDF 상위 가중치 키워드표\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    tfidf_words = [
        ("1위. ai", "174.96 (2위 대비 2배 이상 독주)"),
        ("2위. 위한", "80.91 (타깃 독자 명시 어휘)"),
        ("3위. 배우는", "65.84 (학습·입문 지향성)"),
        ("5위. 코딩", "43.62 (실무 개발 중심)"),
        ("7위. 실전", "37.75 (프로젝트 실행형)"),
        ("8위. 실무", "35.86 (현업 직결 콘텐츠)"),
        ("9위. 에이전트", "33.82 (자율 AI 신규 트렌드)"),
        ("12위. 클로드", "31.98 (최신 코딩 도구의 부상)"),
        ("26위. 바이브", "22.10 (Vibe Coding 신조어)")
    ]
    for k, v in tfidf_words:
        p_s = tf24.add_paragraph()
        p_s.space_before = Pt(3)
        r_k = p_s.add_run()
        r_k.text = f"{k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf24.add_paragraph()
    p_obs.space_before = Pt(8)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 텍스트 트렌드 시사점\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf24.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "형태소 분석기 없이 순수 TF-IDF로 분석한 결과, 'ai'의 압도적 독주와 함께 '클로드', '에이전트', '바이브 코딩', '자동화'가 핵심 어휘로 급부상했습니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img7_path = "yes24/images/07_tfidf_top30_keywords.png"
    if os.path.exists(img7_path):
        s24.shapes.add_picture(img7_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s24, """이번 차트는 Scikit-learn의 TF-IDF 벡터라이저를 사용하여 1,000권 도서의 제목과 부제목 텍스트에서 추출한 핵심 키워드 가중치 상위 30개입니다.
오른쪽 그래프를 보시면 단연 압도적인 1위는 영문 `ai`로 가중치가 무려 174.96에 달합니다. 2위인 `위한`(80.91) 대비 2배가 넘는 수치입니다.
왼쪽 표에 정리된 것처럼 주요 기술 단어들을 보시면 `코딩`, `실전`, `실무`, `에이전트`, `클로드`, `챗gpt`, `제미나이`, `바이브`, `자동화` 등이 최상위권을 휩쓸고 있습니다. 제목 속에 담긴 어휘들만 보아도 현재 IT 독자들이 어떤 기술에 가장 목말라하고 있는지가 투명하게 드러납니다.""")

    # ==========================================
    # SLIDE 25: 텍스트 마이닝 인사이트: 에이전틱 코딩으로의 전환
    # ==========================================
    s25 = prs.slides.add_slide(blank_layout)
    add_bg(s25, COLOR_BG_LIGHT)
    add_header(s25, "텍스트 마이닝 인사이트: 이론에서 실무·에이전트로의 대전환", "Part 3. 텍스트 트렌드")

    ai_trends = [
        ("01. 'ai' 키워드의 압도적 시장 지배", "독보적 가중치 174.96 기록",
         "• 2위 키워드 대비 2배 이상, 일반 프로그래밍 언어 대비 10배 이상의 가중치 독점\n• '인공지능', '챗gpt', '제미나이', '클로드'가 동반 최상위권 형성\n• AI와 무관한 단순 전통 코딩 서적의 수요 위축 및 AI 융합 필수화"),
        ("02. '에이전틱 & 바이브 코딩' 신드롬", "단순 챗봇 문답에서 자율 실행으로",
         "• '에이전트(33.82)', '클로드(31.98)', '바이브(22.10)', '코드(21.24)'의 급부상\n• 프롬프트 문답을 넘어 CLI/IDE에서 AI가 직접 코드를 작성·테스트하는 패러다임\n• 개발자의 생산성을 10배 향상시키는 차세대 워크플로우 도서 갈망"),
        ("03. '실전 · 실무 · 자동화' 중심 기획", "읽는 책이 아닌 '당장 쓰는 책'",
         "• '실전(37.75)', '실무(35.86)', '만들기(28.86)', '활용(29.17)', '자동화(18.59)' 결합\n• 뜬구름 잡는 미래학적 담론보다 내일 출근해서 쓸 수 있는 실무 예제 선호\n• 엑셀 업무 자동화, 웹 서비스 원데이 빌드 등 즉각형 프로젝트 도서 강세")
    ]
    for i, (atitle, asub, adesc) in enumerate(ai_trends):
        x = 0.8 + i * 3.98
        c = add_card(s25, x, 1.9, 3.8, 4.3)
        abar = s25.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.9), Inches(3.8), Inches(0.45))
        abar.fill.solid()
        abar.fill.fore_color.rgb = COLOR_CARD_HEADER
        abar.line.fill.background()
        p = abar.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = atitle.split(".")[0] + " " + asub
        set_font(r, FONT_TITLE, 11, bold=True, color=COLOR_ACCENT_DARK)
        abar.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        tb = s25.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(3.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = atitle.split(".")[1].strip() + "\n\n"
        set_font(r1, FONT_TITLE, 14, bold=True, color=COLOR_PRIMARY)
        
        for line in adesc.split("\n"):
            p_l = tf.add_paragraph()
            p_l.space_before = Pt(4)
            r_l = p_l.add_run()
            r_l.text = line
            set_font(r_l, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_callout(s25, 0.8, 6.35, 11.733, 0.85, "기획 방향 제언",
                "독자들은 이제 단순 프롬프트 대화법이 아닌, '클로드 코드 기반 에이전틱 바이브 코딩'과 '실무 엑셀·업무 자동화'처럼 실질적 결과물을 산출하는 프로젝트형 책에 지갑을 엽니다.")

    add_notes(s25, """TF-IDF 결과가 제시하는 가장 핵심적인 트렌드 전환은 '대화형 AI에서 에이전틱 코딩으로의 진화'입니다.
작년까지만 해도 'ChatGPT에게 좋은 질문 던지는 법' 같은 프롬프트 엔지니어링이나 대화법 서적이 주를 이루었습니다. 하지만 2026년 현재 독자들은 더 이상 단순 대화에 만족하지 않습니다.
'에이전트', '클로드 코드', '바이브 코딩' 키워드의 폭발적 부상이 의미하는 것은, AI가 개발 환경 안에서 직접 파일을 수정하고 테스트하며 코드를 작성하는 '실행형 워크플로우'에 대한 수요입니다.
또한 `실전`, `실무`, `만들기`, `업무`, `자동화`라는 단어들의 결합은, 독자들이 더 이상 뜬구름 잡는 미래학적 기술 이론서를 사지 않고, 당장 내일 출근해서 내 업무 시간을 반으로 줄여줄 수 있는 실전 프로젝트 도서만을 엄격하게 골라 구매하고 있음을 확증합니다.""")

    # ==========================================
    # SLIDE 26: [간지 4] Part 4
    # ==========================================
    s26 = prs.slides.add_slide(blank_layout)
    add_bg(s26, COLOR_BG_DARK)
    c26 = add_card(s26, 1.2, 1.2, 10.933, 5.1, bg_color=COLOR_BG_DARK, border_color=COLOR_ACCENT)
    
    badge_s26 = s26.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.8), Inches(2.0), Inches(0.45))
    badge_s26.fill.solid()
    badge_s26.fill.fore_color.rgb = COLOR_ACCENT
    badge_s26.line.fill.background()
    p = badge_s26.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "SECTION 04"
    set_font(r, FONT_TITLE, 13, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    tb26 = s26.shapes.add_textbox(Inches(1.8), Inches(2.5), Inches(9.5), Inches(3.2))
    tf26 = tb26.text_frame
    tf26.word_wrap = True
    p = tf26.paragraphs[0]
    r = p.add_run()
    r.text = "다변량 관계 및 비즈니스 제언\n"
    set_font(r, FONT_TITLE, 34, bold=True, color=RGBColor(0xF4, 0xF1, 0xEC))

    p2 = tf26.add_paragraph()
    p2.space_before = Pt(16)
    r2 = p2.add_run()
    r2.text = "출판사별 가격-판매지수 매트릭스, 가격대 구간별 상자그림 및 평점-리뷰 수렴 분석,\n상관계수 히트맵 및 피봇 분석을 종합한 20년차 분석가의 전략적 실행 가이드라인"
    set_font(r2, FONT_BODY, 16, bold=False, color=RGBColor(0xC5, 0xBC, 0xB2))

    add_notes(s26, """마지막 네 번째 파트인 '다변량 관계 분석 및 비즈니스 제언'에 오신 것을 환영합니다.
데이터 분석의 진정한 가치는 단일 변수의 관찰을 넘어, 변수와 변수가 교차할 때 비로소 드러나는 인과적 메커니즘과 패턴을 포착하는 데 있습니다.
이번 파트에서는 출판사별 가격 정책과 판매 성과의 상관성, 가격대별 이상치와 중앙값을 비교하는 상자그림, 평점과 리뷰 수가 서로를 어떻게 견인하는지 보여주는 산점도, 그리고 전체 수치 변수 간의 피어슨 상관계수 행렬을 면밀히 분석합니다.
나아가 최근 4개년 출판연도와 가격대의 피봇 히트맵을 통해 최신 시장의 프라이싱 트렌드를 확정 짓고, 이를 토대로 출판사와 기획자가 즉각 실행할 수 있는 3대 핵심 비즈니스 전략과 데이터 무결성 검증 통과 내역을 제시해 드리겠습니다.""")

    # ==========================================
    # SLIDE 27: 상위 출판사별 평균 판매가 vs 평균 판매지수 (차트 8)
    # ==========================================
    s27 = prs.slides.add_slide(blank_layout)
    add_bg(s27, COLOR_BG_LIGHT)
    add_header(s27, "상위 출판사별 평균 판매가 vs 평균 판매지수", "Part 4. 다변량 분석")

    c27_l = add_card(s27, 0.8, 1.9, 5.3, 5.1)
    tb27 = s27.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf27 = tb27.text_frame
    tf27.word_wrap = True
    p = tf27.paragraphs[0]
    r = p.add_run()
    r.text = "⚖️ 출판사별 가격-성과 포지셔닝\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    pubs_mat = [
        ("길벗", "24,949원 | 지수 3,923 (최고 성과 리더)"),
        ("골든래빗", "26,460원 | 지수 3,892 (고단가 프리미엄 성공)"),
        ("한빛미디어", "25,603원 | 지수 3,865 (볼륨 & 고지수 유지)"),
        ("앤써북", "19,831원 | 지수 3,248 (2만원 미만 고회전)"),
        ("이지스퍼블리싱", "22,963원 | 지수 3,124 (대중 실용 가격)"),
        ("제이펍", "25,820원 | 지수 2,756 (전문 번역서 지지)"),
        ("위키북스", "27,867원 | 지수 2,412 (최고 단가 형성)"),
        ("커뮤니케이션북스", "13,852원 | 지수 892 (초저단가 니치)")
    ]
    for k, v in pubs_mat:
        p_s = tf27.add_paragraph()
        p_s.space_before = Pt(3)
        r_k = p_s.add_run()
        r_k.text = f"• {k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf27.add_paragraph()
    p_obs.space_before = Pt(8)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 가격-성과 시사점\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf27.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "길벗과 골든래빗은 25,000~26,000원대의 높은 단가에도 불구하고 평균 판매지수 3,900 안팎을 기록하여, 양질의 콘텐츠가 가격 저항을 압도함을 증명합니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img8_path = "yes24/images/08_publisher_price_sales_bivariate.png"
    if os.path.exists(img8_path):
        s27.shapes.add_picture(img8_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s27, """상위 10개 출판사의 평균 판매가와 평균 판매지수를 교차 분석한 산점도와 집계표입니다.
오른쪽 그래프를 보시면 출판사마다 위치한 사분면이 뚜렷하게 나뉩니다.
길벗은 평균 판매가 24,949원에 평균 판매지수 3,923으로 10대 출판사 중 가장 높은 판매지수를 기록했습니다. 골든래빗은 평균 단가가 26,460원으로 가장 높음에도 불구하고 평균 판매지수 3,892를 달성하며 '고단가 고품질 전문서 전략'이 완벽하게 통함을 입증했습니다.
반면 이지스퍼블리싱은 22,900원대의 친숙한 가격대로 3,124의 지수를 유지했고, 앤써북은 19,800원대의 가성비 전략으로 높은 회전율을 보였습니다. 즉 출판사마다 타깃 독자에 맞춘 뚜렷한 프라이싱 포지셔닝을 구사하고 있음을 확인했습니다.""")

    # ==========================================
    # SLIDE 28: 도서 가격대 구간별 판매지수 상자그림 (차트 9)
    # ==========================================
    s28 = prs.slides.add_slide(blank_layout)
    add_bg(s28, COLOR_BG_LIGHT)
    add_header(s28, "도서 가격대 구간별 판매지수 상자그림 (Boxplot)", "Part 4. 다변량 분석")

    c28_l = add_card(s28, 0.8, 1.9, 5.3, 5.1)
    tb28 = s28.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(4.9), Inches(4.8))
    tf28 = tb28.text_frame
    tf28.word_wrap = True
    p = tf28.paragraphs[0]
    r = p.add_run()
    r.text = "📦 가격대별 판매지수 기술통계표\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    box_stats = [
        ("1.5만 미만 (102권)", "평균 1,684 | 중앙값 852 (입문/교양서 한계)"),
        ("1.5만~2만원 (285권)", "평균 3,215 | 중앙값 1,420 (최대 판매지수)"),
        ("2만~2.5만원 (268권)", "평균 3,184 | 중앙값 1,390 (고수익 황금구간)"),
        ("2.5만~3만원 (215권)", "평균 2,892 | 중앙값 1,280 (전문 실습서 지지)"),
        ("3만~5만원 (124권)", "평균 1,985 | 중앙값 964 (가격 저항 발생)"),
        ("5만 이상 (6권)", "평균 2,120 | 중앙값 1,050 (견고한 틈새 수요)")
    ]
    for k, v in box_stats:
        p_s = tf28.add_paragraph()
        p_s.space_before = Pt(4)
        r_k = p_s.add_run()
        r_k.text = f"• {k}: "
        set_font(r_k, FONT_BODY, 11, bold=True, color=COLOR_TEXT_MAIN)
        r_v = p_s.add_run()
        r_v.text = v
        set_font(r_v, FONT_BODY, 10, bold=False, color=COLOR_TEXT_MUTED)

    p_obs = tf28.add_paragraph()
    p_obs.space_before = Pt(12)
    r_obs = p_obs.add_run()
    r_obs.text = "📌 황금 구간(Sweet Spot) 규명\n"
    set_font(r_obs, FONT_TITLE, 13, bold=True, color=COLOR_PRIMARY)
    p_obs2 = tf28.add_paragraph()
    r_obs2 = p_obs2.add_run()
    r_obs2.text = "1.5만~2.5만원 구간이 중앙값(1,400선)과 상위 이상치(판매지수 2만~7만대 초대형 메가 베스트셀러)를 최다 배출하는 최적의 시장입니다."
    set_font(r_obs2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    img9_path = "yes24/images/09_price_bracket_sales_boxplot.png"
    if os.path.exists(img9_path):
        s28.shapes.add_picture(img9_path, Inches(6.3), Inches(1.9), Inches(6.233), Inches(5.1))

    add_notes(s28, """도서 가격대별 판매 성과를 박스플롯으로 시각화한 결과입니다. 상자그림은 데이터의 중앙값과 4분위수뿐만 아니라, 상단의 이상치 즉 메가 베스트셀러의 분포를 한눈에 보여줍니다.
오른쪽 그래프에서 가장 주목할 구간은 `1.5만~2만원`과 `2만~2.5만원` 구간입니다.
이 두 구간은 중앙값 판매지수가 각각 1,420과 1,390으로 가장 높을 뿐만 아니라, 상자 상단으로 길게 뻗은 점들(판매지수 2만~7만 이상의 초대형 히트작)이 집중적으로 쏟아져 나오고 있습니다.
반면 3만원을 초과하는 구간으로 넘어가면 중앙값이 964 수준으로 급락하며 상위 이상치의 빈도도 크게 줄어듭니다. 따라서 대중적 판매 볼륨과 출판사 마진을 동시에 극대화할 수 있는 비즈니스 스윗스팟은 단연 2만~2.5만원 구간임을 통계적으로 명백히 확인할 수 있습니다.""")

    # ==========================================
    # SLIDE 29: 평점 vs 리뷰수 산점도 및 상관계수 (차트 10, 11)
    # ==========================================
    s29 = prs.slides.add_slide(blank_layout)
    add_bg(s29, COLOR_BG_LIGHT)
    add_header(s29, "평점 vs 리뷰수 산점도 및 수치형 상관계수 행렬", "Part 4. 다변량 분석")

    # 상단: 2개 차트 나란히 배치
    img10_path = "yes24/images/10_rating_vs_reviews_scatter.png"
    img11_path = "yes24/images/11_correlation_matrix_heatmap.png"
    if os.path.exists(img10_path):
        s29.shapes.add_picture(img10_path, Inches(0.8), Inches(1.9), Inches(5.75), Inches(3.4))
    if os.path.exists(img11_path):
        s29.shapes.add_picture(img11_path, Inches(6.78), Inches(1.9), Inches(5.75), Inches(3.4))

    # 하단 2개 해석 카드
    c29_1 = add_card(s29, 0.8, 5.45, 5.75, 1.6)
    tb29_1 = s29.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(5.35), Inches(1.4))
    tf29_1 = tb29_1.text_frame
    tf29_1.word_wrap = True
    p = tf29_1.paragraphs[0]
    r = p.add_run()
    r.text = "🎯 평점-리뷰 수렴 메커니즘 (대수의 법칙)\n"
    set_font(r, FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)
    p2 = tf29_1.add_paragraph()
    r2 = p2.add_run()
    r2.text = "리뷰 수가 100건 이상 누적된 대형 도서는 예외 없이 9.5~9.8점의 좁은 고득점 영역에 수렴합니다. 10점 만점 도서는 리뷰 10건 미만 소규모 초기 표본 효과가 지배적입니다."
    set_font(r2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    c29_2 = add_card(s29, 6.78, 5.45, 5.75, 1.6)
    tb29_2 = s29.shapes.add_textbox(Inches(6.98), Inches(5.55), Inches(5.35), Inches(1.4))
    tf29_2 = tb29_2.text_frame
    tf29_2.word_wrap = True
    p = tf29_2.paragraphs[0]
    r = p.add_run()
    r.text = "🔗 판매지수 핵심 동인: 리뷰수 (r = +0.46)\n"
    set_font(r, p.runs[0].font.name if p.runs else FONT_TITLE, 13, bold=True, color=COLOR_ACCENT_DARK)
    p2 = tf29_2.add_paragraph()
    r2 = p2.add_run()
    r2.text = "판매지수와 가장 강력한 양의 상관관계를 갖는 변수는 리뷰수(r = +0.46)입니다. 반면 가격이나 할인율은 판매지수와 상관성이 거의 없어(r ≈ 0.05), 가격 탄력성이 낮은 시장임을 확인했습니다."
    set_font(r2, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_notes(s29, """독자의 만족도를 대변하는 평점과 독자의 적극적 행동을 대변하는 리뷰 수 간의 산점도, 그리고 전체 수치형 변수의 상관계수 행렬입니다.
왼쪽 산점도를 보시면 매우 전형적인 '대수의 법칙'에 따른 수렴 깔때기 형태가 관찰됩니다. 리뷰가 100건 이상 누적되어 1,240건에 이르는 대형 베스트셀러 도서들은 예외 없이 평점이 9.5점에서 9.8점 사이의 좁은 구간으로 강력하게 수렴합니다.
오른쪽 상관계수 행렬표에서 비즈니스적으로 가장 주목하셔야 할 수치는 바로 '판매지수와 리뷰수'의 상관계수입니다. 상관계수 r이 무려 0.46으로 전체 변수 쌍 중 가장 강한 양의 상관관계를 기록했습니다.
반면 판매가나 정가는 판매지수와의 상관계수가 0.05~0.06으로 거의 0에 가깝습니다. 이는 책 가격이 비싸다고 해서 덜 팔리거나, 싸다고 해서 더 많이 팔리는 가격 탄력성이 IT 도서 시장에서는 거의 작동하지 않음을 시사합니다.""")

    # ==========================================
    # SLIDE 30: 최근 출판연도 × 가격대 피봇 히트맵 & 수석 분석가의 3대 비즈니스 제언
    # ==========================================
    s30 = prs.slides.add_slide(blank_layout)
    add_bg(s30, COLOR_BG_LIGHT)
    add_header(s30, "연도×가격 피봇 분석 및 수석 분석가의 3대 비즈니스 제언", "Part 4. 종합 제언")

    # 좌측: 피봇 히트맵 이미지
    img12_path = "yes24/images/12_year_price_sales_pivot_heatmap.png"
    if os.path.exists(img12_path):
        s30.shapes.add_picture(img12_path, Inches(0.8), Inches(1.9), Inches(5.5), Inches(5.1))

    # 우측: 3대 핵심 비즈니스 제언 카드
    c30_r = add_card(s30, 6.5, 1.9, 6.033, 5.1)
    tb30 = s30.shapes.add_textbox(Inches(6.75), Inches(2.05), Inches(5.5), Inches(4.8))
    tf30 = tb30.text_frame
    tf30.word_wrap = True
    p = tf30.paragraphs[0]
    r = p.add_run()
    r.text = "🏆 20년차 수석 데이터 분석가의 3대 실행 전략\n"
    set_font(r, FONT_TITLE, 15, bold=True, color=COLOR_ACCENT_DARK)

    biz_strategies = [
        ("전략 1. Sweet Spot Pricing (24,000 ~ 28,000원)",
         "피봇 분석 결과 2026년 2만~2.5만원대 도서의 평균 지수가 4,120으로 역대 최고치입니다. 어설픈 저가 정책보다 예제와 실습 분량을 충실히 담아 2만원 중후반대로 책정하는 것이 매출과 브랜드 가치를 극대화합니다."),
        ("전략 2. 콘텐츠 테마: '에이전틱 실무 자동화' 집중",
         "TF-IDF 1위 키워드 'ai'와 급부상한 '클로드', '바이브 코딩', '에이전트', '자동화'를 전면에 배치하십시오. 단순 프롬프트 문답을 넘어 IDE/CLI 환경에서 코드를 생성·배포하는 실행형 워크플로우 기획이 필수적입니다."),
        ("전략 3. 출간 직후 '리뷰 50건' 신속 부스팅",
         "상관계수 0.46이 입증하듯 리뷰 수는 판매지수의 핵심 동인입니다. 사전 서평단, 개발자 커뮤니티 협업, 독자 리뷰 리워드 이벤트를 집중 전개하여 출간 첫 달 내 진성 리뷰 임계점(50건)을 신속히 돌파해야 베스트셀러에 롱런합니다.")
    ]
    for stitle, sdesc in biz_strategies:
        p_t = tf30.add_paragraph()
        p_t.space_before = Pt(8)
        r_t = p_t.add_run()
        r_t.text = f"{stitle}\n"
        set_font(r_t, FONT_TITLE, 12, bold=True, color=COLOR_PRIMARY)
        p_d = tf30.add_paragraph()
        r_d = p_d.add_run()
        r_d.text = sdesc
        set_font(r_d, FONT_BODY, 11, bold=False, color=COLOR_TEXT_MAIN)

    add_notes(s30, """마지막 슬라이드에서는 최근 4개년 출판연도와 가격대별 피봇 분석 결과와 함께, 출판 현장에서 즉시 적용할 수 있는 수석 분석가의 3대 핵심 비즈니스 제언을 드립니다.
왼쪽 피봇 히트맵을 보시면 2026년 현재 2만~2.5만원대 및 2.5만~3만원대 도서의 평균 판매지수가 4,120선까지 치솟아 역대 최고치를 기록했습니다. 독자들은 고품질 AI 실습서에 대해 2만원 중후반대의 비용을 아낌없이 지불하고 있습니다.
이를 토대로 3대 전략을 제언합니다.
첫째, 가격 책정 전략입니다. 황금 가격대는 '24,000원에서 28,000원'입니다. 무리한 저가 정책보다는 실습 분량과 예제를 담아 가치를 입증하는 가격 책정이 출판사 이익을 극대화합니다.
둘째, 기획 콘텐츠의 테마입니다. 단순 프롬프트 문답이 아닌 '클로드 코드', '바이브 코딩', '자율 에이전트', '실무 자동화'를 전면에 배치하십시오.
셋째, 마케팅 액션 플랜입니다. 출간 직후 4주 내에 '리뷰 50건'을 사수하십시오. 리뷰와 판매지수의 상관계수는 0.46입니다. 초기 서평단과 커뮤니티 리워드를 집중 투입해 임계 리뷰를 돌파하는 것이 성공의 핵심 방정식입니다.
경청해 주셔서 대단히 감사드립니다.""")

    # 파일 저장
    output_path = "yes24/docs/eda_presentation.pptx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"PPTX Deck generated successfully: {output_path} (Total 30 slides)")

if __name__ == "__main__":
    create_deck()
