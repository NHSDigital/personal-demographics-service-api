from dataclasses import dataclass
from typing import List, Union


@dataclass
class Field:
    path: str
    value: Union[str, int, float]


@dataclass
class Search:
    query: List(tuple)
    expected_response_fields: List[Field]


UNICODE = Search(query=[("family", "ATTSÖN"),
                        ("given", "PÀULINÉ"),
                        ("birthdate", "1960-07-14"),
                        ("_fuzzy-match", "true")],
                 expected_response_fields=[
                     Field("entry[0].search.score", 0.9317),
                     Field("entry[0].resource.id", "9693633148"),
                     Field("entry[0].resource.gender", "female"),
                     Field("entry[0].resource.birthDate", "1960-07-14"),
                     Field("entry[0].resource.name[0].family", "attisón"),
                     Field("entry[0].resource.name[0].given[0]", "Pauline"),
                     Field("entry[1].search.score", 0.9077),
                     Field("entry[1].resource.id", "9693633121"),
                     Field("entry[1].resource.gender", "female"),
                     Field("entry[1].resource.birthDate", "1960-07-14")
                     ]
                 )

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

NO_GENDER_MULTIPLE_MATCHES = Search(query={"family", "YOUDS",
                                           "birthdate", "1970-01-24"},
                                    expected_response_fields=[
                                        Field("resourceType", "Bundle"),
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
                                        Field("entry[3].resource.gender", "other"),
                                        ]
                                    )

# FUZZY_MATCHH = Search(query=)
