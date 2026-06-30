#!/usr/bin/env python3
"""
报价比对脚本 — 将厂商报价与招标需求逐项比对，生成参数偏离表。

用法:
    python3 compare_quotation.py requirements.json quotation.xlsx [--vendor 厂商名]

输入:
    requirements.json  — parse_hardware.py 输出的结构化需求
    quotation.xlsx     — 厂商报价文件

输出: JSON 格式偏离比对结果
{
  "vendor": "威努特",
  "comparisons": [...],
  "summary": {
    "meets": 9, "positive_deviation": 4,
    "negative_deviation": 0, "cannot_determine": 2,
    "comparable_total": 629021
  },
  "risk_items": [...]
}
"""

import json
import sys
import os
import re
from pathlib import Path


def extract_number(text):
    """从文本中提取第一个数字"""
    m = re.search(r'(\d+[\.,]?\d*)', str(text))
    return float(m.group(1).replace(',', '')) if m else None


def extract_unit(text, unit_keywords):
    """从文本中提取带单位的数值，如 '吞吐≥20G' → 20, 'G'"""
    for uk in unit_keywords:
        pattern = rf'(\d+[\.,]?\d*)\s*{uk}'
        m = re.search(pattern, str(text), re.I)
        if m:
            return float(m.group(1).replace(',', '')), uk
    return None, None


