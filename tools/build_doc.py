# -*- coding: utf-8 -*-
"""生成《薪火仁义 · 设计说明书》"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"C:\Users\春生\Desktop\农创"
SHOTS = os.path.join(ROOT, "shots")

RED = RGBColor(0xA6, 0x3A, 0x2E)
RED_D = RGBColor(0x7A, 0x28, 0x20)
INK = RGBColor(0x2A, 0x24, 0x1E)
INK2 = RGBColor(0x6B, 0x5D, 0x50)
INK3 = RGBColor(0x99, 0x8B, 0x7C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SANS = "微软雅黑"
SERIF = "宋体"

doc = Document()

# ---------- 页面 ----------
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.left_margin = Cm(2.1)
sec.right_margin = Cm(2.1)
sec.top_margin = Cm(2.0)
sec.bottom_margin = Cm(1.9)

# ---------- 默认样式 ----------
st = doc.styles["Normal"]
st.font.name = SANS
st.font.size = Pt(9.5)
st.font.color.rgb = INK
st.element.rPr.rFonts.set(qn("w:eastAsia"), SANS)
st.paragraph_format.line_spacing = 1.65
st.paragraph_format.space_after = Pt(4)


def font(run, name=SANS, size=9.5, bold=False, color=INK, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    return run


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def cell_margins(table, top=40, bottom=40, left=100, right=100):
    tbl = table._tbl
    tblPr = tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement("w:" + k)
        e.set(qn("w:w"), str(v))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)


def no_border(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "none")
        e.set(qn("w:sz"), "0")
        borders.append(e)
    tblPr.append(borders)


def p(text="", size=9.5, color=INK, bold=False, name=SANS, align=None,
      before=0, after=4, indent=0.0, line=1.65, first_line=0.0):
    par = doc.add_paragraph()
    pf = par.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if indent:
        pf.left_indent = Cm(indent)
    if first_line:
        pf.first_line_indent = Cm(first_line)
    if align == "center":
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    elif align == "just":
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if text:
        font(par.add_run(text), name=name, size=size, bold=bold, color=color)
    return par


def rule(color="A63A2E", size=8, space_before=6, space_after=10):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(space_before)
    par.paragraph_format.space_after = Pt(space_after)
    pPr = par._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)
    return par


def h1(num, text, en=""):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(20)
    par.paragraph_format.space_after = Pt(2)
    font(par.add_run(num + "  "), name=SERIF, size=17, bold=True, color=RED)
    font(par.add_run(text), name=SANS, size=15, bold=True, color=INK)
    if en:
        font(par.add_run("   " + en), name=SANS, size=7.5, color=INK3)
    rule(size=10, space_before=2, space_after=9)
    return par


def h2(text, tag=""):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(12)
    par.paragraph_format.space_after = Pt(3)
    font(par.add_run("▍"), size=9, color=RED)
    font(par.add_run(text), name=SANS, size=11.5, bold=True, color=RED_D)
    if tag:
        font(par.add_run("  " + tag), size=7.5, color=INK3)
    return par


def body(text, indent=0.0, after=5):
    return p(text, size=9.5, color=RGBColor(0x33, 0x2C, 0x26), align="just",
             after=after, indent=indent, line=1.75)


def bullet(text, lead=""):
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Cm(0.55)
    par.paragraph_format.space_after = Pt(3)
    par.paragraph_format.line_spacing = 1.7
    font(par.add_run("— "), size=9, color=RGBColor(0xB8, 0x89, 0x3F))
    if lead:
        font(par.add_run(lead), size=9.5, bold=True, color=RED_D)
    font(par.add_run(text), size=9.5, color=RGBColor(0x33, 0x2C, 0x26))
    return par


def caption(text, align="left"):
    return p(text, size=7.8, color=INK3, align=align, before=2, after=10, line=1.4)


def image(path, width_cm=16.0):
    doc.add_picture(path, width=Cm(width_cm))
    par = doc.paragraphs[-1]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(0)
    par.paragraph_format.keep_with_next = True


def data_table(headers, rows, widths=None, head_bg="A63A2E", size=8.6, first_col_bold=True):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    cell_margins(t, 50, 50, 90, 90)
    TOTAL = 16.6
    if widths:
        s = sum(widths)
        widths = [w * TOTAL / s for w in widths]
    else:
        widths = [TOTAL / len(headers)] * len(headers)
    tblPr = t._tbl.tblPr
    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), str(int(TOTAL * 567)))
    tblW.set(qn("w:type"), "dxa")
    tblPr.append(tblW)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    hdr = t.rows[0].cells
    for i, htxt in enumerate(headers):
        shade(hdr[i], head_bg)
        par = hdr[i].paragraphs[0]
        par.paragraph_format.space_after = Pt(1)
        font(par.add_run(htxt), size=size, bold=True, color=WHITE)
    for r, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            if r % 2 == 1:
                shade(cells[i], "FBF7EF")
            par = cells[i].paragraphs[0]
            par.paragraph_format.space_after = Pt(1)
            par.paragraph_format.line_spacing = 1.45
            bold = first_col_bold and i == 0
            font(par.add_run(val), size=size, bold=bold,
                 color=RED_D if bold else RGBColor(0x3B, 0x33, 0x2B))
    for i, w in enumerate(widths):
        for row in t.rows:
            row.cells[i].width = Cm(w)
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
    return t


def two_col_screens(items, w=7.6):
    """两列界面截图 + 图注"""
    for i in range(0, len(items), 2):
        pair = items[i:i + 2]
        t = doc.add_table(rows=2, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        no_border(t)
        for j, (fname, title, note) in enumerate(pair):
            cell = t.rows[0].cells[j]
            par = cell.paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(0)
            run = par.add_run()
            run.add_picture(os.path.join(SHOTS, fname), width=Cm(w))
            par.paragraph_format.keep_with_next = True
            cap = t.rows[1].cells[j].paragraphs[0]
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.space_after = Pt(9)
            font(cap.add_run(title + "\n"), size=8.6, bold=True, color=RED_D)
            font(cap.add_run(note), size=7.6, color=INK2)
        doc.add_paragraph().paragraph_format.space_after = Pt(0)


def page_number_footer():
    footer = doc.sections[0].footer
    par = footer.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    font(par.add_run("薪火仁义 · 天全县仁义镇红色研学与在地体验   |   "), size=7.5, color=INK3)
    run = par.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = "PAGE"
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    run._r.append(f1); run._r.append(it); run._r.append(f2)
    font(run, size=7.5, color=INK3)


# =====================================================================
# 封面
# =====================================================================
p("", after=0)
p("", after=0)
p("N U M B E R   0 1 7   ·   D I G I T A L   V I L L A G E   S E R V I C E   D E S I G N",
  size=7.2, color=INK3, after=16)

par = doc.add_paragraph()
par.paragraph_format.space_after = Pt(2)
font(par.add_run("薪火"), name=SERIF, size=44, bold=True, color=INK)
font(par.add_run("仁义"), name=SERIF, size=44, bold=True, color=RED)

p("天全县仁义镇 · 红色研学与在地体验小程序", size=13, color=INK2, after=6)
p("从“8 处遗址、13 个村”到一条可以下单的一天", size=10.5, color=INK3, after=26)

rule(size=18, space_before=0, space_after=14)

t = doc.add_table(rows=0, cols=2)
no_border(t)
cell_margins(t, 30, 30, 0, 80)
meta = [
    ("作品类别", "数字乡村服务设计"),
    ("作品载体", "微信小程序（高保真可点击原型）＋ 后台服务逻辑"),
    ("设计对象", "四川省雅安市天全县仁义镇 · 红军村及周边村落"),
    ("核心服务", "红色研学组队预约 · 遗址打卡集章 · 非遗与农事体验 · 红军食堂与民宿 · 助农风物"),
    ("交付物", "① 可交互原型  ② 本说明书（含设计过程、界面与交互、后台逻辑）"),
]
for k, v in meta:
    row = t.add_row().cells
    par = row[0].paragraphs[0]
    par.paragraph_format.space_after = Pt(5)
    font(par.add_run(k), size=8.4, color=INK3)
    par2 = row[1].paragraphs[0]
    par2.paragraph_format.space_after = Pt(5)
    font(par2.add_run(v), size=9.4, color=RGBColor(0x33, 0x2C, 0x26), bold=True)

doc.add_paragraph().paragraph_format.space_after = Pt(40)
par = doc.add_paragraph()
par.paragraph_format.space_after = Pt(2)
font(par.add_run("一句话"), size=8, color=RED)
p("把“看一次就走”的红色景点，改成“做一天粮仓人”的完整服务：一次组队下单、四件必须完成的事、八枚现场印章、一张能核验的证书。",
  size=11.5, color=INK, after=0, line=1.85)

doc.add_page_break()

# =====================================================================
# 摘要
# =====================================================================
h1("00", "作品摘要", "ABSTRACT")

body("仁义镇是四川雅安天全县北部的一个镇。2019 年由仁义乡、老场乡合并设立，辖 13 个村；镇域内 4 个村分布着 8 处红军遗址——红四方面军总司令部旧址、总政治部旧址、红军井、红军大学旧址、红军总医院旧址、总指挥部遗址、红军粮仓遗址、红军盐厂遗址，2018 年更名的“红军村”是川西唯一以“红军”命名的行政村。")

body("资源不缺，缺的是把资源变成“服务”的那道工序。调研发现：一个班 40 人的研学团要成行，组织者平均要打 7–8 个电话，分别对接讲解、餐位、场地、停车；游客到现场平均停留约 2 小时、人均消费不到 50 元；学校要一份研学证明，只能手写盖章。红色资源被“看”掉了，没有被“做”出来。")

body("本作品把“文旅＋研学＋民宿＋非遗”收成一个可交付的服务单元——「一日粮仓」：上午在红军大学上一堂情景课，到红军井打一桶水，中午在红军食堂吃一顿忆苦思甜餐，下午推石磨做豆花、下稻田上课，全程集 8 枚遗址印章，结营时生成一张可核验的研学证书。围绕这个单元，设计了一套四方参与的服务系统：游客端小程序、村民/商户工作台、镇村运营看板，以及支撑它们的排程、核销、分账与证书签发逻辑。")

body("设计的重点不在界面好看，而在三个“卡点”上做了取舍：把“排程”从后台功能提升为产品核心——先给方案，再让人填表；把“供给端”压缩到一个按钮——村民扫码即核销，其余自动；把“证明”做成闭环——没到现场盖不出章，没盖章生不成证书。")

data_table(
    ["维度", "设计前", "设计后"],
    [
        ["组织成本", "7–8 通电话、3 个微信群、1 张手抄名单", "1 次下单（选日期人数 → 排程 → 支付）"],
        ["停留时长", "约 2 小时，拍照即走", "6.5 小时，4 个任务、7 个时间节点"],
        ["客单价", "人均不足 50 元", "人均 128 元（课程）＋ 附加体验与住宿"],
        ["成果", "手写盖章证明", "一证一码电子证书，含里程、打卡数与核验编号"],
        ["供给端", "临时找人、口头排班、微信转账", "派单 / 核销 / 分账（农户 87% · 村集体 8% · 平台 5%）"],
    ],
    widths=[2.6, 6.4, 7.8])

p("说明：文中涉及的村名、遗址、历史事件、产业与人流数据，凡标注〔公开资料〕者来自政府与官方媒体公开报道；人物画像、访谈样本、问卷数字、运营指标与商户名称为设计推演与原型示例，用于说明设计逻辑，不构成实际统计。界面中的照片为公开渠道的实拍素材（示意图），正式提交时建议替换为红军村实拍。",
  size=7.8, color=INK3, before=8, after=0, line=1.5)

h2("本册导览")
data_table(
    ["你想了解", "看这一节"],
    [
        ["为什么做这个作品、场地到底什么情况", "01 背景与问题界定"],
        ["设计过程是怎么走的、调研了什么", "01.4 设计过程 · 02 调研与洞察"],
        ["服务是怎么设计的、谁参与", "03 用户旅程与服务蓝图 · 04 设计策略"],
        ["小程序怎么组织、核心流程是什么", "05 信息架构与核心流程"],
        ["主要界面与交互细节", "06 界面与交互设计"],
        ["后台怎么跑、怎么分账", "07 后台服务逻辑"],
        ["怎么验证的、怎么落地", "08 验证与迭代 · 09 落地与运营"],
        ["交付了哪些文件、怎么演示", "10 交付说明"],
    ],
    widths=[9.0, 7.6], size=8.4)
caption("表 0｜阅读导览")

# =====================================================================
h1("01", "背景与问题界定", "CONTEXT")

h2("1.1 场地：一个“有遗址、有产业、有游客，但没产品”的镇")
body("仁义镇位于天全县城北部，2019 年由仁义乡、老场乡合并设镇，镇政府驻永兴村〔公开资料〕。镇域红色资源集中在 4 个村：红军村（原程家窝，总司令部旧址、总政治部旧址、红军井）、红岩村（红军大学旧址、红军总医院旧址）、禾林村（总指挥部遗址、红军粮仓遗址）、老场村（红军盐厂遗址，另有明代杨家土司祠堂，省级文物保护单位）。")
body("1935 年 11 月，红四方面军长征途经天全，在程家窝驻扎战斗生活 118 天，天全人民为红军筹粮约 10 万公斤，并筹集食盐、生姜、辣椒等御寒物资〔公开资料〕。这段“粮仓”历史，是今天所有内容设计的原点——不是抽象的“红色教育”，而是“一亩田怎么养活一支军队”。")
body("产业侧同样有基础：全镇依托水稻连片种植打造万亩生态粮仓产业大环线与环红军村农旅融合小环线；红军村 2021 年获评国家 AAA 级旅游景区，是四川省中小学红色教育研学实践基地、市级自然教育研学基地，年均承接红色研学及党建团建 120 余场次；村内已有 1 个游客中心、4 家红军食堂、1 家特色民宿、1 家星级农家乐、2 家特色院子；稻渔综合种养使亩产值从水稻单作的最高 4000 元提升至近万元〔公开资料〕。")

data_table(
    ["指标", "数值", "来源"],
    [
        ["红军遗址", "8 处，分布在 4 个村", "天全县民政局《天全地名故事录·仁义镇》"],
        ["红军村驻扎时长", "118 天（1935.11 起）", "雅安市人民政府网报道"],
        ["为红军筹粮", "约 10 万公斤", "同上"],
        ["景区等级", "国家 AAA 级（2021 年）", "同上"],
        ["年研学 / 团建接待", "120 余场次", "同上"],
        ["村集体经济收入", "2021 年 7.4 万元 → 2023 年 253 万元", "同上"],
        ["红色研学基地", "省级中小学红色教育研学实践基地", "同上"],
    ],
    widths=[4.0, 7.4, 5.4])
caption("表 1｜场地基础数据（公开资料整理）")

h2("1.2 问题：不是没有内容，是没有“可下单的一天”")
body("我们先把“能不能来”这件事拆开看。一个 40 人的班级研学，实际要解决四类资源的匹配：讲解员、餐位、教学场地、停车位。这四件事分别由村集体、4 家食堂、旧址管理方、游客中心掌握，彼此不通气。组织者只能挨个打电话，且每次改人数都要重来一遍。")
body("第二层问题是“来了做什么”。8 处遗址分散在 4 个村、最远相距约 5 公里，缺少动线设计；遗址以“看 + 听”为主，缺少可参与的环节，导致停留时间短、客单价低、口碑传播弱。")
body("第三层问题是“走了留下什么”。学校需要可归档的研学成果，学生需要可分享的凭据，村集体需要可对账的收入记录——目前三者都落在纸面和微信转账上。")

p("问题陈述（Problem Statement）", size=9.5, bold=True, color=RED_D, before=8, after=3)
body("如何让一个组织者，在 3 分钟内确定“这一天能不能成行”，并让 40 个学生在同一片田野里完成 4 件必须动手的事，最终带走一张学校认、自己能晒、村里可对账的证书？", indent=0.4)

h2("1.3 设计目标")
data_table(
    ["目标", "可度量表述", "对应设计动作"],
    [
        ["降低组织成本", "从 7–8 次沟通降到 1 次下单；排程决策 ≤ 3 分钟", "实时余量 + 四类资源匹配 + 锁位"],
        ["延长停留与提升客单", "停留 2h → 6.5h；人均 50 元 → 128 元起", "「一日粮仓」四任务动线 + 体验 SKU"],
        ["形成可核验成果", "证书领取率 ≥ 90%，学校可扫码核验", "打卡集章 + 一证一码"],
        ["让村民能上手", "村民端核心动作 ≤ 1 次点击", "扫码核销 + 自动分账"],
        ["沉淀运营数据", "镇村可按日看客流、资源利用率、分成", "运营看板 + 冲突预警"],
    ],
    widths=[3.4, 7.2, 6.2])
caption("表 2｜设计目标与对应动作")

h2("1.4 设计过程：两次发散、两次收敛")
body("整个设计过程分六个阶段：场域调研 → 用户研究 → 定义问题 → 服务设计 → 界面与交互 → 测试与迭代。前两个阶段是第一次发散（把问题看清楚），中间两个阶段收敛（把方案定下来），后两个阶段再发散再收敛（把方案做对）。每一阶段的产出都直接成为下一阶段的输入，没有跳步。")
image(os.path.join(SHOTS, "d_process.png"), 16.4)
caption("图 5｜设计过程与时间线（2025.10 – 2026.04）")

# =====================================================================
h1("02", "调研与洞察", "RESEARCH")

h2("2.1 方法与样本")
body("调研分四步：先看现场，再看人，再看竞品，最后回到现场验证。")
data_table(
    ["方法", "对象 / 样本", "主要产出"],
    [
        ["现场观察与动线记录", "8 处遗址、4 个村、2 家食堂、1 家民宿；跟拍 3 个团队", "动线草图、停留时长、卡点位置"],
        ["半结构访谈", "12 人：学校 3、家长 4、党建组织者 2、村民 3", "决策链、真实语言、失败案例"],
        ["问卷", "156 份（教师 / 家长 / 青年游客）", "价格敏感度、内容偏好、阻碍因素"],
        ["桌面研究", "政策文件、政府报道、非遗名录、同类小程序 6 个", "合规边界、可比对标、内容素材"],
        ["村民走查", "村委 2 人、食堂经营者 2 人", "供给端能力与真实顾虑"],
    ],
    widths=[3.8, 6.8, 6.2])
caption("表 3｜调研方法与样本（访谈与问卷为设计推演样本，用于说明逻辑）")

h2("2.2 五个洞察")
insights = [
    ("I1", "真正的用户是“组织者”，不是“游客”。",
     "决定成行的人承担的是责任——安全、时间、费用、交差。他们需要的不是美图，是“确定的答案”：几点到、谁接待、吃什么、下雨怎么办。"),
    ("I2", "供给不缺，缺的是“可售单元”。",
     "讲解、餐、场地、体验各自都成立，但从没被打包成一个 SKU。打包之后才可能被比较、被下单、被复购。"),
    ("I3", "红色资源的“停留价值”没被激活。",
     "遗址是“看”的，不是“做”的。把“看”改成“做”（打水、推磨、割稻），停留时间自然拉长——这是内容设计，不是界面设计。"),
    ("I4", "供给端的数字化门槛在“一次点击”。",
     "村民能接受“扫一下”，不能接受“填一张表”。任何需要培训三步以上的功能，在村里都活不过一个季度。"),
    ("I5", "证明与留存，是同一件东西。",
     "学校要可归档的成果，游客要可炫耀的凭据。做成“一证一码”的电子证书，同时满足两边，还顺带把打卡行为沉淀成数据。"),
]
for k, title, txt in insights:
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(6)
    par.paragraph_format.space_after = Pt(1)
    font(par.add_run(k + "  "), name=SERIF, size=11, bold=True, color=RED)
    font(par.add_run(title), size=10.2, bold=True, color=INK)
    p(txt, size=9.2, color=RGBColor(0x3B, 0x33, 0x2B), align="just", indent=0.62, after=2, line=1.7)

h2("2.3 三个用户画像")
t = doc.add_table(rows=2, cols=3)
no_border(t)
cell_margins(t, 60, 60, 110, 110)
profiles = [
    ("文理｜45 岁", "天全中学 高一班主任", "组织者",
     "一年带两次研学；怕出事、怕家长投诉、怕报不了账。手机里 3 个微信群同时在问“几点集合”。",
     "要一个确定的排程和一张能交给德育处的证明。"),
    ("李桂芳｜48 岁", "红军村 红军食堂经营者", "供给端",
     "旺季一天接 3 个团；不会用电脑，微信转账对账靠记忆；最怕临时改人数。",
     "要一个按钮就能核销，月底能看清自己该拿多少。"),
    ("王芳｜31 岁", "村级讲解员（后备）", "服务者",
     "平时在合作社上班，有团就上；接单靠村委打电话，常常和上班冲突。",
     "要能提前看到派单，能拒绝、能换人。"),
]
for j, (name, role, tag, desc, need) in enumerate(profiles):
    c = t.rows[0].cells[j]
    shade(c, "FBF7EF")
    par = c.paragraphs[0]
    par.paragraph_format.space_after = Pt(0)
    font(par.add_run(tag + "\n"), size=7.5, color=RED)
    font(par.add_run(name + "\n"), size=10, bold=True, color=INK)
    font(par.add_run(role), size=8, color=INK3)
    c2 = t.rows[1].cells[j]
    shade(c2, "FBF7EF")
    par = c2.paragraphs[0]
    par.paragraph_format.space_after = Pt(0)
    font(par.add_run(desc + "\n"), size=8, color=RGBColor(0x3B, 0x33, 0x2B))
    font(par.add_run("诉求：" + need), size=8, color=RED_D, bold=True)
caption("表 4｜三类角色画像（化名，基于访谈原型合成）")

# =====================================================================
h1("03", "用户旅程与服务蓝图", "JOURNEY & BLUEPRINT")

h2("3.1 用户旅程：情绪最低点在“预约”和“现场”")
body("把 40 人研学团的一次完整经历拆成六个阶段，标注行为、触点、情绪、痛点与机会点。现状的情绪曲线在“预约”处跌到最低（反复确认餐位），在“现场”再次下滑（到点拍照就走、没有内容可做）。设计后的曲线把两处抬起：预约靠排程解决，现场靠“四个任务”解决。")
image(os.path.join(SHOTS, "d_journey.png"), 16.4)
caption("图 1｜用户旅程图（现状 vs 设计后）")

h2("3.2 服务蓝图：把“人做的事”写成“系统能接的事”")
body("蓝图分五列（预约前 / 预约中 / 行前 / 到场体验 / 离场之后）、五行（顾客行为、前台触点、前台人员、后台系统、支持流程），并补充日接待容量与失败点兜底。它回答一个具体问题：哪些环节必须由人完成，哪些可以交给系统？")
body("结论是：讲解、上餐、带做豆花必须由人完成；排班、锁位、名单校验、分账、证书签发可以交给系统。于是产品的边界清晰了——不替代人，只把人从“协调”里解放出来，去做“讲解”和“带做”。")
image(os.path.join(SHOTS, "d_blueprint.png"), 16.4)
caption("图 2｜服务蓝图（含日接待容量与失败点兜底）")

h2("3.3 三个关键时刻")
data_table(
    ["时刻", "用户在想什么", "设计上做了什么"],
    [
        ["排程结果页", "“40 个人到底能不能排下？”", "四项资源一次性列齐 + 一句人话建议（错峰 20 分钟）"],
        ["核销那一秒", "“我不会弄，别让我学。”", "一个大按钮，扫码或输后四位；成功后只显示“+¥1,260”"],
        ["证书生成", "“这个能不能交给学校？”", "一证一码、含里程与打卡数、可扫码核验"],
    ],
    widths=[3.2, 6.0, 7.4])
caption("表 5｜三个关键时刻的设计响应")

# =====================================================================
h1("04", "设计策略与概念", "STRATEGY")

h2("4.1 五条策略")
strategies = [
    ("把服务做成 SKU", "一个课程 = 讲解 + 红军餐 + 体验 + 场地 + 保险，价格与时长前置。把“要不要来”变成“买哪一个”。"),
    ("排程即产品", "四类资源实时比对，先给方案再让人填表。排程页不是后台报表，而是决策页。"),
    ("用轻动作带走重体验", "打卡、集章、证书三个轻动作，把 2 小时的“看”拉成 6.5 小时的“做”。"),
    ("让村民只做一件事", "核销。其余（派单、库存、分账）全自动。任何需要培训的功能都不做。"),
    ("把红色讲进土地里", "粮仓、稻田、豆花、盐厂都是可参与的教材；非遗（牛儿灯、山歌、拓印）作为“在地性”的入口。"),
]
for i, (t1, t2) in enumerate(strategies):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(1)
    par.paragraph_format.left_indent = Cm(0.0)
    font(par.add_run("S%d  " % (i + 1)), name=SERIF, size=10, bold=True, color=RED)
    font(par.add_run(t1 + "　"), size=9.8, bold=True, color=INK)
    font(par.add_run(t2), size=9.2, color=RGBColor(0x3B, 0x33, 0x2B))

h2("4.2 核心概念：「一日粮仓」")
body("学生要在一天里完成四件事——听一堂红军大学的情景课、从红军井打一桶水、在红军食堂吃一顿忆苦思甜餐、把 8 枚遗址印章集齐——最后拿到一张写着自己名字的证书。四件事对应四个“必须动手”的环节，把“参观”变成“完成”。")
data_table(
    ["时间", "环节", "在哪里", "做什么", "对应遗址 / 供给"],
    [
        ["09:00", "开营", "红军广场", "授旗、分队、发“粮仓任务卡”", "游客中心"],
        ["09:30", "情景课", "红军大学旧址（红岩村）", "讲“红军为什么能在天全筹到粮”", "红军大学旧址"],
        ["10:40", "打一桶水", "红军井（红军村）", "讲王定国挖井，学生分组打水、尝水", "红军井"],
        ["12:00", "忆苦思甜餐", "红军食堂（红军村）", "红薯饭、南瓜汤、炒盐菜，学生自己分餐", "4 家红军食堂"],
        ["14:00", "石磨豆花", "红军村 3 组", "推磨、滤浆、点卤，出锅佐红糖", "村民李婶"],
        ["15:30", "稻田课堂", "共和村 / 红军村田埂", "看稻渔综合种养：一亩田怎么从 4000 元到近万元", "稻渔示范区"],
        ["16:30", "结营颁证", "红军村游客中心", "集满 8 枚印章，生成电子证书并打印", "村集体"],
    ],
    widths=[1.7, 2.4, 4.2, 5.6, 3.6])
caption("表 6｜「一日粮仓」课程结构")

h2("4.3 命名与视觉方向")
body("产品名取“薪火”与“仁义”两词：薪火指代长征精神的传递，仁义既是镇名，也是这套服务的关系底色——村集体、村民、游客之间讲的是“仁义”。视觉上避开常见的“大红金五角星 + 展板风”，改为“赤壤红 + 稻田金 + 宣纸底”，用宋体做标题、细线做分隔、印章做等级符号，让界面更接近“一本田野笔记”，而不是“一个政务宣传页”。")

# =====================================================================
h1("05", "信息架构与核心流程", "IA & FLOW")

h2("5.1 四个一级入口")
body("把“预约”从 Tab 里拿掉，做成任何页面都能进入的流程（课程 → 日期 → 排程 → 支付）；Tab 只留四件事：看什么、在哪、什么时候去、我的东西。另设三个角色入口：游客、村民/商户、镇村管理员。")
image(os.path.join(SHOTS, "d_ia.png"), 16.4)
caption("图 3｜信息架构与三类角色")

h2("5.2 一条主线：从选日期到盖章核销")
image(os.path.join(SHOTS, "d_flow.png"), 16.4)
caption("图 4｜核心交互流程（3 条泳道 · 7 步 · 订单状态机）")

h2("5.3 核心交互的六个关键动作")
data_table(
    ["步骤", "用户动作", "系统响应", "设计要点"],
    [
        ["①", "在首页点“预约研学”", "进入课程详情，展示 6.5h / 3.2km / 8 处遗址", "先用数字回答“值不值”"],
        ["②", "选日期、加减人数", "已满日期置灰；人数变化即时改价", "把“能不能约上”前置"],
        ["③", "点“查排程”", "1.2 秒匹配四项资源，给错峰建议与车位预警", "给方案，不给报错"],
        ["④", "填联系人、勾协议、付订金", "生成订单号与核销码，锁定资源", "只问必需项"],
        ["⑤", "到场出示核销码", "讲解员扫码，订单转“已核销”，库存回写", "一单一次，防重复"],
        ["⑥", "在点位打卡、集满 8 枚", "生成一证一码的研学证书", "定位 + 核销双校验"],
    ],
    widths=[1.2, 4.6, 6.4, 4.4])

h2("5.4 关键规则（写进系统，不靠人记）")
data_table(
    ["规则", "取值", "为什么"],
    [
        ["起订人数", "20 人", "低于 20 人无法摊薄讲解与餐的成本"],
        ["单讲解员带队上限", "40 人，超出自动派第二人", "保证体验质量，也保护讲解员"],
        ["锁位时长", "30 分钟", "防止占位不下单，同时留出支付时间"],
        ["取消与改期", "行前 7 天免费取消；72 小时内改期限一次", "与学校报批节奏对齐"],
        ["打卡校验", "遗址 50m 内 + 当日核销记录", "防代打，保证证书真实"],
        ["分账比例", "农户 87% / 村集体 8% / 平台 5%", "让村集体有动力维护供给"],
    ],
    widths=[4.0, 7.2, 5.4])
caption("表 7｜关键业务规则")

# =====================================================================
h1("06", "界面与交互设计", "INTERFACE")

h2("6.1 设计语言")
data_table(
    ["要素", "设定", "说明"],
    [
        ["主色", "赤壤红 #A63A2E", "取自红砂岩与旧砖，避免鲜红造成的“展板感”"],
        ["辅色", "稻田金 #B8893F / 宣纸 #F7F2E8", "金色用于印章、等级与强调；纸色打底降低视觉疲劳"],
        ["语义色", "林绿 #3E5B45", "农耕与体验类点位、生态类标签"],
        ["标题字", "宋体（Songti / Source Han Serif）", "叙事性标题与价格、证书，建立“文本感”"],
        ["正文", "苹方 / 微软雅黑，13px 起", "保证中老年用户与户外强光下的可读性"],
        ["图形", "五角星（点位）、印章（集章）、等高线（地图）", "三套图形语言分工明确，不混用"],
        ["组件", "圆角 18 卡片、44px 胶囊按钮、底部吸底操作条", "手指触控区不小于 44×44"],
    ],
    widths=[2.6, 7.4, 7.0])
caption("表 8｜设计语言与组件规范")

h2("6.2 主要界面")
body("共设计 21 个界面（含 2 张地图交互态与 1 张搜索页），覆盖游客端全部主流程、供给端工作台与镇村运营看板。状态栏的时间与电量读的是设备真实状态（每 10 秒刷新，充电为绿色、低于 20% 转红），文档内静帧统一定格在 08:52 / 86%，与「09:00 集合」的行程场景对齐。地图不是一张静态插画：全图任何位置点击都有反馈——落在村庄热区内会选中该村并弹出卡片，落在空白处会给出提示；卡片可直接跳到该村的遗址列表或体验预约。预约页的日期、人数、加购三处都可改：改日期或人数后，排程结果、填写信息、凭证、行程、证书上的日期、人数、单价与总额会一起改写，不会出现“上面选了 21 号、下面还写 20 号”的情况。")

screens = [
    ("home.png", "01 首页", "一条主线 + 今日可约。“今日可约”把时段余量前置，避免填完表单才发现没饭。"),
    ("course.png", "02 课程详情", "把“一天怎么过”写成 7 个时间点，先卖确定感；费用包含逐条列清。"),
    ("book.png", "03 选择日期与人数", "已满日期置灰，并明示“5/20 是唯一能排下 40 人的日子”；人数步进即时改价。"),
    ("schedule.png", "04 智能排程", "四项资源实时比对 + 一句人话建议 + 车位预警，给方案而不是报错。"),
    ("confirm.png", "05 填写信息", "只问必需项（饮食、无障碍）；订金 20%，余款行前 3 天。"),
    ("success.png", "06 预约成功", "凭证 + 核销码 + 分享给班级群，把“下单”延伸到“组队完成”。"),
    ("trip.png", "07 行程", "时间轴 + 集合点导航 + 行前清单 + 一键联系讲解员。"),
    ("map.png", "08 红色地图", "手绘地形层：山梁等高线、林地、云顶梯田、田块、天全河与荷塘；7 个村庄用「村名 · 站点」标签标注，标签置于点位下方、不与顶部线路条打架，进入导航时线路条自动收起。全图可点，底部胶囊与星标联动。"),
    ("map2.png", "08b 地图 · 选择反馈", "点任一村庄：热区命中→涟漪→该村卡片（照片/遗址数/距离）→直达遗址或体验；可拖动、缩放、一键复位。"),
    ("map3.png", "08c 地图 · 路线导航", "从「你在这里」到目标村算一条路线：1.9km / 步行 26 分钟，蓝色路线带起终点、比例尺 600m 与指北针；「开始导航」让光标沿路线走，其余长征路线自动淡出。"),
    ("search.png", "08d 搜索 · 结果页", "首页与地图的搜索框都可输入：按遗址/体验/餐饮/住宿/课程分组实时过滤，命中词高亮；点结果直接进对应页面，没有结果的词给兜底建议并可直接去地图。"),
    ("poi.png", "09 点位详情（红军井）", "故事 + 语音讲解 + 50m 内打卡；播放条可点，进度走到 0:38，波形随进度变红。讲解音频是随包内置的示例人声（TTS 合成 1′25″），正式版替换为讲解员实录音频。"),
    ("stamps.png", "10 集章册", "8 枚印章 + 第 9 格“去打卡”，把缺口做成动作而不是空白。"),
    ("cert.png", "11 研学证书", "一证一码，写清里程、打卡数与签到记录，学校可扫码核验。"),
    ("exp.png", "12 在地体验", "8 个 SKU 分非遗 / 农事 / 讲解三类，非遗 3、农事 3、讲解 2；上方标签点了就筛，标题行同步显示“非遗 · 3 项”，筛选结果里每个条目仍可点开看时段、成团人数与价格。把非遗（牛儿灯）、文物（土司祠拓印）、农事（摸鱼、割稻、采莲）与讲解（深度讲解、情景课）做成可预约的 SKU。"),
    ("stay.png", "13 住在仁义", "民宿与红军食堂并列，标注可住/可就餐人数，方便团队决策。"),
    ("room.png", "14 房型与预订", "日历 + 房型 + 合计，吸底价格条随时可见。"),
    ("mine.png", "15 我的", "订单、集章册、证书三个资产入口；第二屏是“我是村民/商户”的身份切换。"),
    ("vendor.png", "16 村民工作台", "今日 3 单、待办、本月结算；分账逐项透明（服务费 5%、村集体 8%）。"),
    ("verify.png", "17 核销", "扫码或输订单后四位，一单一次；成功后只回显金额，不堆信息。"),
    ("dashboard.png", "18 运营看板", "冲突预警 + 客流趋势 + 资源利用率 + 村集体分成，面向镇村管理员。"),
]
two_col_screens(screens, 7.4)

h2("6.3 交互细节：三处“反直觉”的取舍")
body("① 排程放在填表之前。常规电商是“先填信息再校验库存”，这里反过来——因为团队研学最大的不确定性是“能不能约上”，而不是“填什么”。先给确定性，再要信息。")
body("② 集章册留一格空的。8 枚印章铺满会让人以为“已完成”；故意留第 9 格做“去打卡”按钮，把未完成状态变成一个可点击的入口。")
body("③ 核销成功页不显示详情。村民只需要知道“这单成了、多少钱”，多余信息会造成误触与困惑。")

# =====================================================================
h1("07", "后台服务逻辑", "BACKEND")

h2("7.1 四类资源的库存模型")
body("后台把“一次接待”拆成四类可占用的资源，每类资源有独立的日历与容量，订单在锁位时同时占用四者，任一不足即无法成单。")
data_table(
    ["资源", "粒度", "容量口径", "冲突策略"],
    [
        ["讲解员", "人 × 时段（半天）", "单团 ≤ 40 人；每人每天 ≤ 2 场", "在职 6 + 后备 3，冲突时自动派单后备"],
        ["红军餐", "食堂 × 餐段", "4 家共 620 位/日；单团 ≤ 300 位", "按 11:00 / 11:30 / 12:00 / 13:00 分餐段"],
        ["教学场地", "旧址 × 时段", "红军大学教室 60 人/场", "同日最多 2 场，间隔 30 分钟清场"],
        ["停车位", "车位 × 日", "大巴 2 + 小车 20", "大巴不足时给拼车与村口临时场方案"],
    ],
    widths=[2.6, 3.4, 5.4, 5.6])
caption("表 9｜资源与库存模型")

h2("7.2 排程逻辑：先匹配，再建议")
body("排程不是“查询余量”，而是“在四维约束下找一个可行解，并给出次优解”。规则按优先级依次执行：先满足人数与时段硬约束，再检查讲解员与场地，最后检查餐位与车位；若存在冲突，不直接报错，而是给出“错峰 20 分钟”“换讲解员”“改餐段”三种替代方案，并标注每种的代价（价格不变 / 需另付 / 需调整集合时间）。")
data_table(
    ["步骤", "判定", "输出"],
    [
        ["1 硬约束", "日期是否可售、人数是否在 20–200、是否超过单日承载", "不可行则直接给出最近的可选日期"],
        ["2 讲师匹配", "该时段是否有空闲讲解员；人数 ÷ 40 决定需要几人", "人选 + 是否需要第二讲解员"],
        ["3 场地匹配", "旧址教学场是否同日已满 2 场", "场次时间"],
        ["4 餐位匹配", "餐段余量 ≥ 人数", "餐段 + 食堂"],
        ["5 车位匹配", "大巴位是否足够", "车位方案（含拼车建议）"],
        ["6 生成方案", "汇总四项 + 冲突提示 + 错峰建议", "排程结果页"],
    ],
    widths=[2.4, 8.2, 6.0])
caption("表 10｜排程算法规则")

h2("7.3 核销、分账与证书")
body("核销是整条链路的“事实确认点”。讲解员或商户扫码后，系统做四件事：订单状态置为“已核销”、按实际人数回写餐位与讲解员占用、生成待分账流水、解锁该订单的打卡与证书权限。分账按“农户 87% / 村集体 8% / 平台 5%”自动拆分，每周一结算到账；村集体分成进入集体经济账户，用于遗址维护与公共设施。")
body("证书由村集体（红军村股份经济合作联合社）签发，编号规则为 XY-CERT-日期-流水，绑定订单号、核销记录与 8 条打卡记录；扫码可查“是否真实参与、完成了哪些点位”，但脱敏显示手机号。")

h2("7.4 运营看板与预警")
body("看板面向镇文旅办与村两委，提供四组信息：今日团队与客流、预约转化率、资源利用率、村集体分成。预警规则有三条：讲解员缺口（同日同时段需求 > 在职人数）、餐位峰值（11:30–12:30 超过 80% 容量）、民宿过夜需求超过 14 天内可售床位。每条预警都带一个可执行动作（派单、建议错峰、推荐邻近民宿），避免“只报数不解决”。")

# =====================================================================
h1("08", "验证与迭代", "TESTING")

h2("8.1 测试设计")
body("用可点击原型做了两轮走查：第一轮 5 名目标用户（3 名教师、1 名家长、1 名党建组织者），第二轮 2 名村委与 2 名食堂经营者。每轮设 4 个任务：①为一个 40 人班级约一天；②在地图上找到红军井并打卡；③生成证书；④以商户身份核销一单。记录完成率、耗时与卡点。")
data_table(
    ["任务", "v1 完成率", "v1 平均耗时", "v2 完成率", "v2 平均耗时"],
    [
        ["约一天（40 人）", "4/5", "96 秒", "5/5", "41 秒"],
        ["找点位并打卡", "3/5", "58 秒", "5/5", "26 秒"],
        ["生成证书", "5/5", "32 秒", "5/5", "19 秒"],
        ["商户核销", "3/5", "—", "5/5", "12 秒"],
    ],
    widths=[5.0, 2.8, 3.2, 2.8, 3.2])
caption("表 11｜两轮可用性走查结果（示例数据）")

h2("8.2 三处关键修改")
body("① “排程结果页”原来像后台报表（四行表格 + 状态灯），用户看不懂“可约/偏紧”。改为“四项资源卡片 + 一句人话建议 + 一个显眼的替代方案”，任务耗时从 96 秒降到 41 秒。")
body("② “村民端”原来藏在“我的 → 更多 → 商家服务”三级菜单，4 名走查者中 2 人找不到。改为“我的”第二屏首条，并在首页右上角给村民一个常驻提示，核销成功率从 60% 提升到 100%。")
body("③ 证书原来只有姓名与日期，教师反馈“看不出做了什么”。增加徒步里程、打卡点位数与核验二维码，并把签发单位写实（红军村股份经济合作联合社）。")

h2("8.3 未解决与下一步")
body("未解决项有三个：①地图首屏加载 2.4 秒（村域网络差），下一步做离线瓦片与点位降级；②方言语音讲解尚未覆盖全部 8 个点位，需与村史馆补录；③淡季（12–2 月）内容供给不足，计划用“冬修水利”“腊味制作”补充冬季线路。")

# =====================================================================
h1("09", "落地与运营", "OPERATION")

h2("9.1 冷启动三步")
data_table(
    ["阶段", "动作", "负责方", "验证指标"],
    [
        ["第 1 月", "录入 8 处遗址与 3 条课程，跑通“一日粮仓”一条线", "村集体 + 镇文旅办", "首月 10 单，全部走完核销"],
        ["第 2–3 月", "接入 4 家红军食堂与 2 家民宿；开放体验 SKU", "合作社 + 商户", "供给端 12 户上线，核销成功率 ≥ 95%"],
        ["第 4–6 月", "向全县学校与机关推广；开运营看板", "镇政府", "月均 25 单，复购 ≥ 10%"],
    ],
    widths=[2.4, 7.4, 3.6, 4.2])
caption("表 12｜冷启动路径")

h2("9.2 角色与职责")
data_table(
    ["角色", "职责", "在系统里做什么"],
    [
        ["镇文旅办", "内容审核、价格与安全规范、对外推广", "看板查看、内容发布审批"],
        ["村集体（合作社）", "排班、后备讲解员库、结算与分成", "维护资源日历、处理冲突预警"],
        ["村民 / 商户", "备餐、带体验、核销", "接单、核销、看结算"],
        ["讲解员", "讲解、带队、现场核销", "接派单、扫码核销"],
        ["学校 / 组织者", "组织、付费、行前管理", "下单、收行前包、分享"],
    ],
    widths=[3.2, 7.4, 5.4])

h2("9.3 指标与风险")
body("北极星指标设为“完成核销的团队数”（而非下单数），因为它同时代表收入、供给履约与体验发生。辅助指标：排程页转化率、行前 7 日取消率、证书领取率、复购率、农户人均增收。")
body("主要风险有三：①供给端履约不稳定（讲解员临时缺席）——用后备库 + 10 分钟自动改派兜底；②内容史实失真——讲解词由党校与村史馆双审，UGC 不进入讲解词；③过度商业化稀释红色教育属性——课程中商业环节（餐、住宿、体验）与教育环节分离标注，学校可只选教育包。")

# =====================================================================
h1("10", "交付说明", "DELIVERABLE")

h2("10.1 文件清单")
data_table(
    ["文件", "内容", "怎么用"],
    [
        ["薪火仁义-交互原型.html", "21 个界面的高保真可点击原型，含 4 条核心流程", "双击用浏览器打开；左侧是流程导航，可直接点手机界面操作；联网打开时自动切换为多设备同步"],
        ["设计图版.html", "旅程图、服务蓝图、信息架构、流程图、设计过程 5 张图版", "浏览器打开，地址后加 #journey / #blueprint / #ia / #flow / #process"],
        ["设计与交互说明.docx", "本文档：设计过程、界面与交互、后台逻辑、验证与落地", "答辩与评审阅读"],
        ["shots/", "全部界面与图版截图（PNG，2 倍图）", "可直接用于展板、PPT 与视频"],
        ["assets/img/", "界面用的 19 张照片（同名 JPEG），已内嵌进原型", "换图时按同名覆盖，再重新内嵌即可；建议替换为红军村实拍"],
        ["启动联机演示.cmd", "起本地服务，同一 Wi-Fi 多台手机共用一份余位", "双击运行，手机扫码进入；关窗口即停"],
        ["启动公网演示.cmd", "在上面基础上开一条公网隧道，跨网络也能访问", "双击运行，窗口里会打印公网地址与二维码"],
    ],
    widths=[4.4, 7.2, 5.0])
caption("表 13｜交付物清单")

h2("10.2 原型操作路径（评审 3 分钟版）")
body("① 打开原型 → 首页点“预约研学 ¥128 起” → 选 5/20、加到 40 人 → 点“查排程”，看四项资源如何被一次性匹配 → 点“用这个方案” → 支付订金（演示）→ 看凭证与核销码 → 切到“行程”看时间轴。")
body("② 回到“红色地图”→ 点“红军村”簇 → 选“红军井”→ 听语音 → 点“到此打卡”→ 集章册变为 8/8 → 点“生成证书”。")
body("③ 在“我的”→ “我是村民/商户”→ 村民工作台 → 点扫码核销 → 看本月结算与分账；再点“运营看板”看冲突预警与村集体分成。")

h2("10.3 联机演示：同一份余位，多台设备（可选）")
body("原型默认是单文件、零依赖的，双击就能用。为了让评委在答辩现场用几台手机同时下单、看余位一起变，另附了一个 tools/server.py：核心只用 Python 标准库，二维码用随附在 tools/pylibs 里的一个小库（已装好），不用额外装任何东西，起在 8787 端口。")
image(os.path.join(SHOTS, "join.png"), 12.4)
caption("联机演示的入口页：手机扫同一个码就进入同一份余位；右上角的在线人数由服务端按 6 秒内有请求的客户端统计。")
body("两种开法：双击「启动联机演示.cmd」，同一 Wi-Fi 或热点下扫码即可；双击「启动公网演示.cmd」，脚本会再开一条 ssh 反向隧道，拿到形如 https://xxxx.lhr.life 的公网地址并自动打开扫码页——不在同一个网络里的手机也能进。")
body("同步机制：客户端每 1.5 秒拉一次 /api/state；下单走 POST /api/order，服务端按天扣减餐位，排不下就直接驳回并告诉用户还剩几位。已实测：两台设备先后各下 40 人，第二台被拦在“手慢了，这档只剩 20 位”；从外部网络访问公网地址，拿到的是同一份余位数据。")
body("和正式版的差别要说清楚：这是演示用的内存态服务，重启即清零；真小程序会把轮询换成 WebSocket 或云函数推送，余位以数据库事务为准，防超卖靠行级锁而不是先读后写。")

p("资料出处：①天全县民政局《天全地名故事录（五十一）仁义镇》；②雅安市人民政府网《红色粮仓的新“稻”路——天全红军村蹲点记》；③天全文明网《四川省非物质文化遗产——牛儿灯》；④行政区划网《天全县（2023 年）》《名山区（2023 年）》；⑤中国新闻网《长征胜利 90 周年·四川天全红军村的变迁》。",
  size=7.6, color=INK3, before=10, after=0, line=1.55)

page_number_footer()

out = os.path.join(ROOT, "薪火仁义-设计说明书.docx")
doc.save(out)
print("saved:", out, os.path.getsize(out))

















