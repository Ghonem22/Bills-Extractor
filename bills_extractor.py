import re
import yaml
import numpy as np
import pandas as pd

with open(r'patterns.yml') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    patterns = yaml.load(file, Loader=yaml.FullLoader)


def read_csv(file):
    return pd.read_csv(file, sep=',', header=0, encoding='unicode_escape')


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


def get_letters_pattern(pattern_txt):
    '''
    :param pattern_txt: the letters pattern written in the YAML
    :return: pattern after make it non-case sensitive with digits after it
    '''
    pattern = ''
    for l in pattern_txt:
        # HR  >> "[Hh].?[Rr].?\s?\d+"
        pattern += f'[{l.upper()}{l.lower()}]' + '.?'
    return pattern + "\s?\d+"


def extract_bills(text):
    if not text or text in ['nan', '', np.nan]:
        return text

    bills = []
    # extracting pattern like H.R. using the yaml file
    for letter in patterns['letters']:
        p = re.compile(get_letters_pattern(letter))
        bills.extend(p.findall(text))

    # extracting pattern like XXXX ACT (ex: SUBS act)
    bills.extend(re.findall(r'\b[A-Z]+\b\s[Aa][Cc][Tt]', text))

    # using yml file to extract other patterns
    for pattern in patterns['patterns']:
        results = re.findall(get_pattern(pattern), text)

        # remove any overlapping between this case and any other cases
        if results:
            for result in results:
                result_groups = result.split()
                joined_gropus = " ".join(result_groups[-2:])
                if joined_gropus in bills:
                    bills.remove(joined_gropus)

        bills.extend(results)

    if not bills:
        return ''
    else:
        return ", ".join(bills)


if __name__ == '__main__':
    # apply extract_bills function to csv file
    csv_file_path = ''
    csv_saving_path = ''
    df = read_csv(csv_file_path)
    df['bills'] = df.apply(lambda x: extract_bills(x['description']), axis=1)
    df.to_csv(csv_saving_path)
