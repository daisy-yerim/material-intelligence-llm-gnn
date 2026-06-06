# ============================================================
# build_erp_kg.py
# ------------------------------------------------------------
# 목적:
#   - ERP 원본 엑셀(ITHM, DR, Rule Deduction, HeadMessage)을
#     OWL 온톨로지 스키마(wms_headmessage_ontology_v2.owl)에 맞춰
#     "지식그래프 인스턴스(RDF/TTL)"로 변환한다.
#
# 출력:
#   - erp_knowledge_graph.ttl  (스키마 + 인스턴스 포함)
#
# 준비:
#   pip install pandas openpyxl rdflib
# ============================================================

import re
import pandas as pd
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal
from rdflib.namespace import XSD

# ----------------------------
# 0) 파일 경로 설정 (네 환경에 맞게 수정)
# ----------------------------
OWL_SCHEMA_PATH = "wms_headmessage_ontology_v2.owl"

PATH_ITHM = "ITHM MASTER.xlsx"
PATH_DR   = "DR_Data.xlsx"
PATH_RD   = "Final_Rule_Deduction_Clean_add.xlsx"
PATH_HM   = "헤드메세지 MASTER 원본.xlsx"

OUT_TTL   = "erp_knowledge_graph.ttl"

# ----------------------------
# 1) OWL 스키마의 namespace (Protégé에서 보던 prefix)
#    OWL 파일이 사용하는 base IRI가 이거였음:
#      http://example.org/wms-hm#
# ----------------------------
WMS = Namespace("http://example.org/wms-hm#")

# ----------------------------
# 2) 유틸: 문자열을 URI-safe하게 바꾸기
#    (Observation id 만들 때 Date/ORG/Product 등으로 URI를 만듦)
# ----------------------------
def slugify(x: str) -> str:
    """
    URI에 들어갈 수 있게 위험한 문자들을 '_'로 치환.
    """
    s = str(x).strip()
    s = re.sub(r"\s+", "_", s)           # 공백 -> _
    s = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", s)  # 특수문자 -> _
    return s

def to_date(x):
    """
    pandas Timestamp / datetime / string 을 xsd:date용 'YYYY-MM-DD'로 변환.
    """
    if pd.isna(x):
        return None
    d = pd.to_datetime(x).date()
    return d.isoformat()

def to_float(x):
    """
    숫자형으로 변환. 변환 실패하면 None.
    """
    if pd.isna(x):
        return None
    try:
        return float(x)
    except:
        return None

def to_int(x):
    if pd.isna(x):
        return None
    try:
        return int(float(x))
    except:
        return None

# ----------------------------
# 3) 그래프 생성: 스키마(OWL) + 인스턴스 합치기
# ----------------------------
kg = Graph()

# (1) OWL 스키마를 먼저 로딩해두면, 결과 TTL이 "스키마+인스턴스"로 self-contained가 됨
kg.parse(OWL_SCHEMA_PATH)

# (2) prefix 바인딩 (TTL이 보기 좋아짐)
kg.bind("wms", WMS)
kg.bind("owl", OWL)
kg.bind("rdfs", RDFS)
kg.bind("xsd", XSD)

# ----------------------------
# 4) 캐시: 중복 인스턴스 생성 방지
#    - 같은 ORG는 같은 Organization 인스턴스
#    - 같은 Product는 같은 Product 인스턴스
#    - 같은 (Date,ORG,Product)는 같은 Observation 인스턴스
# ----------------------------
org_cache = {}     # orgCode -> org_uri
prod_cache = {}    # productCode -> product_uri
obs_cache = {}     # (date, org, product) -> obs_uri

# assessment cache: (obs_key, assessment_type) -> assessment_uri
assess_cache = {}

# line caches (obs_key, idx) -> line_uri
part_line_cache = {}
dr_line_cache = {}
rd_line_cache = {}

# raw material cache (optional)
raw_cache = {}     # rawMaterialCode -> raw_uri

