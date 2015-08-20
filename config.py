import re


class RegExMap:
    def __init__(self, lines):
        regex_dict = self.regex_dict = {}
        for line in lines:
            field, replace_str, find_regex = line.split()
            existing_rules = regex_dict.get(field, [])
            existing_rules.append((replace_str, re.compile(find_regex)))
            regex_dict[field] = existing_rules

    def apply_to(self, input_dict):
        output_dict = {}
        for field in input_dict.iterkeys():
            output_dict[field] = input_dict[field]
            if field in self.regex_dict:
                for replace_str, regex in self.regex_dict[field]:
                    if regex.match(output_dict[field]):
                        if replace_str[0] == '~':
                            return None
                        output_dict[field] = regex.sub(replace_str, output_dict[field])
                        break
        return output_dict


class Config:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as file:
            data = file.read()
        self.data = data
        self.config_dict = {}
        self.parse()

    def get(self, field, mandatory=False):
        if mandatory and field not in self.config_dict:
            raise Exception("Mandatory config section [%s] is msising!" % field)
        return self.config_dict.get(field)

    def parse(self):
        section_name = None
        for line in self.data.splitlines():
            line = line.split('#', 1)[0]
            if not line:
                continue
            if line[0] == '[':
                section_name = line.strip('[]')
                self.config_dict[section_name] = []
            else:
                self.config_dict[section_name].append(line)

    def regex_map(self, section_name):
        return RegExMap(self.get(section_name) or [])
