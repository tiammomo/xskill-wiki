"""Responsive, bilingual visual explanations for the static reference."""

def render_visuals(b):
    def head(number, en, zh, note_en, note_zh):
        return f'<header class="visual-head"><span class="visual-number">{number}</span><div><h3>{b(en, zh)}</h3><p>{b(note_en, note_zh)}</p></div></header>'

    moments = [
        ('01', 'goal-a', 'Timeout investigation', '排查超时', '“Fix the order API timeout.”', '“帮我解决订单接口超时。”', 'Raise the timeout; validation still fails.', '先调大超时阈值，验证仍然失败。', 'Task A · Attempt 1', 'Task A · 第一次尝试', 'The failed approach remains part of the record.', '这次失败会留下来，不会被后来的成功覆盖。'),
        ('02', 'goal-a', 'Change the approach', '换一种办法', '“Check the connection pool instead.”', '“换个方向，查一下连接池。”', 'The goal stays the same; the user corrects the method.', '目标没变，用户纠正了处理方法。', 'Task A · Attempt 2', 'Task A · 纠正后的尝试', 'A confirmed correction starts a new Attempt and records correction_of.', '确认是方法纠正后，新建 Attempt，并记录 correction_of。'),
        ('03', 'goal-b', 'A different request', '插入另一件事', '“Translate this paragraph first.”', '“先帮我翻译这段说明。”', 'Translation serves a separate goal.', '翻译有自己的交付目标。', 'Task B · its own Attempt', 'Task B · 独立尝试', 'Sharing a session does not make these two goals one task.', '即使在同一会话里，也不把翻译并入接口排障。'),
        ('04', 'goal-a', 'Return to the issue', '回到原来的问题', '“Back to the connection pool.”', '“继续刚才的连接池问题。”', 'Resume Task A when the evidence confirms the link.', '证据确认后，回到 Task A。', 'Task A · check continuity', 'Task A · 另判执行连续性', 'A stable run identity may support Attempt 2. Without enough evidence, keep a new Attempt and a proposed continuation.', '稳定运行身份可能支持沿用 Attempt 2；证据不足时保留新 Attempt 和待确认的继续关系。'),
    ]
    timeline = head('01', 'One conversation, two goals', '一段对话，两件事', 'Read down the timeline. Color follows the goal, not the message order.', '顺着时间往下看。颜色跟着目标走，话题切回来时，目标身份仍可延续。')
    timeline += '<ol class="story-timeline">'
    for n, cls, en, zh, qe, qz, de, dz, te, tz, xe, xz in moments:
        timeline += f'<li class="{cls}"><span class="story-dot">{n}</span><div class="story-card"><div class="story-top"><strong>{b(en,zh)}</strong><span class="goal-tag">{b(te,tz)}</span></div><p class="story-quote">{b(qe,qz)}</p><p>{b(de,dz)}</p><details><summary>{b("Why this grouping?", "为什么这样分？")}</summary><p>{b(xe,xz)}</p></details></div></li>'
    timeline += '</ol><p class="visual-footnote">' + b('Illustrative grouping: goal links and correction signals are assumed confirmed. A return to a goal does not by itself prove the same execution continued.', '示例假设目标关联与纠正信号已获确认。回到同一个目标，并不单独证明仍是同一次执行。') + '</p>'

    decision = head('02', 'Same goal. Same execution?', '目标一样，还是同一次执行吗？', 'Check goal ownership first, then examine the execution evidence.', '先确认属于哪个 Task，再看这次执行与之前是什么关系。')
    decision += '<div class="decision-entry">' + b('Starting point: evidence already belongs to a confirmed Task', '起点：这段证据已有确认的 Task 归属') + '</div><div class="decision-grid">'
    branches = [
        ('↻', 'A retry or correction', '明确重试或纠正', 'Create a new Attempt', '新建 Attempt', 'Keep retry_of or correction_of, so the earlier attempt stays traceable.', '用 retry_of 或 correction_of 连回之前的尝试，保留失败和改法的经过。'),
        ('→', 'Evidence of continuity', '有执行连续性证据', 'May keep the same Attempt', '可以沿用 Attempt', 'Consider original adjacency, a stable run identity and confirmed history together.', '结合原始相邻关系、稳定运行身份及已确认历史一起判断。'),
        ('?', 'Continuity is unclear', '还不能确定是否连续', 'Keep a separate Attempt', '先保留独立 Attempt', 'Retain a proposed continuation instead of silently combining executions.', '保留待确认的 continuation_of，等证据足够再确认关系。'),
    ]
    for symbol,en,zh,re,rz,de,dz in branches:
        decision += f'<div class="decision-card"><span class="decision-symbol" aria-hidden="true">{symbol}</span><h4>{b(en,zh)}</h4><p class="decision-result">{b(re,rz)}</p><p>{b(de,dz)}</p></div>'
    decision += '</div><p class="visual-footnote">' + b('This is a reading guide, not a complete decision algorithm. Confirmed historical boundaries still take precedence; a shared Task alone is not continuity evidence.', '这是帮助理解的判断概览。实际分组还要遵守已确认的历史边界；属于同一 Task 本身不构成执行连续性证据。') + '</p>'

    usage = head('04', 'Where the 101 Tokens go', '101 个 Token，最后分到哪里？', 'Worked example · two Attempts · weights 3:2 · no unattributed balance', '算例 · 两次尝试 · 权重 3:2 · 没有未归因余额')
    usage += '<div class="allocation-equation"><div><span class="allocation-total">101</span><span>Token</span></div><span aria-hidden="true">→</span><div><strong>61 + 40</strong><span>' + b('The total stays 101', '合计仍是 101') + '</span></div></div>'
    usage += '<div class="allocation-bar" role="img" aria-label="Attempt A: 61 Tokens; Attempt B: 40 Tokens; total: 101"><span class="allocation-a">A · 61</span><span class="allocation-b">B · 40</span></div>'
    usage += '<div class="allocation-legend"><span><i class="swatch-a" aria-hidden="true"></i>Attempt A · 61 Token</span><span><i class="swatch-b" aria-hidden="true"></i>Attempt B · 40 Token</span></div>'
    usage += '<ol class="allocation-steps">'
    for en,zh,value in [('Proportional shares','先按比例算','60.6 / 40.4'),('Round down','取整数部分','60 / 40'),('Give A the remaining Token','余下 1 个给 A','61 / 40')]:
        usage += '<li><span>'+b(en,zh)+'</span><strong>'+value+'</strong></li>'
    usage += '</ol><p class="visual-footnote">' + b('The bar shows allocated shares, not measured usage per Attempt. The formulas below explain the calculation and its boundaries.', '条形图展示分摊结果，并非逐次执行的实测用量。下面的公式说明算法与适用范围。') + '</p>'

    outcome = head('03', '“Finished” answers only one question', '“执行结束”只回答了一个问题', 'Example: the tool reports success, but verification and user acceptance are still missing.', '例如：工具报告成功，但还没有核验证据，也没有用户验收。')
    outcome += '<div class="outcome-grid">'
    for en,zh,ve,vz,de,dz in [
        ('Lifecycle','执行状态','Ended','已结束','The run has stopped.','这次运行已经停止。'),
        ('Reported result','来源报告','Success','成功','This is the tool’s report.','这是工具给出的结论。'),
        ('Verification','目标核验','Unverified','未验证','Supporting checks are missing.','还缺少对应目标的核验证据。'),
        ('User feedback','用户反馈','Unknown','未知','No acceptance has been recorded.','还没有收到用户确认。')]:
        outcome += '<div><span class="outcome-label">'+b(en,zh)+'</span><strong>'+b(ve,vz)+'</strong><p>'+b(de,dz)+'</p></div>'
    outcome += '</div><p class="visual-footnote">' + b('These states describe different facts. Do not turn a reported success into verified completion of every goal in the session.', '四项记录分别回答不同问题。不能因为来源报告成功，就把会话里的所有目标都标为已验证完成。') + '</p>'
    return {key: f'<figure class="explain-visual">{value}</figure>' for key,value in [('example',timeline),('attempts',decision),('usage',usage),('outcomes',outcome)]}