# ----------------------------
# 5) 인스턴스 생성 함수들 (OWL domain/range 그대로 사용)
# ----------------------------
def get_or_create_org(org_code: str):
    """
    Organization 인스턴스 생성/재사용.
    OWL:
      Class: Organization
      DataProperty: orgCode (domain Organization, range xsd:string)
    """
    key = str(org_code)
    if key in org_cache:
        return org_cache[key]

    uri = WMS[f"org_{slugify(key)}"]
    kg.add((uri, RDF.type, WMS.Organization))
    kg.add((uri, WMS.orgCode, Literal(key, datatype=XSD.string)))
    org_cache[key] = uri
    return uri

def get_or_create_product(product_code: str):
    """
    Product 인스턴스 생성/재사용.
    OWL:
      Class: Product
      DataProperty: productCode (domain Product)
    """
    key = str(product_code)
    if key in prod_cache:
        return prod_cache[key]

    uri = WMS[f"product_{slugify(key)}"]
    kg.add((uri, RDF.type, WMS.Product))
    kg.add((uri, WMS.productCode, Literal(key, datatype=XSD.string)))
    prod_cache[key] = uri
    return uri

def get_or_create_observation(date_iso: str, org_code: str, product_code: str):
    """
    Observation 인스턴스 생성/재사용.
    OWL:
      Class: Observation
      DataProperty: date (domain Observation, range xsd:date)
      ObjectProperty:
        - hasOrganization (Observation -> Organization)
        - aboutProduct    (Observation -> Product)
    """
    key = (date_iso, str(org_code), str(product_code))
    if key in obs_cache:
        return obs_cache[key]

    uri = WMS[f"obs_{slugify(date_iso)}_{slugify(org_code)}_{slugify(product_code)}"]
    kg.add((uri, RDF.type, WMS.Observation))

    # date는 Observation의 data property
    kg.add((uri, WMS.date, Literal(date_iso, datatype=XSD.date)))

    # org/product 연결
    org_uri = get_or_create_org(org_code)
    prod_uri = get_or_create_product(product_code)

    kg.add((uri, WMS.hasOrganization, org_uri))
    kg.add((uri, WMS.aboutProduct, prod_uri))

    obs_cache[key] = uri
    return uri

def get_or_create_assessment(obs_key, assessment_cls):
    """
    Assessment 인스턴스 생성/재사용.
    assessment_cls 예: WMS.DeliveryRiskAssessment, WMS.InventoryTrendAssessment ...
    OWL:
      Observation hasAssessment Assessment
    """
    cache_key = (obs_key, str(assessment_cls))
    if cache_key in assess_cache:
        return assess_cache[cache_key]

    uri = WMS[f"assess_{slugify(obs_key[0])}_{slugify(obs_key[1])}_{slugify(obs_key[2])}_{slugify(local_name(assessment_cls))}"]
    kg.add((uri, RDF.type, assessment_cls))

    obs_uri = obs_cache[obs_key]  # 이미 observation이 만들어져 있다는 가정
    kg.add((obs_uri, WMS.hasAssessment, uri))

    assess_cache[cache_key] = uri
    return uri

def local_name(uri):
    s = str(uri)
    return s.split("#")[-1] if "#" in s else s.rsplit("/", 1)[-1]

def create_head_message(obs_uri, assessment_uri, category: str, text: str):
    """
    HeadMessage 인스턴스 생성.
    OWL:
      Class: HeadMessage
      DataProperty: messageText, messageCategory
      ObjectProperty:
        - Assessment generatesHeadMessage HeadMessage
        - Observation hasHeadMessage HeadMessage
    """
    if text is None or str(text).strip() == "":
        return None

    hm_uri = WMS[f"hm_{slugify(str(obs_uri).split('#')[-1])}_{slugify(category)}"]
    kg.add((hm_uri, RDF.type, WMS.HeadMessage))
    kg.add((hm_uri, WMS.messageCategory, Literal(category, datatype=XSD.string)))
    kg.add((hm_uri, WMS.messageText, Literal(str(text), datatype=XSD.string)))

    kg.add((assessment_uri, WMS.generatesHeadMessage, hm_uri))
    kg.add((obs_uri, WMS.hasHeadMessage, hm_uri))
    return hm_uri

