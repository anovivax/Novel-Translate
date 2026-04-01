# -*- coding: utf-8 -*-
import os
import re
from collections import defaultdict
import streamlit as st

# --- การตั้งค่าและพรอมต์ ---
MAX_CONTEXT_PARAGRAPHS = 75
MIN_FREQUENCY = 5

PROMPT_HEADER = """
บทบาท: ท่านคือผู้เชี่ยวชาญการแปลวรรณกรรม (Professional Literary Translator) มีความสามารถเป็นเลิศในการถ่ายทอดนิยายจีนแนวกำลังภายใน, เทพเซียน, และแนวระบบ เทคโนโลยีสมัยใหม่ ให้เป็นภาษาไทยได้อย่างมีชีวิตชีวา เปี่ยมด้วยอรรถรส และคงไว้ซึ่งเจตนารมณ์ของผู้เขียน

เป้าหมายหลัก: เป้าหมายของท่านคือการแปลคำศัพท์ภาษาจีนจาก 'เนื้อหาที่ยกมา' ให้เป็นภาษาไทย โดยคำศัพท์ที่แปลต้องเหมาะสมกับนิยายจีนแนวกำลังภายใน, เทพเซียน, และแนวระบบ เทคโนโลยีสมัยใหม่

สำหรับแต่ละคำศัพท์ ท่านต้องเสนอชื่อ 2 รูปแบบ คือ:
- การแปลตามความหมาย: เพื่อสื่อถึงนัยสำคัญและภาพลักษณ์ของชื่อนั้นๆ
- การทับศัพท์: เพื่อคงเสียงอ่านดั้งเดิมไว้ โดยต้องปฏิบัติตาม 'หลักการแปลเพิ่มเติม' และ 'กฎการทับศัพท์' ที่กำหนดไว้อย่างเคร่งครัด

หลักการแปลเพิ่มเติม (Additional Translation Principles):
1.  การแปลชื่อเฉพาะ (สถานที่, สำนัก, ตระกูล):
    เมื่อแปลชื่อเฉพาะ เช่น สำนัก, นิกาย, วัง, เมือง, หรือตระกูล ให้ท่านแยกส่วนประกอบของชื่อออกเป็น 2 ส่วน:
    - ส่วนที่เป็นชื่อเฉพาะ (เช่น 皇极, 百花, 金剑): ให้ทำการ ทับศัพท์ ตามเสียงอ่านและกฎที่กำหนด
    - ส่วนที่เป็นคำนามทั่วไป (เช่น 宗, 门, 阁, 城, 家): ให้ทำการ แปลความหมาย เป็นภาษาไทย (เช่น สำนัก, ประตู/สำนัก, หอ, เมือง, ตระกูล)
    - ตัวอย่าง: 皇极宗 จะต้องแปลแบบทับศัพท์เป็น สำนักหวงจี๋ (ไม่ใช่ หวงจี๋จง)

2.  การแปลชื่อบุคคลที่มีฉายาหรือตำแหน่ง:
    เมื่อแปลชื่อบุคคลที่มีฉายาหรือตำแหน่งต่อท้าย ให้ท่านแยกส่วนประกอบออกเป็น 2 ส่วน:
    - ส่วนที่เป็นชื่อบุคคล (เช่น 楚阳, 皇卓宇): ให้ทำการ ทับศัพท์ ตามเสียงอ่านและกฎที่กำหนด
    - ส่วนที่เป็นฉายาหรือตำแหน่ง (เช่น 仙帝, 宗主, 圣女): ให้ทำการ แปลความหมาย ของตำแหน่งนั้นๆ และนำมาวางไว้ ข้างหน้า ชื่อบุคคล
    - ตัวอย่าง: 楚阳仙帝 จะต้องแปลเป็น จักรพรรดิเซียนฉู่หยาง (ไม่ใช่ ฉู่หยางเซียนตี้)

การแปลตามโครงสร้างและรูปแบบ (Structural Patterns):
กฎ: หากเจอคำที่ตรงตามโครงสร้างที่กำหนด ให้แปลตามรูปแบบนั้น การแปลชื่อให้ทับศัพท์โดยใช้กฎการทับศัพท์ตัวอักษรเดี่ยว
- รูปแบบที่ 1 (ตำแหน่ง + ชื่อ): [ชื่อเฉพาะ] + [ตำแหน่ง/ระดับพลัง] ต้องแปลเป็น [คำแปลตำแหน่ง/ระดับพลัง] + [คำแปลชื่อเฉพาะ] (ตัวอย่าง: 震雷域神 -> เทพโลกาเจิ้นเหลย)
- รูปแบบที่ 2 (คำนำหน้า + ชื่อ): 老 + [ชื่อ] ต้องแปลเป็น ผู้เฒ่า + [ชื่อ] (ตัวอย่าง: 老杨 -> ผู้เฒ่าหยาง)

กฎการทับศัพท์ที่ต้องปฏิบัติตามอย่างเคร่งครัด: การทับศัพท์ตัวอักษรเดี่ยว (Single-Character Transliteration)
เมื่อทำการทับศัพท์ชื่อตัวละครหรือคำเฉพาะ หากเจอตัวอักษรจีนต่อไปนี้ จะต้อง ทับศัพท์เป็นคำภาษาไทยที่กำหนดให้เท่านั้น:
- เมื่อแปลแล้วเจอ 素, 肃, 苏, 蘇, 宿, 树, 绪, 叙, 序, 須, 须, 臾, 蓿, 恤, 戍, 澍, 朔, 秫, 洙, 徐,许 หรือเสียงพินอิน (sù,xù,su)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า ซู่
- เมื่อแปลแล้วเจอ 云, 芸, 昀, 耘, 筠, 韫, 蕴, 熨, 运, 贇, 缊, 殒 ,韵 หรือเสียงพินอิน (yùn,yǔn,yún,yun)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า หยุน
- เมื่อแปลแล้วเจอ 玉, 雨, 宇, 煜, 昱, 渝, 悦, 月, 钺, 鉞, 越, 岳, 禹, 語, 语, 羽, 禦, 御, 毓, 郁, 喻, 癒, 愈, 諭, 谕, 瑀, 萸,魊, 域, 虞, 浴  หรือเสียงพินอิน (yù,yǔ,yú,yu)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า หยู
- เมื่อแปลแล้วเจอ 燕, 艳, 艷, 彦, 延, 炎, 颜, 顏, 言, 研, 岩, 烟, 煙, 严, 嚴, 闫, 閆, 堰, 晏, 雁, 筵, 鄢, 偃 ,焱 ,衍, 焰  หรือเสียงพินอิน (yān,yǎn,Yān,yán,yàn )ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า เหยียน
- เมื่อแปลแล้วเจอ 霍, 火, 华, 華, 花, 画, 畫, 化, 滑, 哗, 嘩, 骅, 桦, 樺, 铧, 鍜, 豁, 婳 หรือเสียงพินอิน (huā,huà,huá,Huà,Huá,Huā )ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า ฮั่ว
- เมื่อแปลแล้วเจอ 莫, 墨, 寞, 陌, 魔, 漠, 末, 沫, 妺, 脉, 脈, 貘 หรือเสียงพินอิน (mò,mó,mò)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า โม่
- เมื่อแปลแล้วเจอ 軒, 玄, 宣, 璇, 喧, 暄, 煊, 瑄, 旋, 悬, 漩, 玹, 选, 癣, 烜, 炫, 绚, 眩, 渲, 泫 หรือเสียงพินอิน (xuǎn,xuán,xuān)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า ซวน
- เมื่อแปลแล้วเจอ 绝, 絕, 爵, 决, 決, 覺, 觉, 蕨, 鐍, 钁, 噘, 撅, 玦, 珏, 厥, 崛, 谲, 矍, 攫, 蹶, 倔 หรือเสียงพินอิน (jué)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า จิ่ว
- เมื่อแปลแล้วเจอ 学, 雪, 削, 穴, 薛, 鳕, 噱, 穴, 血, 削, 靴 หรือเสียงพินอิน (xuě)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า เสวีย
- เมื่อแปลแล้วเจอ 姚, 妖, 腰, 邀, 夭, 瑶, 遥, 谣, 窑, 杳, 咬, 要, 药, 耀 หรือเสียงพินอิน (yāo, yáo, yǎo, yào)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า เหยา
- เมื่อแปลแล้วเจอ 夜, 叶, 业, 烨, 邑 ,爷 หรือเสียงพินอิน (yè,ye)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า เย่
- เมื่อแปลแล้วเจอ 朱, 猪, 珠, 株, 诸, 竹, 菊, 助, 菊, 局, 橘, 鞠, 举, 咀, 拘 หรือเสียงพินอิน (zhú,jú,zhu)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า จู
- เมื่อแปลแล้วเจอ 元, 圆, 原, 源, 苑, 院, 缘, 猿, 袁, 垣, 媛, 源 หรือเสียงพินอิน (yuán,yuàn,yuan)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า หยวน
- เมื่อแปลแล้วเจอ 君, 军, 軍, 均, 钧, 鈞, 菌, 皲, 皸, 筠, 郡, 珺, 莙, 皲, 俊, 峻, 骏, 駿, 竣, 浚, 隽, 捃 หรือเสียงพินอิน (jùn,jún,jūn)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า จุน
- เมื่อแปลแล้วเจอ 捋, 啰, 囉, 椤, 猡, 罗, 羅, 螺, 逻, 邏, 锣, 鑼, 箩, 籮, 骡, 騾, 蠃, 猡, 蠃, 倮, 裸, 倮, 蠃, 落, 洛, 络, 絡, 骆, 駱, 烙, 雒, 摞, 荦, 犖, 珞 หรือเสียงพินอิน (luǒ,luó,luō,luò)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า หลัว
- เมื่อแปลแล้วเจอ 孙, 孫, 荪, 蓀, 狲, 猻, 飧, 损, 損, 损, 損, 笋, 筍, 榫, 隼, 巽, 狲, 潠 หรือเสียงพินอิน (sǔn,sún,sūn,sùn)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า ซุน
- เมื่อแปลแล้วเจอ 没, 沒, 妹, 梅, 眉, 媒, 枚, 煤, 酶, 霉, 糜, 美, 每, 浼, 镁, 鎂, 妹, 媚, 寐, 昧, 袂, 媄, 嚜 หรือเสียงพินอิน (mèi,měi,méi,mēi)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า เหมย
- เมื่อแปลแล้วเจอ 威, 微, 危, 巍, 煨, 偎, 逶, 葳, 囗, 为, 為, 围, 圍, 维, 維, 唯, 违, 違, 帷, 惟, 闱, 闈, 桅, 沩, 潙, 涠, 潿, 伟, 偉, 尾, 委, 娓, 苇, 蔿, 萎, 艉, 位, 未, 味, 卫, 衛, 谓, 謂, 蔚, 尉, 畏, 喂, 慰, 渭, 餵, 猬, 蝟, 謂, 谓 หรือเสียงพินอิน (wèi,wěi,wéi,wēi)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า เหวย
- เมื่อแปลแล้วเจอ 缺, 炔, 阙, 闕, 瘸, 确, 確, 鹊, 鵲, 阙, 闕, 雀, 榷, 炔, 悫, 愨 หรือเสียงพินอิน (què,quě,qué,quē)ในชื่อหรือคำเฉพาะที่ทับศัพท์ ให้ทับศัพท์เป็นคำว่า ฉิว
และกำหนดให้ 
圣域 = ดินแดนศักดิ์สิทธิ์
圣地 = ดินแดนศักดิ์สิทธิ์ 
道人 = นักพรต 
侯府 = จวนเจ้าพระยา
侯 = เจ้าพระยา
公府 = จวนเจ้าผู้ครองเมือง
"""

