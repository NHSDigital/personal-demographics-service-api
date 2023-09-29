from dataclasses import dataclass
from typing import List, Union


@dataclass
class Field:
    path: str
    expected_value: Union[str, int, float]


@dataclass
class Search:
    query: List[tuple]
    expected_response_fields: List[Field]


DEFAULT = Search(query=[("family", "Capon"),
                        ("gender", "male"),
                        ("birthdate", "eq1953-05-29")],
                 expected_response_fields=[Field("entry[0].resource.id", "9693632117")])

SENSITIVE = Search(query=[("family", "Godsoe"),
                          ("gender", "male"),
                          ("birthdate", "eq1936-02-24")],
                   expected_response_fields=[Field("entry[0].resource.id", "9693632125")])

UNKNOWN_GENDER = Search(query=[("family", "Massam"), ("birthdate", "eq1920-08-11")],
                        expected_response_fields=[Field("entry[0].resource.id", "9693632966")])

DOB_RANGE = Search(query=[("family", "Massam"),
                          ("birthdate", "le1920-08-11")],
                   expected_response_fields=[Field("entry[0].resource.id", "9693632966")])

VAGUE = Search(query=[("family", "YOUDS"),
                      ("birthdate", "1970-01-24")],
               expected_response_fields=[Field("type", "searchset"),
                                         Field("resourceType", "Bundle"),
                                         Field("total", 4),
                                         Field("entry[*].search.score", 1),
                                         Field("entry[*].resource.birthDate", "1970-01-24"),
                                         Field("entry[0].resource.id", "9693633679"),
                                         Field("entry[0].resource.gender", "male"),
                                         Field("entry[1].resource.id", "9693633687"),
                                         Field("entry[1].resource.gender", "female"),
                                         Field("entry[2].resource.id", "9693633695"),
                                         Field("entry[2].resource.gender", "unknown"),
                                         Field("entry[3].resource.id", "9693633709"),
                                         Field("entry[3].resource.gender", "other")])

UNICODE = Search(query=[("family", "ATTSÖN"),
                        ("given", "PÀULINÉ"),
                        ("birthdate", "1960-07-14"),
                        ("_fuzzy-match", "true")],
                 expected_response_fields=[Field("entry[0].search.score", 0.9317),
                                           Field("entry[0].resource.id", "9693633148"),
                                           Field("entry[0].resource.gender", "female"),
                                           Field("entry[0].resource.birthDate", "1960-07-14"),
                                           Field("entry[0].resource.name[0].family", "attisón"),
                                           Field("entry[0].resource.name[0].given[0]", "Pauline"),
                                           Field("entry[1].search.score", 0.9077),
                                           Field("entry[1].resource.id", "9693633121"),
                                           Field("entry[1].resource.gender", "female"),
                                           Field("entry[1].resource.birthDate", "1960-07-14")])

DOB_UPPER_AND_LOWER_RANGE = Search(query=[('family', 'Garton'),
                                          ('given', 'Bill'),
                                          ('birthdate', 'le1990-01-01'),
                                          ('birthdate', 'ge1946-01-19'),
                                          ('_fuzzy-match', 'true')],
                                   expected_response_fields=[
                                       Field("type", "searchset"),
                                       Field("resourceType", "Bundle"),
                                       Field("entry[0].search.score", 1),
                                       Field("entry[0].resource.id", "9693632109")
                                       ]
                                   )

NO_GENDER_MULTIPLE_MATCHES = Search(query=[("family", "YOUDS"),
                                           ("birthdate", "1970-01-24")],
                                    expected_response_fields=[Field("resourceType", "Bundle"),
                                                              Field("type", "searchset"),
                                                              Field("total", 4),
                                                              Field("entry[*].search.score", 1),
                                                              Field("entry[*].resource.birthDate", "1970-01-24"),
                                                              Field("entry[0].resource.id", "9693633679"),
                                                              Field("entry[0].resource.gender", "male"),
                                                              Field("entry[1].resource.id", "9693633687"),
                                                              Field("entry[1].resource.gender", "female"),
                                                              Field("entry[2].resource.id", "9693633695"),
                                                              Field("entry[2].resource.gender", "unknown"),
                                                              Field("entry[3].resource.id", "9693633709"),
                                                              Field("entry[3].resource.gender", "other")])

FUZZY = Search(query=[("family", "Garton"),
                      ("given", "Bill"),
                      ("birthdate", "1946-06-23")],
               expected_response_fields=[Field("type", "searchset"),
                                         Field("resourceType", "Bundle"),
                                         Field("entry[0].resource.id", "9693632109"),
                                         Field("entry[0].search.score", 1)])
