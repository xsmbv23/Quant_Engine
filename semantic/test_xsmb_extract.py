from semantic.xsmb_extract import extract


def _html():
    rows = []
    vals = {"G7":["12","34","56","78"],"G6":["123","234","345"],"G5":["1234","2345","3456","4567","5678","6789"],"G4":["12345","23456","34567","45678"],"G3":["12345","23456","34567","45678","56789","67890"],"G2":["12345","23456"],"G1":["12345"],"DB":["123456"]}
    labels = {"DB":"Đặc biệt","G1":"Giải nhất","G2":"Giải nhì","G3":"Giải ba","G4":"Giải tư","G5":"Giải năm","G6":"Giải sáu","G7":"Giải bảy"}
    for k in ["G7","G6","G5","G4","G3","G2","G1","DB"]:
        rows.append('<tr><td>'+labels[k]+'</td>'+''.join('<td>'+v+'</td>' for v in vals[k])+'</tr>')
    return '<table>'+''.join(rows)+'</table>'


def test_extracts_exact_27(tmp_path):
    p = tmp_path / 'x.html'; p.write_text(_html(), encoding='utf-8')
    result = extract(p, '2026-08-22', 'test-source')
    assert result['status'] == 'PASS'
    assert len(result['full_27']) == 27


def test_missing_prize_denies(tmp_path):
    p = tmp_path / 'x.html'; p.write_text(_html().replace('Giải nhì', 'UNKNOWN'), encoding='utf-8')
    result = extract(p, '2026-08-22', 'test-source')
    assert result['status'] == 'DENY'
    assert result['promotion'] == 'DENY'
