import sys
import json


def generate_example(schema_dict, path):
    example = {}

    for property_name, property_value in schema_dict.items():
        if property_value['type'] == 'array':
            if property_value['items']['type'] == 'object':
                example[property_name] = [generate_example(property_value['items']['properties'], property_name)]
            else:
                if ('example' not in property_value) and ('default' not in property_value):
                    property_path = '.'.join(path)
                    raise RuntimeError(f'Patient.{property_path}.{property_name} has no example or default!')
                example[property_name] = property_value.get('example', property_value.get('default'))
        elif property_value['type'] == 'object':
            example[property_name] = generate_example(property_value['properties'], property_name)
        else:
            if ('example' not in property_value) and ('default' not in property_value):
                property_path = '.'.join(path)
                raise RuntimeError(f'Patient.{property_path}.{property_name} has no example or default!')
            example[property_name] = property_value.get('example', property_value.get('default'))

    return example


if __name__ == "__main__":
    spec = json.loads(sys.stdin.read())
    patient_spec = spec['components']['schemas']['Patient']['properties']
    print(json.dumps(generate_example(patient_spec, ['Patient'])))
