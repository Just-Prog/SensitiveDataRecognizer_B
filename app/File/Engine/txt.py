import re
from loguru import logger
from io import BytesIO
from ..re_pattern import patterns


def text_process(file, useless1, useless2, useless3):
    ori_text = file.read()
    file.close()
    text = str(ori_text.decode('utf-8'))
    for p in patterns:
        s = re.search(p, text)
        if s:
            if len(s.group()) <= 8:
                text = re.sub(p,'X'*len(s.group()),text)
            else:
                text = text[:s.start()+3]+'X'*(len(s.group())-6)+text[s.end()-3:]
    new_text = BytesIO()
    new_text.write(text.encode('utf-8'))
    new_text.seek(0)
    return new_text