def get_or_create_part_line(obs_key, idx: int):
    """
    PartInventoryLine 인스턴스 생성/재사용.
    OWL:
      Observation hasPartInventoryLine PartInventoryLine
      PartInventoryLine has partLineIndex (integer) 등 여러 data property
    """
    key = (obs_key, idx)
    if key in part_line_cache:
        return part_line_cache[key]

    uri = WMS[f"partline_{slugify(obs_key[0])}_{slugify(obs_key[1])}_{slugify(obs_key[2])}_{idx}"]
    kg.add((uri, RDF.type, WMS.PartInventoryLine))
    kg.add((uri, WMS.partLineIndex, Literal(idx, datatype=XSD.integer)))

    obs_uri = obs_cache[obs_key]
    kg.add((obs_uri, WMS.hasPartInventoryLine, uri))

    part_line_cache[key] = uri
    return uri

def get_or_create_dr_line(dr_assess_uri, obs_key, idx: int):
    """
    DeliveryRiskLine 인스턴스 생성/재사용.
    OWL:
      DeliveryRiskAssessment hasDeliveryRiskLine DeliveryRiskLine
      DeliveryRiskLine has drLineIndex, drDescription, poLeadTimeDays ...
    """
    key = (obs_key, idx)
    if key in dr_line_cache:
        return dr_line_cache[key]

    uri = WMS[f"drline_{slugify(obs_key[0])}_{slugify(obs_key[1])}_{slugify(obs_key[2])}_{idx}"]
    kg.add((uri, RDF.type, WMS.DeliveryRiskLine))
    kg.add((uri, WMS.drLineIndex, Literal(idx, datatype=XSD.integer)))

    kg.add((dr_assess_uri, WMS.hasDeliveryRiskLine, uri))
    dr_line_cache[key] = uri
    return uri

def get_or_create_rd_line(obs_key, idx: int):
    """
    RuleDeductionLine 인스턴스 생성/재사용.
    OWL:
      Observation hasRuleDeductionLine RuleDeductionLine
      RuleDeductionLine has lineIndex, overAmount, overDescription, assetFlag, requiredAmount
    """
    key = (obs_key, idx)
    if key in rd_line_cache:
        return rd_line_cache[key]

    uri = WMS[f"rdline_{slugify(obs_key[0])}_{slugify(obs_key[1])}_{slugify(obs_key[2])}_{idx}"]
    kg.add((uri, RDF.type, WMS.RuleDeductionLine))
    kg.add((uri, WMS.lineIndex, Literal(idx, datatype=XSD.integer)))

    obs_uri = obs_cache[obs_key]
    kg.add((obs_uri, WMS.hasRuleDeductionLine, uri))

    rd_line_cache[key] = uri
    return uri

# ============================================================
# 6) 데이터 로딩 (엑셀 헤더가 병합된 파일은 header row를 찾아서 읽기)
# ============================================================

def read_excel_guess_header(path, header_key="Date", max_scan_rows=10):
    """
    어떤 엑셀은 0~2행에 설명이 있고 실제 헤더가 아래에 있음.
    이 함수는 상단 몇 행을 스캔해서 첫 컬럼이 header_key인 행을 헤더로 사용한다.
    """
    tmp = pd.read_excel(path, sheet_name="Sheet1", header=None)
    header_row = None
    for r in range(min(max_scan_rows, len(tmp))):
        if str(tmp.iloc[r, 0]).strip() == header_key:
            header_row = r
            break
    if header_row is None:
        # 못 찾으면 그냥 0행을 헤더로
        return pd.read_excel(path, sheet_name="Sheet1")
    return pd.read_excel(path, sheet_name="Sheet1", header=header_row)

