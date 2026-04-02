from __future__ import annotations

import json
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Iterable


IMAGE_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")
TITLE_RE = re.compile(r"^(.*?)（(.*?)）$")
DOI_RE = re.compile(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)

METHOD_KEYWORDS = (
    "路线",
    "总览",
    "总图",
    "框架",
    "alignment",
    "取向",
    "合成",
    "synthesis",
    "program",
    "编程",
    "printing",
    "DIW",
)
RESULT_KEYWORDS = (
    "对比",
    "strain",
    "打印",
    "应用",
    "机器人",
    "medical",
    "biomedical",
    "功能",
    "差异",
    "结果",
)

RATING_DIMS = [
    ("novelty", "创新性"),
    ("rigor", "严谨性"),
    ("practicality", "实用性"),
    ("clarity", "清晰度"),
    ("impact", "影响力"),
]

RATING_OVERRIDES = {
    "liquid-crystal-elastomers-an-introduction-and-review-of-emerging-technologies": {
        "novelty": {
            "score": 3,
            "justification": "作为导论型综述，它的创新主要在于把基础物理、合成路线与应用趋势串成清晰路线图，而不是提出全新材料机理。",
        },
        "rigor": {
            "score": 4,
            "justification": "文章对关键 chemistry、programming 与应用案例的证据链组织扎实，但跨路线定量 benchmark 仍较少。",
        },
        "practicality": {
            "score": 4,
            "justification": "它对 bulk synthesis、post-programming 和应用约束的讨论具体，能直接帮助研究者做路线选择。",
        },
        "clarity": {
            "score": 5,
            "justification": "结构和图示都很清楚，作为进入 LCE 领域的综述读物可读性很强。",
        },
        "impact": {
            "score": 4,
            "justification": "这篇综述为 LCE 从实验现象走向工程平台提供了明确导航，对后续研究方向有持续影响。",
        },
    },
    "synthesis-and-alignment-of-liquid-crystalline-elastomers": {
        "novelty": {
            "score": 4,
            "justification": "它把 mechanics、chemistry 与 alignment route 纳入统一设计框架，综合视角明显强于一般文献盘点。",
        },
        "rigor": {
            "score": 5,
            "justification": "对 LCE 与 LCN 差异、四类取向路线和代表性 chemistry 的论证完整且证据组织严密。",
        },
        "practicality": {
            "score": 5,
            "justification": "文章直接回应厚样品、图案分辨率、打印与重编程等工程问题，方法边界非常可操作。",
        },
        "clarity": {
            "score": 5,
            "justification": "图示和叙事结构都极其清晰，读者很容易把材料选择、取向工艺和器件目标对应起来。",
        },
        "impact": {
            "score": 5,
            "justification": "作为路线型高水平综述，它对理解和规划当前 LCE 研究方向具有很强的引导作用。",
        },
    },
}

GLOSSARY_TERMS = [
    ("Fréedericksz 转变", "液晶在外场超过阈值后整体重新取向的经典失稳过程。"),
    ("dynamic covalent network", "能在保持交联网络连通的同时发生键交换、实现重编程的共价网络。"),
    ("covalent adaptable network", "通过可逆键交换实现重写、焊接或自修复的动态交联网络。"),
    ("surface-enforced alignment", "利用表面锚定或配向层把液晶取向写入材料表面的对齐方法。"),
    ("field-assisted alignment", "利用电场或磁场强制液晶分子重排并实现体积取向的方法。"),
    ("rheological alignment", "利用流动与剪切把液晶取向直接写入材料或打印路径的方法。"),
    ("hydrosilylation", "硅氢键与双键加成的反应，是传统 LCE 合成常用路线。"),
    ("transesterification", "酯交换反应，可在热或催化条件下重排网络并实现重编程。"),
    ("thiol-Michael", "巯基对活化双键进行亲核加成的温和 click 反应，常用于 LCE 分阶段构筑。"),
    ("aza-Michael", "胺基对活化双键进行亲核加成的反应，可用于构建主链或网络结构。"),
    ("order parameter", "衡量液晶分子取向一致程度的量，数值越高表示取向越整齐。"),
    ("actuation strain", "材料在刺激下产生的可逆形变量，用于衡量致动幅度。"),
    ("soft elasticity", "director 重排时出现的低增量应力大变形响应，是 LCE 的典型特征。"),
    ("Frank 自由弹性能", "描述液晶 splay、twist、bend 畸变代价的连续体弹性能。"),
    ("Gay-Berne", "描述各向异性椭球分子相互作用的经典势函数。"),
    ("director", "液晶分子平均取向所定义的方向轴。"),
    ("monodomain", "液晶取向在样品内基本一致的单畴状态。"),
    ("polydomain", "样品内部存在多个取向区域的多畴状态。"),
    ("DIW", "direct ink writing 的缩写，通过挤出墨水同时成形并写入取向。"),
    ("RAFT", "可逆加成-断裂链转移机理，可用于聚合调控或网络重排。"),
    ("SmA", "smectic A 的缩写，表示分子长轴平均垂直于层面的层状液晶相。"),
    ("SmC", "smectic C 的缩写，表示分子长轴相对层法向发生倾斜的层状液晶相。"),
]