PROMPT_FOOTER_INSTRUCTIONS = """
คำสั่ง : ให้ทำการวิเคราะห์เนื้อที่ให้ไว้ในตอนต้น จากนั้นคิดชื่อภาษาไทยในเหมาะสมในการใช้กับนิยายกำลังภายใน เทพเซียน ให้มีกลิ่นอ้าย นิยายเทพเซียน ศักดิ์สิทธิ์ โบราณ โดยอ้างอิงจาก "เนื้อส่วนหนึ่งของนิยายที่ใช้สำหรับอ้างอิงในการคิดชื่อคำศัพท์"
สร้างผลลัพธ์ใน ** Code Box ของตัวเอง** โครงสร้างผลลัพธ์สุดท้ายต้องเป็นดังนี้ทุกประการ:
โดยจัดรูปดังนี้ [คำศัพท์ภาษาจีน] | [คำทับศัพท์ (พินอิน)] [คำแปลภาษาไทย1]/[คำแปลภาษาไทย2]/[คำแปลภาษาไทย]   | (หมวดหมู่และยุคสมัย)[คำอธิบายของตำศัพท์โดยละเอียด] ***จัดให้อยู่ใน Code Block*** 
"""

FINAL_COMMAND_TEXT = """คำสั่งสุดท้าย: สำหรับรายการคำศัพท์ภาษาจีนทั้งหมดด้านล่างนี้
โปรดประมวลผลทีละคำ โดยอ้างอิงจากบริบทใน 'เนื้อหาที่ยกมา' และปฏิบัติตามกฎทั้งหมดที่ให้ไว้ข้างต้นอย่างเคร่งครัด
สร้างผลลัพธ์สำหรับแต่ละคำในรูปแบบที่กำหนดเท่านั้น:คิดชื่อคำศัพท์พร้อมบอกยุคสมัย เช่นคำนี้อยู่ในนิยายจีนโบราณกำลังภายในหรืออยู่ในนิยายยุคปัจจุบันไซไฟแฟนตาซี
"""

