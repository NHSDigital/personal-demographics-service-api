#!/usr/bin/env python
"""
Example Formatting.
"""
from copy import deepcopy


def _return_value(resource, key):
    """ Return the value from the resource """
    return resource[key]


def _format_telecom(resource, key, add_textphone_extension=True, whitelist=None):
    """
    Return the telecom field with the correct values.
    Optionally adds additional emergency contact telecoms to ensure all
    varieties are covered in the response.
    """
    if not whitelist:
        whitelist = ["extension"]

    telecoms = resource.pop(key)

    resource[key] = []
    for telecom in deepcopy(telecoms):
        for key_to_delete in whitelist:
            # Removing certain fields - for example extension is not needed when
            # a use field is present.
            del telecom[key_to_delete]
        resource[key].append(telecom)

    # Adding the emergency contact telecoms details.
    if add_textphone_extension:
        for telecom in deepcopy(telecoms):
            if "id" not in telecom:
                continue

            telecom["system"] = "other"

            # Ids need to be unique.
            telecom["id"] = "OC{}".format(telecom["id"])
            resource[key].append(telecom)

    return resource[key]


def _format_contact(resource, key):
    """
    Return the contact field with the correct values.
    This is mainly stripping out the unecessary fields from the telecom part of
    the response.
    """
    contacts = resource.pop(key)

    resource[key] = []
    for contact in contacts:
        contact["telecom"] = _format_telecom(
            contact,
            "telecom",
            add_textphone_extension=False,
            whitelist=["id", "use", "period", "extension"]
        )
        resource[key].append(contact)

    return resource[key]


def _format_address(resource, key):
    """
    Return the address field with the correct values.
    """
    addresses = resource.pop(key)

    resource[key] = []
    for addr in addresses:
        temp_address = None
        if addr["use"] == "home":
            temp_address = deepcopy(addr)
            temp_address["use"] = "temp"
            if "id" in temp_address:
                temp_address["id"] = "T{}".format(temp_address["id"])

            # Remove 'text' from the home address as it should not have
            # a description.
            del addr["text"]

        resource[key].append(addr)
        if temp_address:
            resource[key].append(temp_address)

    return resource[key]


def _process_whitelist(resource, whitelist):
    """ Process a whitelist of keys """
    new_resource = {}
    for key, value in resource.items():
        if key in whitelist:
            new_resource[key] = value
    return new_resource


def _process_blacklist(resource, blacklist):
    """ Process a blacklist of keys """
    new_resource = {}
    for key, value in resource.items():
        if key not in blacklist:
            new_resource[key] = value
    return new_resource


def _slim_address(resource, key):
    """ Only return the "home" address """
    address = _format_address(resource, key)
    resource[key] = address
    return [addr for addr in resource[key] if addr["use"] == "home"]


def _slim_extension(resource, key):
    """ The only extension to return is Death Notification """
    return [
        addr for addr in resource[key]
        if addr["url"] == "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus"
    ]


def format_patient(resource):
    """
    Format the patient
    """
    formatters = {
        "telecom": _format_telecom,
        "contact": _format_contact,
        "address": _format_address,
    }

    for key, func in formatters.items():
        resource[key] = func(resource, key)
    return resource


def minimal_patient(resource):
    """
    Remove all but the mandatory details on the patient
    """
    whitelist = {
        "id",
        "identifier",
        "meta",
        "resourceType"
    }
    return _process_whitelist(resource, whitelist)


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
        "multipleBirthInteger": _return_value,
        "deceasedDateTime": _return_value,
        "address": _slim_address,
        "telecom": _format_telecom,
        "contact": _format_contact,
        "generalPractitioner": _return_value,
        "extension": _slim_extension
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
        "contact",
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
        "telecom",
        "contact"
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

    formatters = {
        "telecom": _format_telecom,
        "address": _slim_address
    }

    for key in list_fields:
        for element in resource[key]:
            del element["id"]

    for key, func in formatters.items():
        resource[key] = func(resource, key)

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
