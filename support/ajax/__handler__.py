#
# testing


from draco2.draco import DracoHandler

from lxml.etree import ElementTree, Element, SubElement

def create_formresult(status, message, fields):
    top = Element('formresult')
    stel = SubElement(top, 'status')
    stel.text = status
    msgel = SubElement(top, 'message')
    msgel.text = message
    for field in fields:
        fldel = SubElement(top, 'field')
        fldel.text = field
    tree = ElementTree(top)
    return tree

class TestHandler(DracoHandler):


    def form(self, api):
        pass

    def _xml_response(self, api, tree):
        output = tree.write_str()
        response = api.response
        response.set_template(None)
        response.set_buffering(False)
        response.set_header('content-type', 'text/xml')
        response.set_header('content-length', str(len(output)))
        print output
        response.write(output)

    def submit(self, api):
        args = api.request.args()
        status = 'nok'
        message = 'Submitted data: %s' % str(args.values())
        fields = ['surname']
        tree = create_formresult(status, message, fields)
        self._xml_response(api, tree)
