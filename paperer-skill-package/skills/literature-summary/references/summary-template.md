# Literature Summary Template

Use this file for the final `summary.md` structure.

The headings must be localized to `target_language`. The Chinese labels below define the section logic, not a requirement to keep Chinese in non-Chinese output.

## Writing standard

- Write as a polished research brief, not as fragmented notes.
- Prefer short paragraphs over bullet dumps where explanation matters.
- Keep a stable heading hierarchy.
- Use evidence anchors mainly in technical sections.
- Avoid ratings. Make judgment in prose.
- When extraction is partial, keep the document polished and mark missing support clearly.
- Keep the prose focused on the paper itself. Do not discuss extraction strategy, crop quality, or other workflow-side details inside `summary.md`.
- Every header image, figure, table, and formula that exists in the bundle must be embedded visibly inside `summary.md`.
- The displayed page title must always be the Chinese translation of the paper's English title, even when the body follows another `target_language`.
- In `1.3 核心结论速览`, allow multiple problem / method / result / contribution points when the paper clearly contains more than one.
- Treat the section bullets below as compact writing prompts: cover each point directly, but answer in polished prose rather than checklist fragments.

## Recommended structure

### Page Title

Include:

- use the Chinese translation of the paper's English title as the displayed page title, regardless of `target_language`
- keep the original English paper title in the metadata block beneath it
- venue or journal
- authors and affiliations
- basic citation metadata
- header screenshot covering title, venue, authors, and affiliations

The header screenshot must be embedded directly in the Markdown, not only described in text.

### 1. 论文概览

#### 1.1 论文定位

- State in one sentence what this paper studies.
- Clarify which problem area it belongs to and what class of core problem it addresses.

#### 1.2 这篇论文为什么值得关注

- Explain what key question this paper is trying to answer.
- Explain where its potential value lies relative to prior work.
- Explain why this paper is worth reading beyond the abstract.

#### 1.3 核心结论速览

- Problem: describe the paper's core problem in a few natural sentences, not as a keyword list.
- Method: describe the main method or strategy in a few natural sentences, not as a keyword list.
- Results: describe the main results in a few natural sentences, not as a keyword list.
- Contribution: describe the supported contribution in a few natural sentences, not as a keyword list.
- If any of these four areas contains multiple important points, cover them fully instead of compressing them into a single point for neatness.

### 2. 研究问题与动机

#### 2.1 背景与痛点

- Explain the research background.
- Explain the main limitations of existing methods.
- Explain why the authors see this problem as worth solving.

#### 2.2 研究问题

- State clearly what problem the paper is trying to solve.
- Clarify the boundary conditions and intended application setting.
- If the paper relies on assumptions or constraints, state them explicitly.

#### 2.3 作者的研究目标

- Explain what the authors are trying to achieve.
- Explain what counts as success in the paper's own logic.

### 3. 方法与创新

#### 3.1 整体方法框架

- Explain the method as a coherent mechanism rather than a pile of terms.
- State the inputs, the core mechanism, and the outputs.
- Add a brief process explanation when it helps comprehension.

#### 3.2 核心创新点

- Extract the 1-3 most important innovations.
- For each one, explain what is new and why it matters.

#### 3.3 方法为什么可能有效

- Explain at the mechanism level why the method could solve the stated problem.
- If the paper provides theoretical motivation or design intuition, absorb it into the explanation.

### 4. 实验设计与证据

#### 4.1 实验设置

- State the datasets, tasks, and comparison baselines.
- State the evaluation metrics.
- Point out the most important part of the experimental setup.

#### 4.2 关键结果

- Extract the most important results.
- Explain which results genuinely support the central claims.
- Start using page, figure, table, or equation anchors here when helpful.

#### 4.3 证据是否充分

- Judge whether the results actually support the conclusions.
- Point out which evidence is especially strong.
- Point out where the argument remains incomplete or weak.

### 5. 图表与公式解读

#### 5.1 图片解读

- Embed each figure first, then explain it in complete sentences.
- Explain what the figure is, what can be observed from it, and what role it plays in the paper's chain of argument.
- Do not merely restate the caption or describe the picture surface.

#### 5.2 表格解读

- Embed each table first, then explain it in complete sentences.
- State the comparison target, the key metrics, and the most notable results.
- Do not copy the table row by row; explain what the table means.

#### 5.3 公式解读

- Embed each core formula first, then explain it in complete sentences.
- Explain what the formula does instead of merely rewriting symbols.
- If there are many formulas, prioritize the core ones and explain their variable meaning when needed.
- If a formula cannot be explained reliably from the paper, mark that clearly and do not force an interpretation.

Do not summarize extraction problems here. If the bundle has extraction uncertainty, keep that in `report.json` unless it materially changes what the paper itself can support.

### 6. 作者真正完成了什么

#### 6.1 论文的实际贡献

- Explain what this paper actually accomplished.
- Explain whether it introduces a new method, provides new evidence, or reframes the problem.
- Distinguish between what the authors claim and what the paper genuinely supports.

#### 6.2 这项工作的价值判断

- Explain where the academic or practical value of the work lies.
- Explain which readers are most likely to benefit from it.
- Keep the judgment analytical and in prose; do not use ratings.

### 7. 局限性与讨论

#### 7.1 论文的不足

- Analyze method-level limitations.
- Analyze experiment-level limitations.
- Analyze scope and applicability limitations.
- You may include both author-acknowledged limitations and additional paper-supported weaknesses you identify.

#### 7.2 可以进一步追问的问题

- Point out which key questions remain unanswered.
- Point out which assumptions or settings may limit generalization.
- Point out promising directions for follow-up research.

### 8. 总结与启示

#### 8.1 这篇论文意味着什么

- Explain what this paper means for the field or research direction.
- Explain what it means for research practice or application.

#### 8.2 一句话总结

- Close with one natural, precise, and defensible sentence.

## Tone guide

Target tone:

- professional
- academic
- concise
- confident only where supported

Avoid:

- checklist-like phrasing
- filler translation
- exaggerated praise
- unsupported certainty
- commentary about your own extraction or rendering process