def compare_specs(req_spec, quote_spec, spec_type):
    """逐项比对关键参数

    返回: (verdict, deviation_detail)
    verdict 类型: 'meet', 'positive', 'negative', 'unclear'
    """
    issues = []
    positive = []
    negative = []

    # --- CPU 核数比对 ---
    req_cpu_cores = None
    for pat in [r'(?:≥|>=|不低于)\s*(\d+)\s*(?:核|Core|C)', r'(\d+)\s*(?:核|Core|C)\s*(?:CPU|处理器)']:
        m = re.search(pat, req_spec)
        if m:
            req_cpu_cores = int(m.group(1))
            break
    if not req_cpu_cores:
        m = re.search(r'(?:CPU|处理器).*?(\d+)\s*(?:核|Core|C)', req_spec)
        if m: req_cpu_cores = int(m.group(1))

    quote_cpu_match = re.search(r'(\d+)\s*(?:核|Core|C)', quote_spec)
    quote_cpu_cores = int(quote_cpu_match.group(1)) if quote_cpu_match else None

    if req_cpu_cores and quote_cpu_cores:
        if quote_cpu_cores >= req_cpu_cores:
            if quote_cpu_cores > req_cpu_cores * 1.3:
                positive.append(f'CPU核数({quote_cpu_cores}核>{req_cpu_cores}核)')
            else:
                issues.append(f'CPU核数({quote_cpu_cores}核≥{req_cpu_cores}核)')
        else:
            negative.append(f'⚠ CPU核数不足({quote_cpu_cores}核<{req_cpu_cores}核)')

    # --- 内存比对 ---
    req_mem = None
    for pat in [r'(?:≥|>=|不低于)\s*(\d+)\s*GB?\s*(?:内存|DDR|ECC)',
                r'内存\s*(?:≥|>=)\s*(\d+)\s*GB?',
                r'(\d+)\s*GB?\s*(?:内存)']:
        m = re.search(pat, req_spec, re.I)
        if m:
            req_mem = int(m.group(1))
            break
    # Also try to extract from "16×32GB" pattern
    if not req_mem:
        m = re.search(r'(\d+)\s*[×x]\s*(\d+)\s*GB?\s*(?:DDR|ECC|内存)', req_spec, re.I)
        if m: req_mem = int(m.group(1)) * int(m.group(2))

    quote_mem = None
    for pat in [r'(\d+)\s*GB?\s*(?:DDR|ECC|内存)', r'内存\s*(?:≥|=)\s*(\d+)\s*GB?']:
        m = re.search(pat, quote_spec, re.I)
        if m:
            quote_mem = int(m.group(1))
            break
    if not quote_mem:
        m = re.search(r'(\d+)\s*[×x]\s*(\d+)\s*GB?\s*(?:DDR|ECC|内存)', quote_spec, re.I)
        if m: quote_mem = int(m.group(1)) * int(m.group(2))

    if req_mem and quote_mem:
        if quote_mem >= req_mem:
            if quote_mem > req_mem * 1.5:
                positive.append(f'内存({quote_mem}GB>{req_mem}GB)')
            else:
                issues.append(f'内存({quote_mem}GB≥{req_mem}GB)')
        else:
            negative.append(f'⚠ 内存不足({quote_mem}GB<{req_mem}GB)')

    # --- 吞吐量比对 ---
    req_tput = None
    quote_tput = None
    for unit in ['Gbps', 'G', 'Mbps', 'M']:
        v, u = extract_unit(req_spec, [f'{unit}(?:ps)?'])
        if v:
            req_tput = (v, u)
            break
    for unit in ['Gbps', 'G', 'Mbps', 'M']:
        v, u = extract_unit(quote_spec, [f'{unit}(?:ps)?'])
        if v:
            quote_tput = (v, u)
            break

    if req_tput and quote_tput:
        rv, ru = req_tput
        qv, qu = quote_tput
        # Normalize to Mbps
        r_norm = rv * 1000 if 'G' in ru else rv
        q_norm = qv * 1000 if 'G' in qu else qv
        if q_norm >= r_norm:
            if q_norm > r_norm * 2:
                positive.append(f'吞吐量({qv}{qu}>{rv}{ru})')
            else:
                issues.append(f'吞吐量({qv}{qu}≥{rv}{ru})')
        else:
            negative.append(f'⚠ 吞吐量不足({qv}{qu}<{rv}{ru})')

    # --- 端口/接口数比对 ---
    for port_type, port_label in [('千兆电', '千兆电口'), ('万兆光', '万兆光口'),
                                     ('SFP\\+', '万兆光口'), ('GE', 'GE口'), ('10GE', '10GE口')]:
        req_ports = None
        m = re.search(rf'(?:≥|>=)\s*(\d+)\s*(?:个|口)?\s*{port_type}', req_spec)
        if m: req_ports = int(m.group(1))
        quote_ports = None
        m = re.search(rf'(\d+)\s*(?:个|口)?\s*{port_type}', quote_spec)
        if m: quote_ports = int(m.group(1))

        if req_ports and quote_ports:
            if quote_ports >= req_ports:
                if quote_ports > req_ports * 1.5:
                    positive.append(f'{port_label}({quote_ports}个>{req_ports}个)')
            else:
                negative.append(f'⚠ {port_label}不足({quote_ports}个<{req_ports}个)')

    # --- 并发连接数比对 ---
    req_conn = None
    m = re.search(r'并发\s*(?:连接)?\s*(?:≥|>=)\s*(\d+)\s*万', req_spec)
    if m: req_conn = int(m.group(1)) * 10000
    if not req_conn:
        m = re.search(r'并发\s*(?:≥|>=)\s*(\d+)', req_spec)
        if m and int(m.group(1)) > 1000: req_conn = int(m.group(1))

    quote_conn = None
    m = re.search(r'并发\s*(?:连接)?[：:]*\s*(\d+)\s*万', quote_spec)
    if m: quote_conn = int(m.group(1)) * 10000
    if not quote_conn:
        m = re.search(r'并发\s*(?:≥|=)\s*(\d+)', quote_spec)
        if m and int(m.group(1)) > 1000: quote_conn = int(m.group(1))

    if req_conn and quote_conn:
        if quote_conn >= req_conn:
            if quote_conn > req_conn * 3:
                positive.append(f'并发连接({quote_conn}>>{req_conn})')
        else:
            negative.append(f'⚠ 并发连接不足({quote_conn}<{req_conn})')

    # --- 判定 ---
    if negative:
        return ('negative_deviation', '; '.join(negative + [f'✅ {i}' for i in issues]))
    if positive and not issues:
        return ('positive_deviation', '; '.join(positive))
    if positive:
        return ('meet_with_positive', '; '.join(issues + ['🔺 ' + p for p in positive]))
    if issues:
        return ('meet', '; '.join(issues))
    return ('unclear', '无法自动提取关键参数进行比对，需人工确认')


def match_items(req_items, quote_items):
    """将报价项匹配到需求项"""
    matches = []
    unmatched_req = list(req_items)
    unmatched_quote = list(quote_items)

    # Phase 1: exact name match
    for qi in quote_items[:]:
        qname = qi.get('name', '')
        for ri in unmatched_req[:]:
            rname = ri.get('name', '')
            if qname == rname or qname in rname or rname in qname:
                matches.append((ri, qi))
                unmatched_req.remove(ri)
                unmatched_quote.remove(qi)
                break

    # Phase 2: keyword overlap match
    for qi in unmatched_quote[:]:
        qname = qi.get('name', '')
        qwords = set(re.findall(r'[一-鿿\w]+', qname))
        best_ri, best_score = None, 0
        for ri in unmatched_req:
            rname = ri.get('name', '')
            rwords = set(re.findall(r'[一-鿿\w]+', rname))
            score = len(qwords & rwords) / max(len(qwords | rwords), 1)
            if score > best_score and score > 0.3:
                best_ri, best_score = ri, score
        if best_ri:
            matches.append((best_ri, qi))
            unmatched_req.remove(best_ri)
            unmatched_quote.remove(qi)

    return matches, unmatched_req, unmatched_quote


