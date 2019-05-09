import sys
import io
import csv
import yaml

header = '''##
##
## Use ## for comments and # for configuration. Paste CSV below.
## The following names are reserved and should not be used (or ignored):
## id, tooltip, placeholder(s), link and label (see below)
##
#
## Node label with placeholders and HTML.
## Default is '%name_of_first_column%'.
#
# label: <i style="color:gray;">%node_id%</i><br><i style="color:blue;">%type%</i><br>%node_label%<br>%attributes%
#
## Node style (placeholders are replaced once).
## Default is the current style for nodes.
#
# style: whiteSpace=wrap;html=1;rounded=1;fillColor=%fill%;strokeColor=#999999;
#
## Uses the given column name as the identity for cells (updates existing cells).
## Default is no identity (empty value or -).
#
# identity: node_id
#
## Connections between rows ("from": source colum, "to": target column).
## Label, style and invert are optional. Defaults are '', current style and false.
## In addition to label, an optional fromlabel and tolabel can be used to name the column
## that contains the text for the label in the edges source or target (invert ignored).
## The label is concatenated in the form fromlabel + label + tolabel if all are defined.
## The target column may contain a comma-separated list of values.
## Multiple connect entries are allowed.
#
## connect: {"from": "manager", "to": "name", "invert": true, "label": "manages", \
##          "style": "curved=1;endArrow=blockThin;endFill=1;fontSize=11;"}
# connect: {"from": "parent", "to": "node_id", "style": "curved=1;fontSize=11;", "invert": true, "fromlabel": "parent_label"}
#
## Node x-coordinate. Possible value is a column name. Default is empty. Layouts will
## override this value.
#
# left: 
#
## Node y-coordinate. Possible value is a column name. Default is empty. Layouts will
## override this value.
#
# top: 
#
## Node width. Possible value is a number (in px), auto or an @ sign followed by a column
## name that contains the value for the width. Default is auto.
#
# width: auto
#
## Node height. Possible value is a number (in px), auto or an @ sign followed by a column
## name that contains the value for the height. Default is auto.
#
# height: auto
#
## Padding for autosize. Default is 0.
#
# padding: 0
#
## Comma-separated list of ignored columns for metadata. (These can be
## used for connections and styles but will not be added as metadata.)
#
# ignore: id,image,stroke
#
## Column to be renamed to link attribute (used as link).
#
# link: url
#
## Spacing between nodes. Default is 40.
#
# nodespacing: 40
#
## Spacing between parallel edges. Default is 40.
#
# edgespacing: 40
#
## Name of layout. Possible values are auto, none, verticaltree, horizontaltree,
## verticalflow, horizontalflow, organic, circle. Default is auto.
#
# layout: verticalflow
#
## ---- CSV below this line. First line are column names. ----
'''.rstrip()

all_rows = []
objs_by_id = {}
empty_item = '<span></span>'

type_colors = {
    'Code': 'MistyRose',
    'Gene': 'MistyRose',
    'CanonicalAllele': 'MistyRose',
    'FunctionalAssayInstance': '#90EE90',
    'GeneticCondition': '#90EE90',
    'Agent': 'Khaki',
    'Contribution': 'Khaki',
    'EvidenceLine': 'Khaki',
    'CriterionAssessment': 'LightSkyBlue',
    'AlleleFunctionalImpactStatement': 'LightSkyBlue',
    'AlleleFunctionalImpactMeasurementStatement': 'LightSkyBlue',
    'FunctionalImpactMeasurementStatement': 'LightSkyBlue',
    'FunctionalAssayEvaluatesPathogenicity': 'Lavender'
}

def visit_object(n, parent='', parent_label=''):
    global all_rows
    global objs_by_id
    row = {}
    row['node_id'] = n.get('id', '')
    if row['node_id'] in objs_by_id:
        row = dict(objs_by_id[row['node_id']])
        row['parent'] = parent
        row['parent_label'] = parent_label
        all_rows.append(row)
        return row
    row['type'] = n.get('type', empty_item)
    row['node_label'] = n.get('label', empty_item)
    row['description'] = n.get('description', empty_item)
    row['parent'] = parent
    row['parent_label'] = parent_label
    row['fill'] = type_colors.get(row['type'], '#ffffff')
    attributes = {}
    for k,v in n.items():
        if k in ('id', 'type', 'label'):
            continue
        if isinstance(v, dict):
            subrow = visit_object(v, row['node_id'], k)
            #attributes[k] = subrow['node_id']
        elif isinstance(v, list):
            attributes[k] = []
            for i in v:
                if isinstance(i, dict):
                    subrow = visit_object(i, row['node_id'], k)
                    #attributes[k].append(subrow['node_id'])
                else:
                    attributes[k].append(i)
            attributes[k] = '<br>'.join(attributes[k])
            if len(attributes[k]) == 0:
                del(attributes[k])
        else:
            attributes[k] = str(v)
    #row['attributes'] = '<br>'.join('%s: %s'%(k,v) for (k,v) in attributes.items())
    row['attributes'] = '<table border=1><tr>' + '</tr><tr>'.join('<td>%s</td><td>%s</td>'%(k,v) for (k,v) in attributes.items()) + '</tr></table>'
    if len(row['attributes']) < 34:
        row['attributes'] = '<span></span>'
    objs_by_id[row['node_id']] = row
    all_rows.append(row)
    return row

y = yaml.safe_load(sys.stdin)
visit_object(y)

si = io.StringIO()
w = csv.DictWriter(si, 'node_id,type,node_label,description,attributes,fill,parent,parent_label'.split(','))
w.writeheader()
w.writerows(all_rows)

print(header)
print(si.getvalue())