df_ithm = pd.read_excel(PATH_ITHM, sheet_name="Sheet1")  # ITHM은 헤더가 깔끔
df_dr   = read_excel_guess_header(PATH_DR, header_key="Date")
df_rd   = read_excel_guess_header(PATH_RD, header_key="Date")
df_hm   = pd.read_excel(PATH_HM, sheet_name="Sheet1")    # 헤더 깔끔

# ============================================================
# 7) ITHM MASTER ingest
#    - Observation 생성
#    - PartInventoryLine(1~5) 생성 및 수치들 매핑
#    - InventoryTrendAssessment + HeadMessage(InventoryTrend) 생성
# ============================================================

for _, row in df_ithm.iterrows():
    date_iso = to_date(row["Date"])
    if date_iso is None:
        continue

    org = row["ORG"]
    product = row["Product"]
    obs_uri = get_or_create_observation(date_iso, org, product)

    # obs_key는 캐시 키로 그대로 재사용
    obs_key = (date_iso, str(org), str(product))

    # InventoryTrendAssessment 생성 (문장이 있으면)
    trend_text = row.get("Inventory Trend", None)
    if pd.notna(trend_text) and str(trend_text).strip() != "":
        trend_assess = get_or_create_assessment(obs_key, WMS.InventoryTrendAssessment)

        # inventoryTrendText는 InventoryTrendAssessment의 data property
        kg.add((trend_assess, WMS.inventoryTrendText, Literal(str(trend_text), datatype=XSD.string)))

        # ITHM에 있는 여러 플래그 컬럼들을 trendFlag 하나에 묶어 저장(1인 것만)
        flag_cols = ["INS TG", "NO TG", "OVER ED", "SHORTAGE ED", "INS PO", "INS Need by Date",
                     "NO REQ", "FEW REQ", "PLAN REQ", "S OVER", "S SHORTAGE", "INC SCORE", "DEC SCORE"]
        active = []
        for c in flag_cols:
            if c in df_ithm.columns and pd.notna(row[c]) and str(row[c]).strip() not in ["0", "0.0", "nan"]:
                # 값이 0이 아니면 '활성'으로 보고 저장
                active.append(c)
        if active:
            kg.add((trend_assess, WMS.trendFlag, Literal(";".join(active), datatype=XSD.string)))

        # HeadMessage도 생성 (category=InventoryTrend)
        create_head_message(obs_uri, trend_assess, "InventoryTrend", trend_text)

    # PartInventoryLine 1~5 생성
    for i in range(1, 6):
        part_no_col = f"Part No._{i}"
        desc_col    = f"Desc._{i}"

        part_no = row.get(part_no_col, None)
        desc    = row.get(desc_col, None)

        # part_no가 없으면 그 part slot은 skip
        if pd.isna(part_no):
            continue

        part_uri = get_or_create_part_line(obs_key, i)

        # 필수: partNumber / partDescription
        kg.add((part_uri, WMS.partNumber, Literal(str(part_no), datatype=XSD.string)))
        if pd.notna(desc):
            kg.add((part_uri, WMS.partDescription, Literal(str(desc), datatype=XSD.string)))

        # 나머지 수치/텍스트 속성들
        def set_if_exists(prop, col, dtype="double"):
            val = row.get(col, None)
            if pd.isna(val):
                return
            if dtype == "double":
                f = to_float(val)
                if f is not None:
                    kg.add((part_uri, prop, Literal(f, datatype=XSD.double)))
            elif dtype == "string":
                kg.add((part_uri, prop, Literal(str(val), datatype=XSD.string)))

        set_if_exists(WMS.unitType,               f"UIT_{i}", "string")
        set_if_exists(WMS.inventoryScore,         f"Inv Score_{i}", "double")
        set_if_exists(WMS.targetDIO,              f"Target DIO_{i}", "double")
        set_if_exists(WMS.estimatedDIO,           f"Est DIO_{i}", "double")
        set_if_exists(WMS.signal,                 f"Signal_{i}", "string")
        set_if_exists(WMS.estimatedInventoryQty,  f"Est. Inv Qty_{i}", "double")
        set_if_exists(WMS.estimatedInventoryAmount,f"Est. Inv Amt_{i}", "double")

        # Gross/Sub (i_k) → (grossIndex,grossValue),(subIndex,subValue)
        # 주의: OWL에는 grossIndex/grossValue가 1쌍을 "객체"로 묶는 구조가 없어서
        #       index/value를 다중값으로 넣고, 나중에 동일한 loop 순서로 zip해 사용한다.
        for k in range(1, 6):
            gross_col = f"Gross {i}_{k}"
            sub_col   = f"Sub {i}_{k}"

            gval = to_float(row.get(gross_col, None))
            sval = to_float(row.get(sub_col, None))

            if gval is not None:
                kg.add((part_uri, WMS.grossIndex, Literal(k, datatype=XSD.integer)))
                kg.add((part_uri, WMS.grossValue, Literal(gval, datatype=XSD.double)))
            if sval is not None:
                kg.add((part_uri, WMS.subIndex, Literal(k, datatype=XSD.integer)))
                kg.add((part_uri, WMS.subValue, Literal(sval, datatype=XSD.double)))