@dataclass
class Subsection:
    title: str
    lines: list[str] = field(default_factory=list)


@dataclass
class Section:
    title: str
    lines: list[str] = field(default_factory=list)
    subsections: list[Subsection] = field(default_factory=list)


@dataclass
class VisualItem:
    title: str
    alt: str
    path: str
    detail: str


@dataclass
class Metadata:
    title_zh: str
    title_en: str
    venue: str
    authors: list[str]
    affiliations: list[str]
    date_text: str
    year: str
    header_image: str


@dataclass
class BundleSummary:
    metadata: Metadata
    sections: OrderedDict[str, Section]
    body_lines: list[str]
    visuals: list[VisualItem]
    formulas: list[VisualItem]


class TermMarker:
    def __init__(self, max_terms: int = 10) -> None:
        self.max_terms = max_terms
        self._used: set[str] = set()

    def apply(self, text: str) -> str:
        marked = escape(text)
        for term, definition in sorted(GLOSSARY_TERMS, key=lambda item: len(item[0]), reverse=True):
            if len(self._used) >= self.max_terms:
                break
            if term in self._used:
                continue
            escaped_term = escape(term)
            if escaped_term not in marked:
                continue
            replacement = (
                f'<span class="term" data-def="{escape(definition, quote=True)}">{escaped_term}</span>'
            )
            marked = marked.replace(escaped_term, replacement, 1)
            self._used.add(term)
        return marked


def parse_image(line: str) -> tuple[str, str] | None:
    match = IMAGE_RE.fullmatch(line.strip())
    if not match:
        return None
    return match.group(1).strip(), match.group(2).strip()


