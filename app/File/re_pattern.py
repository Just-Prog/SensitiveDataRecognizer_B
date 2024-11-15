pattern_cnphone = '1[3456789]\\d{9}'
pattern_cnphone_full = '^1[3456789]\\d{9}$'

pattern_cnid = '[1-9]\\d{5}(18|19|20)\\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\\d{3}[0-9Xx]'
pattern_cnid_full = '^[1-9]\\d{5}(18|19|20)\\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\\d{3}[0-9Xx]$'

pattern_bank = r'([1-9]{1})(\d{15,18})'
pattern_bank_full = r'^([1-9]{1})(\d{15,18})$'

pattern_email = r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+"
pattern_email_full = r"^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"

patterns = [pattern_cnid, pattern_bank, pattern_email, pattern_cnphone]
patterns_full = [pattern_cnid_full, pattern_bank_full, pattern_email_full, pattern_cnphone_full]