def extract_chinese_chars(text): 
    return re.findall(r'[\u4e00-\u9fff]+', text)

def process_data(novel_text, whitelist_text, blacklist_text, special_instruction):
    parsed_blacklist = {}
    if blacklist_text:
        for line in blacklist_text.splitlines():
            if '=' in line:
                parts = line.split('=', 1)
                chinese_term = parts[0].strip()
                thai_translation = parts[1].strip()
                if chinese_term and thai_translation:
                    parsed_blacklist[chinese_term] = thai_translation

    found_blacklist_in_novel = {}
    if parsed_blacklist:
        for term, translation in parsed_blacklist.items():
            if term in novel_text:
                found_blacklist_in_novel[term] = translation

    all_blacklist_keys = set(parsed_blacklist.keys())
    if special_instruction:
        special_blacklist_terms = set(extract_chinese_chars(special_instruction))
        all_blacklist_keys.update(special_blacklist_terms)

    whitelisted_terms = set(extract_chinese_chars(whitelist_text))
    candidate_terms = {term for term in (whitelisted_terms - all_blacklist_keys) if len(term) > 1}

    if not candidate_terms and not found_blacklist_in_novel:
        return "❌ ไม่พบคำศัพท์ใหม่ (ที่ยาวกว่า 1 ตัวอักษร) หรือคำในคลังคำศัพท์ที่ปรากฏในนิยายเลย"

    final_target_terms = []
    if candidate_terms:
        term_counts = defaultdict(int)
        for term in candidate_terms: 
            term_counts[term] = novel_text.count(term)
        final_target_terms = sorted([term for term in candidate_terms if term_counts[term] > MIN_FREQUENCY])

    contexts = defaultdict(list)
    all_novel_lines = novel_text.splitlines()
    
    if final_target_terms:
        regex_pattern = "|".join(re.escape(term) for term in final_target_terms)
        compiled_regex = re.compile(regex_pattern)
        for line in all_novel_lines:
            stripped_line = line.strip()
            if not stripped_line: continue
            found_terms_in_para = set(compiled_regex.findall(stripped_line))
            for term in found_terms_in_para:
                if len(contexts[term]) < MAX_CONTEXT_PARAGRAPHS: 
                    contexts[term].append(stripped_line)

    context_parts = [PROMPT_HEADER.strip()]
    if final_target_terms:
        context_parts.append("\nเนื้อส่วนหนึ่งของนิยายที่ใช้สำหรับอ้างอิงในการคิดชื่อคำศัพท์")
        for term in final_target_terms:
            if term in contexts and contexts[term]:
                term_section = [f"===== คำ: {term} ====="] + contexts[term]
                context_parts.append("\n\n".join(term_section))
    
    context_output_string = "\n\n".join(context_parts)
    special_instruction_block = f"\n\n{special_instruction}" if special_instruction else ""
    
    formatted_blacklist_block = ""
    if found_blacklist_in_novel:
        definitions = [f"{chinese} = {thai}" for chinese, thai in found_blacklist_in_novel.items()]
        formatted_blacklist_block = "คำศัพท์ต่อไปนี้ถูกกำหนดไว้แล้ว (พบในนิยาย):\n" + "\n".join(definitions) + "\n\n"

    new_terms_list_string = "\n".join(final_target_terms)
    instructional_bridge_text = "จากนั้น โปรดประมวลผลรายการคำศัพท์ใหม่ทั้งหมดด้านล่างนี้ตามคำสั่ง:\n" if new_terms_list_string else ""
    
    footer_output_string = (
        f"\n\n\n{PROMPT_FOOTER_INSTRUCTIONS.strip()}{special_instruction_block}\n\n"
        f"{FINAL_COMMAND_TEXT.strip()}\n\n"
        f"{formatted_blacklist_block}"
        f"{instructional_bridge_text}"
        f"{new_terms_list_string}"
    )
    
    return context_output_string + footer_output_string

