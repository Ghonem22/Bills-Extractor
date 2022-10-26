import re
import yaml

with open(r'patterns.yml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    patterns = yaml.load(file, Loader=yaml.FullLoader)


def get_pattern(pattern_txt):
    '''
    :param pattern_txt: the pattern written in the YAML
    :return: pattern after we decoded it to be non case sensitive and the special letters to be optional
    '''

    regex = re.compile('[.@_!#$%^&*()<>?/\|}{~:]')
    special_chars = regex.findall(pattern_txt)
    pattern = ''
    for l in pattern_txt:
        if l in special_chars:
            pattern += l + '?'
        elif l == ' ':
            pattern += l
        else:
            pattern += f'[{l.upper()}{l.lower()}]'
    return pattern

def extract_bills(text):
    bills = []
    # extracting pattern like H.R. (H.R. 2062)
    p1 = re.compile("[Hh].?[Rr].?\s?\d+")
    bills.extend(p1.findall(text))

    # extracting pattern like PL (PL 115-97)
    p2 = re.compile("[pP].?[lL].?\s?\d+-\d+")
    bills.extend(p2.findall(text))

    # extracting pattern like S. (S. 1012)
    p3 = re.compile("[Ss].?\s?\d+")
    bills.extend(p3.findall(text))

    # extracting pattern like XXXX ACT (ex: SUBS act)
    bills.extend(re.findall(r'\b\w{4}\b\s[Aa][Cc][Tt]', text))

    # using yml file to extract other patterns
    for pattern in patterns['patterns']:
        results = re.findall(get_pattern(pattern),text)

        # remove any overlapping between this case and any other cases
        if results:
            for result in results:
                result_groups = result.split()
                joined_gropus = " ".join(result_groups[-2:])
                if joined_gropus in bills:
                    bills.remove(joined_gropus)

        bills.extend(results)
    return bills