# ============================================================
# 8) DR_Data ingest (DeliveryRisk)
# ============================================================

# DR에서 indicatorFlag로 묶을 “0/1 flag 컬럼들”
DR_FLAG_COLS = [
    "과거대비 Over 증가", "과거대비 Over 감소",
    "Shortage가 높음", "Shortage가 낮음", "관리가 잘 되고 있음",
    "Over가 높음", "Over가 낮음", "PO과잉", "PO부족", "No Gross"
]

for _, row in df_dr.iterrows():
    date_iso = to_date(row["Date"])
    if date_iso is None:
        continue
    org = row["ORG"]
    product = row["Product"]
    obs_uri = get_or_create_observation(date_iso, org, product)
    obs_key = (date_iso, str(org), str(product))

    # DeliveryRiskAssessment 생성
    dr_assess = get_or_create_assessment(obs_key, WMS.DeliveryRiskAssessment)

    # riskCategory: Category(0/1)를 Over/Shortage로 해석
    cat = row.get("Category", None)
    if pd.notna(cat):
        risk = "Over" if int(cat) == 1 else "Shortage"
        kg.add((dr_assess, WMS.riskCategory, Literal(risk, datatype=XSD.string)))

    # 전주/현재 비율
    def set_assess_double(prop, col):
        v = to_float(row.get(col, None))
        if v is not None:
            kg.add((dr_assess, prop, Literal(v, datatype=XSD.double)))

    set_assess_double(WMS.prevOverRate,      "전 주 Over Rate")
    set_assess_double(WMS.prevProperRate,    "전 주 Proper Rate")
    set_assess_double(WMS.prevShortageRate,  "전 주 Shortage Rate")
    set_assess_double(WMS.curOverRate,       "현재 주 Over Rate")
    set_assess_double(WMS.curProperRate,     "현재 주 Proper Rate")
    set_assess_double(WMS.curShortageRate,   "현재 주 Shortage Rate")

    set_assess_double(WMS.overDiff,          "Over 차이")
    set_assess_double(WMS.properDiff,        "Proper 차이")
    set_assess_double(WMS.shortageDiff,      "Shortage 차이")

    set_assess_double(WMS.overOverPlusShortage,     "Over/Over+Shortage")
    set_assess_double(WMS.shortageOverPlusShortage, "Shortage/Over+Shortage")
    set_assess_double(WMS.curOverMinusShortage,     "현재 주 Over와 Shortage의 차이")

    # indicatorFlag: 1인 컬럼명을 ;로 join
    active_flags = []
    for c in DR_FLAG_COLS:
        if c in df_dr.columns and pd.notna(row[c]) and int(row[c]) == 1:
            active_flags.append(c)
    if active_flags:
        kg.add((dr_assess, WMS.indicatorFlag, Literal(";".join(active_flags), datatype=XSD.string)))

    # Head Message -> HeadMessage 인스턴스로 저장
    hm_text = row.get("Head Message", None)
    create_head_message(obs_uri, dr_assess, "DeliveryRisk", hm_text)

    # DeliveryRiskLine 1~5
    for i in range(1, 6):
        desc = row.get(f"Description.{i}", None)
        if pd.isna(desc):
            continue

        line_uri = get_or_create_dr_line(dr_assess, obs_key, i)
        kg.add((line_uri, WMS.drDescription, Literal(str(desc), datatype=XSD.string)))

        def set_line_double(prop, col):
            v = to_float(row.get(col, None))
            if v is not None:
                kg.add((line_uri, prop, Literal(v, datatype=XSD.double)))

        set_line_double(WMS.poLeadTimeDays,     f"PO L/T.{i}")
        set_line_double(WMS.poSum,              f"PO SUM.{i}")
        set_line_double(WMS.grossReqSum,        f"Gross REQ SUM.{i}")
        set_line_double(WMS.poOverShortageQty,  f"PO O&S QTY.{i}")
        set_line_double(WMS.poOverShortageAmt,  f"PO O&S AMT.{i}")

