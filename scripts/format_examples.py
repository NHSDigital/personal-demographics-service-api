#!/usr/bin/env python
"""
Example Formatting.
"""
from copy import deepcopy


def _return_value(resource, key):
    """ Return the value from the resource """
    return resource[key]


def _process_blacklist(resource, blacklist):
    """ Process a blacklist of keys """
    new_resource = {}
    for key, value in resource.items():
        if key not in blacklist:
            new_resource[key] = value
    return new_resource


def _slim_address(resource, key):
    """ Only return the "home" address """
    return [addr for addr in resource[key] if addr["use"] == "home"]


def _slim_extension(resource, key):
    """ The only extension to return is Death Notification """
    return [
        addr for addr in resource[key]
        if addr["url"] == "https://fhir.nhs.uk/R4/StructureDefinition/Extension-UKCore-DeathNotificationStatus"
    ]


def slim_patient(resource):
    """
    Remove parts of the patient that will not be returned on a search response
    to align with how the backend actually performs.
    """

    # These are the only fields that will be populated on a search
    whitelist = {
        "resourceType": _return_value,
        "id": _return_value,
        "identifier": _return_value,
        "meta": _return_value,
        "name": _return_value,
        "gender": _return_value,
        "birthDate": _return_value,
        "deceasedDateTime": _return_value,
        "address": _slim_address,
        "generalPractitioner": _return_value
    }

    # Loop around the whitelist returning the result of mapped function.
    return {key: func(resource, key) for key, func in whitelist.items() if key in resource}


def sensitive_patient(resource):
    """
    Only include parts of the patient that will be returned on a sensitive response
    to align with how the backend actually performs.
    """

    # These are the fields that will be removed
    blacklist = [
        "address",
        "telecom",
        "generalPractitioner"
    ]

    new_resource = _process_blacklist(resource, blacklist)
    new_resource["meta"]["security"][0]["code"] = "R"
    new_resource["meta"]["security"][0]["display"] = "restricted"

    if "extension" in resource:
        new_resource["extension"] = _slim_extension(resource, "extension")

    return new_resource


def related_person_reference_only(resource):
    """
    Returning a related person resource with only the reference details
    """
    blacklist = [
        "name",
        "address",
        "telecom"
    ]
    return _process_blacklist(resource, blacklist)


def related_person_no_reference(resource):
    """
    Returning a related person resource with no reference details
    """
    new_resource = deepcopy(resource)
    new_resource["patient"] = {
        "type": "Patient"
    }
    return new_resource


def remove_list_id(resource):
    """
    Remove `id` from list fields.
    """
    list_fields = [
        "name",
        "address",
        "telecom"
    ]

    for key in list_fields:
        for element in resource[key]:
            del element["id"]

    return resource


def remove_empty_elements(obj):
    """
    Recursively traverse the dictionary removing any empty elements (eg. [] or {}).
    """
    new_obj = deepcopy(obj)
    if isinstance(obj, dict):
        for key, value in obj.items():
            sub_value = remove_empty_elements(value)
            if not sub_value and sub_value is not False:
                del new_obj[key]
            else:
                new_obj[key] = sub_value
    elif isinstance(obj, list):
        new_obj = []
        for value in obj:
            sub_value = remove_empty_elements(value)
            if sub_value or sub_value == "":
                new_obj.append(sub_value)

    return new_obj