def compare(requirements, quotation_items, vendor_name=''):
    """主比对函数"""
    req_hw = requirements.get('hardware', [])

    # Match items
    matches, unmatched_req, unmatched_quote = match_items(req_hw, quotation_items)

    comparisons = []
    for req, quote in matches:
        verdict, detail = compare_specs(
            req.get('spec', req.get('key_params', '')),
            quote.get('spec', quote.get('key_params', '')),
            req.get('name', '')
        )
        comparisons.append({
            'req_name': req['name'],
            'req_spec': req.get('spec', '')[:200],
            'quote_model': quote.get('model', quote.get('name', '')),
            'quote_spec': quote.get('spec', '')[:200],
            'quote_qty': quote.get('qty', 0),
            'quote_price': quote.get('unit_price', 0),
            'quote_total': quote.get('total', 0),
            'verdict': verdict,
            'deviation_detail': detail,
        })

    # Summary
    verdict_counts = {'meet': 0, 'meet_with_positive': 0, 'positive_deviation': 0,
                      'negative_deviation': 0, 'unclear': 0}
    for c in comparisons:
        v = c['verdict']
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    meets = verdict_counts.get('meet', 0) + verdict_counts.get('meet_with_positive', 0)
    comparable_total = sum(c['quote_total'] for c in comparisons if c['quote_total'] > 0)

    return {
        'vendor': vendor_name or '未知厂商',
        'comparisons': comparisons,
        'summary': {
            'meets': meets,
            'positive_deviation': verdict_counts.get('positive_deviation', 0),
            'negative_deviation': verdict_counts.get('negative_deviation', 0),
            'cannot_determine': verdict_counts.get('unclear', 0),
            'comparable_total': comparable_total,
        },
        'unmatched_requirements': [{'name': r['name']} for r in unmatched_req],
        'unmatched_quotations': [{'name': q.get('name', '')} for q in unmatched_quote],
        'risk_items': [c for c in comparisons if c['verdict'] == 'negative_deviation'],
    }


def main():
    if len(sys.argv) < 3:
        print("用法: python3 compare_quotation.py requirements.json quotation.xlsx [--vendor 厂商名] [--json-out out.json]")
        sys.exit(1)

    req_file = sys.argv[1]
    quote_file = sys.argv[2]
    vendor = ''
    json_out = None

    for i, a in enumerate(sys.argv):
        if a == '--vendor' and i+1 < len(sys.argv):
            vendor = sys.argv[i+1]
        if a == '--json-out' and i+1 < len(sys.argv):
            json_out = sys.argv[i+1]

    # Load requirements
    with open(req_file, 'r', encoding='utf-8') as f:
        requirements = json.load(f)

    # Load quotation (simple xlsx)
    try:
        import openpyxl
        wb = openpyxl.load_workbook(quote_file, data_only=True)
        ws = wb.active
        quote_items = []
        header = None
        for ri, row in enumerate(ws.iter_rows(values_only=True), 1):
            cells = [str(c).strip() if c else '' for c in row]
            if any(kw in ' '.join(cells) for kw in ['序号', '名称', '型号', '规格', '参数', '单价']):
                header = cells
                continue
            if not header: continue
            if not cells[0].isdigit() and not any(cells): continue
            # Simple extraction
            item = {
                'name': cells[1] if len(cells) > 1 else '',
                'spec': cells[2] if len(cells) > 2 else (cells[3] if len(cells) > 3 else ''),
                'model': cells[3] if len(cells) > 3 else '',
                'qty': int(cells[5]) if len(cells) > 5 and cells[5].isdigit() else 0,
                'unit_price': float(cells[7]) if len(cells) > 7 else 0,
                'total': float(cells[8]) if len(cells) > 8 else 0,
            }
            if item['name']: quote_items.append(item)
    except Exception as e:
        print(f"读取报价文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    result = compare(requirements, quote_items, vendor)

    s = result['summary']
    print(f"✅ {vendor or '厂商'} 比对完成:")
    print(f"   满足: {s['meets']} | 正偏离: {s['positive_deviation']} | "
          f"负偏离: {s['negative_deviation']} | 无法判断: {s['cannot_determine']}")
    print(f"   可比项合计: ¥{s['comparable_total']:,}")
    if result['risk_items']:
        print(f"   ⚠ 负偏离风险: {len(result['risk_items'])}项")
    if result['unmatched_requirements']:
        print(f"   📋 未匹配需求: {len(result['unmatched_requirements'])}项")

    if json_out:
        with open(json_out, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"📄 → {json_out}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