# --- UI ด้วย Streamlit ---
st.set_page_config(page_title="Translator Prompt Gen", layout="wide")

st.title("📚 Literary Prompt Generator (Web Version)")
st.markdown("ระบบสร้าง Prompt สำหรับงานแปลนิยาย รองรับการใช้งานผ่าน iPad")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. กำหนดค่า (Configuration)")
    novel_file = st.file_uploader("📂 1. อัปโหลดไฟล์นิยาย (.txt)", type=['txt'])
    
    whitelist_text = st.text_area("📝 2. วางคำศัพท์ Whitelist ทั้งหมดที่นี่ (บังคับ):", height=150)
    whitelist_file = st.file_uploader("หรือ อัปโหลดไฟล์ Whitelist (.txt)", type=['txt'])
    
    st.markdown("---")
    # เปลี่ยนส่วนนี้ให้ใช้ไฟล์ที่ฝังในระบบแทน
    use_blacklist = st.checkbox("ใช้คลังคำศัพท์ที่ฝังในระบบ (blacklist.txt)", value=True)
    if use_blacklist:
        if os.path.exists("blacklist.txt"):
            st.success("✅ ระบบตรวจพบไฟล์คลังคำศัพท์ที่ฝังไว้แล้ว พร้อมใช้งาน!")
        else:
            st.error("❌ ไม่พบไฟล์ 'blacklist.txt' ในระบบ (กรุณาอัปโหลดขึ้น GitHub)")

