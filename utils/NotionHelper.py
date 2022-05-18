from xml.sax.handler import property_xml_string


class NotionHelper:
    def __init__(self, props):
        self.props = props

    def get_title(self, name):
        if type(name) != str:
            raise ValueError("Input argument has to be of type string.")

        out = ""
        try:
            out = self.props[name]["title"][0]["plain_text"]
        finally:
            return out

    def get_rich_text(self, name):
        if type(name) != str:
            raise ValueError("Input argument has to be of type string.")

        out = ""
        try:
            out = self.props[name]["rich_text"][0]["plain_text"]
        finally:
            return out

    def get_multi_select(self, name):
        if type(name) != str:
            raise ValueError("Input argument has to be of type string.")

        out = []
        try:
            items = self.props[name]["multi_select"]
            for item in items:
                out.append(item["name"])
        finally:
            return out
            