# ============================================================
# 9) Rule Deduction ingest
#    - InOutControlAssessment.inOutControlText <- HeadMessage
#    - RuleDeductionLine(1~5) <- Over Amount/Desc/Asset/REQ Amount
# ============================================================

for _, row in df_rd.iterrows():
    date_iso = to_date(row["Date"])
    if date_iso is None:
        continue
    org = row["ORG"]
    product = row["Product"]
    obs_uri = get_or_create_observation(date_iso, org, product)
    obs_key = (date_iso, str(org), str(product))

    # InOutControlAssessment 생성
    io_assess = get_or_create_assessment(obs_key, WMS.InOutControlAssessment)

    # HeadMessage 텍스트를 inOutControlText에 저장
    io_text = row.get("HeadMessage", None)
    if pd.notna(io_text) and str(io_text).strip() != "":
        kg.add((io_assess, WMS.inOutControlText, Literal(str(io_text), datatype=XSD.string)))
        create_head_message(obs_uri, io_assess, "InOutControl", io_text)

    # RuleDeductionLine 1~5
    for i in range(1, 6):
        over_amt = row.get(f"Over Amount_{i}", None)
        over_desc = row.get(f"Over Desc_{i}", None)
        asset_col = f"Asset_{i}(0:Asset, 1:Non-Asset"
        req_amt = row.get(f"REQ Amount_{i}", None)

        # 아무 정보도 없으면 skip
        if pd.isna(over_amt) and pd.isna(over_desc) and pd.isna(req_amt):
            continue

        rd_uri = get_or_create_rd_line(obs_key, i)

        # overAmount
        v = to_float(over_amt)
        if v is not None:
            kg.add((rd_uri, WMS.overAmount, Literal(v, datatype=XSD.double)))

        # overDescription
        if pd.notna(over_desc):
            kg.add((rd_uri, WMS.overDescription, Literal(str(over_desc), datatype=XSD.string)))

        # assetFlag (integer)
        if asset_col in df_rd.columns:
            av = to_int(row.get(asset_col, None))
            if av is not None:
                kg.add((rd_uri, WMS.assetFlag, Literal(av, datatype=XSD.integer)))

        # requiredAmount
        rv = to_float(req_amt)
        if rv is not None:
            kg.add((rd_uri, WMS.requiredAmount, Literal(rv, datatype=XSD.double)))

# ============================================================
# 10) HeadMessage MASTER ingest (Inventory Trend flags + part(1~5) 보완)
# ============================================================