def split_title(title_line: str) -> tuple[str, str]:
    match = TITLE_RE.match(title_line.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return title_line.strip(), ""


def parse_metadata(lines: list[str]) -> tuple[Metadata, int]:
    title_zh = ""
    title_en = ""
    venue = ""
    authors: list[str] = []
    affiliations: list[str] = []
    date_text = ""
    header_image = ""
    body_start_index = 0

    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if line.startswith("- 论文标题："):
            value = line.split("：", 1)[1].strip()
            title_zh, title_en = split_title(value)
        elif line.startswith("- 期刊名："):
            venue = line.split("：", 1)[1].strip()
        elif line.startswith("- 作者与单位："):
            value = line.split("：", 1)[1].strip()
            if "；" in value:
                authors_part, affiliation_part = value.split("；", 1)
            elif ";" in value:
                authors_part, affiliation_part = value.split(";", 1)
            else:
                authors_part, affiliation_part = value, ""
            authors = [item.strip() for item in authors_part.split(",") if item.strip()]
            affiliations = [affiliation_part.strip()] if affiliation_part.strip() else []
        elif line.startswith("- 文献基本信息："):
            date_text = line.split("：", 1)[1].strip()
        else:
            parsed_image = parse_image(line)
            if parsed_image:
                header_image = parsed_image[1]
                body_start_index = index + 1
                break

    year_match = re.search(r"(19|20)\d{2}", date_text)
    year = year_match.group(0) if year_match else ""
    metadata = Metadata(
        title_zh=title_zh,
        title_en=title_en,
        venue=venue,
        authors=authors,
        affiliations=affiliations,
        date_text=date_text,
        year=year,
        header_image=header_image,
    )
    return metadata, body_start_index


def parse_sections(lines: list[str]) -> OrderedDict[str, Section]:
    sections: OrderedDict[str, Section] = OrderedDict()
    current_section: Section | None = None
    current_subsection: Subsection | None = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if stripped.startswith("## "):
            current_section = Section(title=stripped[3:].strip())
            sections[current_section.title] = current_section
            current_subsection = None
            continue
        if stripped.startswith("### ") and current_section is not None:
            current_subsection = Subsection(title=stripped[4:].strip())
            current_section.subsections.append(current_subsection)
            continue
        if current_section is None:
            continue
        if current_subsection is not None:
            current_subsection.lines.append(line)
        else:
            current_section.lines.append(line)


    return sections


def find_section(sections: OrderedDict[str, Section], keyword: str) -> Section | None:
    for title, section in sections.items():
        if keyword in title:
            return section
    return None


def extract_bullets(lines: Iterable[str]) -> list[str]:
    return [line.strip()[2:].strip() for line in lines if line.strip().startswith("- ")]


def extract_paragraphs(lines: Iterable[str]) -> list[str]:
    paragraphs: list[str] = []
    buffer: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if buffer:
                paragraphs.append(" ".join(buffer).strip())
                buffer = []
            continue
        if line.startswith("- ") or parse_image(line):
            if buffer:
                paragraphs.append(" ".join(buffer).strip())
                buffer = []
            continue
        buffer.append(line)
    if buffer:
        paragraphs.append(" ".join(buffer).strip())
    return paragraphs


def extract_visuals(section: Section | None) -> list[VisualItem]:
    if section is None:
        return []

    visuals: list[VisualItem] = []
    for subsection in section.subsections:
        image_alt = ""
        image_path = ""
        body_lines: list[str] = []
        for line in subsection.lines:
            parsed_image = parse_image(line.strip())
            if parsed_image:
                image_alt, image_path = parsed_image
            else:
                body_lines.append(line)
        if image_path:
            detail = " ".join(extract_paragraphs(body_lines)).strip()
            visuals.append(
                VisualItem(
                    title=subsection.title,
                    alt=image_alt or subsection.title,
                    path=image_path,
                    detail=detail or subsection.title,
                )
            )
    return visuals


def load_bundle_summary(bundle_dir: Path) -> BundleSummary:
    lines = (bundle_dir / "summary.md").read_text(encoding="utf-8").splitlines()
    metadata, body_start = parse_metadata(lines)
    body_lines = lines[body_start:]
    sections = parse_sections(body_lines)
    visuals = extract_visuals(find_section(sections, "5.1"))
    formulas = extract_visuals(find_section(sections, "5.3"))
    return BundleSummary(
        metadata=metadata,
        sections=sections,
        body_lines=body_lines,
        visuals=visuals,
        formulas=formulas,
    )


def default_ratings(summary: BundleSummary, slug: str) -> dict:
    if slug in RATING_OVERRIDES:
        return RATING_OVERRIDES[slug]

    is_review = "综述" in summary.metadata.title_zh or "review" in summary.metadata.title_en.lower()
    novelty_score = 3 if is_review else 4
    impact_score = 4 if is_review else 3
    return {
        "novelty": {
            "score": novelty_score,
            "justification": "文章的主要价值在于整合已有工作并给出清晰框架，创新性更多体现在视角与组织方式上。",
        },
        "rigor": {
            "score": 4,
            "justification": "摘要中的论证结构完整，能把研究问题、方法与证据链较好地对应起来。",
        },
        "practicality": {
            "score": 4,
            "justification": "文中对方法边界和应用条件有较明确讨论，具备一定的直接参考价值。",
        },
        "clarity": {
            "score": 4,
            "justification": "摘要结构清楚、图示丰富，整体可读性较好。",
        },
        "impact": {
            "score": impact_score,
            "justification": "这篇论文对相关研究方向具有稳定参考价值，但影响力仍取决于具体领域背景。",
        },
    }


def update_report_json(bundle_dir: Path, summary: BundleSummary) -> dict:
    report_path = bundle_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    slug = report.get("paper_slug", bundle_dir.name)
    report["paper_slug"] = slug
    report["paper_title"] = summary.metadata.title_zh
    report["paper_title_en"] = summary.metadata.title_en
    report["venue"] = summary.metadata.venue
    report["authors"] = summary.metadata.authors
    report["affiliations"] = summary.metadata.affiliations
    report["date"] = summary.metadata.date_text
    if "ratings" not in report:
        report["ratings"] = default_ratings(summary, slug)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def parse_rating_score(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(value, 0)
    if isinstance(value, float):
        return max(int(value), 0)
    text = str(value).strip()
    if not text:
        return 0
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        return max(int(digits), 0)
    return 0


def ten_point_score(score: object) -> str:
    bounded = min(parse_rating_score(score), 5)
    return f"{bounded * 2}/10"


def pick_visual(visuals: list[VisualItem], keywords: tuple[str, ...], used: set[str]) -> VisualItem | None:
    for visual in visuals:
        haystack = f"{visual.title} {visual.detail}".lower()
        if visual.path in used:
            continue
        if any(keyword.lower() in haystack for keyword in keywords):
            used.add(visual.path)
            return visual
    for visual in visuals:
        if visual.path not in used:
            used.add(visual.path)
            return visual
    return None


def pick_key_visuals(visuals: list[VisualItem], used: set[str], limit: int = 3) -> list[VisualItem]:
    selected: list[VisualItem] = []
    for visual in visuals:
        if visual.path in used:
            continue
        selected.append(visual)
        used.add(visual.path)
        if len(selected) == limit:
            break
    return selected


def split_markdown_blocks(summary_text: str) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in summary_text.splitlines():
        if line.strip():
            current.append(line.rstrip())
            continue
        if current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def clean_inline_markdown(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"[*_`]+", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def extract_doi(text: str) -> str:
    match = DOI_RE.search(text)
    return match.group(1) if match else ""


def build_meta_badges(metadata: Metadata) -> list[str]:
    badges = [metadata.venue] if metadata.venue else []
    doi = extract_doi(metadata.date_text)
    if doi:
        badges.append(f"DOI {doi}")
    return badges