with col2:
    st.subheader("2. สั่งการและผลลัพธ์ (Action & Output)")
    special_instruction = st.text_area("✨ คำสั่งเพิ่มเติมเกี่ยวกับคำศัพท์ (ถ้ามี):", placeholder="เช่น 'คำศัพท์ต่อไปนี้คือระดับพลังทั้งหมด'", height=100)
    
    if st.button("🚀 ดำเนินการสร้างพรอมต์", type="primary", use_container_width=True):
        if not novel_file:
            st.error("❌ กรุณาอัปโหลดไฟล์นิยายก่อนครับ")
        elif not whitelist_text and not whitelist_file:
            st.error("❌ กรุณากรอกหรืออัปโหลดไฟล์ Whitelist")
        else:
            with st.spinner('กำลังประมวลผล... อาจใช้เวลาสักครู่'):
                try:
                    # อ่านไฟล์นิยาย
                    novel_content = novel_file.read().decode('utf-8-sig', errors='replace')
                    
                    # อ่าน Whitelist
                    if whitelist_file:
                        whitelist_text += "\n" + whitelist_file.read().decode('utf-8-sig', errors='replace')
                    
                    # อ่าน Blacklist ที่ฝังไว้
                    blacklist_content = ""
                    if use_blacklist and os.path.exists("blacklist.txt"):
                        with open("blacklist.txt", 'r', encoding='utf-8-sig', errors='replace') as f:
                            blacklist_content = f.read()

                    # ประมวลผล
                    final_prompt = process_data(novel_content, whitelist_text, blacklist_content, special_instruction)
                    
                    if final_prompt.startswith("❌"):
                        st.warning(final_prompt)
                    else:
                        st.success("✅ สร้างพรอมต์สำเร็จ! (ลากคลุมข้อความ หรือคลิกไอคอนกระดาษซ้อนกันที่มุมขวาบนของกล่องเพื่อ Copy)")
                        st.code(final_prompt, language="text")
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")