# Inventory Trend 이후 ~ PartNo1 직전까지를 "플래그 컬럼"으로 보고 1인 것만 trendFlag에 저장
if "PartNo1" in df_hm.columns and "Inventory Trend" in df_hm.columns:
    flag_cols = list(df_hm.columns)[
        list(df_hm.columns).index("Inventory Trend") + 1 : list(df_hm.columns).index("PartNo1")
    ]
else:
    flag_cols = []

for _, row in df_hm.iterrows():
    date_iso = to_date(row["DATE"])
    if date_iso is None:
        continue
    org = row["ORG"]
    product = row["Product"]
    obs_uri = get_or_create_observation(date_iso, org, product)
    obs_key = (date_iso, str(org), str(product))

    # InventoryTrendAssessment
    trend_assess = get_or_create_assessment(obs_key, WMS.InventoryTrendAssessment)

    trend_text = row.get("Inventory Trend", None)
    if pd.notna(trend_text) and str(trend_text).strip() != "":
        kg.add((trend_assess, WMS.inventoryTrendText, Literal(str(trend_text), datatype=XSD.string)))
        create_head_message(obs_uri, trend_assess, "InventoryTrend", trend_text)

    # trendFlag = 1인 플래그 컬럼명 join
    active = []
    for c in flag_cols:
        # 값이 1이면 활성 플래그로 기록
        try:
            if pd.notna(row[c]) and int(row[c]) == 1:
                active.append(c)
        except:
            pass
    if active:
        kg.add((trend_assess, WMS.trendFlag, Literal(";".join(active), datatype=XSD.string)))

    # PartInventoryLine 보완(PartNo1~5)
    for i in range(1, 6):
        pno = row.get(f"PartNo{i}", None)
        if pd.isna(pno):
            continue

        part_uri = get_or_create_part_line(obs_key, i)
        kg.add((part_uri, WMS.partNumber, Literal(str(pno), datatype=XSD.string)))

        desc = row.get(f"Description{i}", None)
        if pd.notna(desc):
            kg.add((part_uri, WMS.partDescription, Literal(str(desc), datatype=XSD.string)))

        uit = row.get(f"UIT{i}", None)
        if pd.notna(uit):
            kg.add((part_uri, WMS.unitType, Literal(str(uit), datatype=XSD.string)))

        invs = to_float(row.get(f"Inv. Score{i}", None))
        if invs is not None:
            kg.add((part_uri, WMS.inventoryScore, Literal(invs, datatype=XSD.double)))

        # Target DIO는 컬럼명이 줄바꿈 포함 -> 정확히 써야 함
        tdio = to_float(row.get(f"Target\nDIO{i}", None))
        if tdio is not None:
            kg.add((part_uri, WMS.targetDIO, Literal(tdio, datatype=XSD.double)))

        edio = to_float(row.get(f"Estimated DIO{i}", None))
        if edio is not None:
            kg.add((part_uri, WMS.estimatedDIO, Literal(edio, datatype=XSD.double)))

        # Gross/Sub (M+1~M+3만 있음: 컬럼명 예 "Gross Req. QTY\nM+11" = (M+1, part1))
        for h in [1, 2, 3]:
            gcol = f"Gross Req. QTY\nM+{h}{i}"
            scol = f"Substitute QTY\nM+{h}{i}"
            gval = to_float(row.get(gcol, None))
            sval = to_float(row.get(scol, None))
            if gval is not None:
                kg.add((part_uri, WMS.grossIndex, Literal(h, datatype=XSD.integer)))
                kg.add((part_uri, WMS.grossValue, Literal(gval, datatype=XSD.double)))
            if sval is not None:
                kg.add((part_uri, WMS.subIndex, Literal(h, datatype=XSD.integer)))
                kg.add((part_uri, WMS.subValue, Literal(sval, datatype=XSD.double)))

# ============================================================
# 11) 저장 (TTL)
# ============================================================
kg.serialize(destination=OUT_TTL, format="turtle")
print(f"[DONE] Knowledge Graph saved to: {OUT_TTL}")