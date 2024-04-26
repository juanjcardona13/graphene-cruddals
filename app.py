from flask import Flask
from graphql_server.flask import GraphQLView

import graphene

from graphene_cruddals.main import CruddalsBuilderConfig, CruddalsModel



people = []

person_model = {
    "id": str,
    "first_name": str,
    "last_name": str,
}

def create_people(root, info, **kw):
    list_people = kw.get("input", [])
    for person in list_people:
        person["id"] = str(len(people) + 1)
        people.append(person)
    return {"objects": list_people}

def read_person(root, info, **kw):
    where = kw.get("where", {})
    for person in people:
        if person["id"] == where.get("id"):
            return person
    return None

def update_people(root, info, **kw):
    list_people = kw.get("input", [])
    for person in list_people:
        for i, person_ in enumerate(people):
            if person_["id"] == person["id"]:
                people[i] = person
    return {"objects": list_people}

def delete_people(root, info, **kw):
    where = kw.get("where", {})
    for i, person in enumerate(people):
        if person["id"] == where.get("id"):
            people.pop(i)
    return {"objects": people}

def deactivate_people(root, info, **kw):
    where = kw.get("where", {})
    for i, person in enumerate(people):
        if person["id"] == where.get("id"):
            people[i]["is_active"] = False
    return {"objects": people}

def activate_people(root, info, **kw):
    where = kw.get("where", {})
    for i, person in enumerate(people):
        if person["id"] == where.get("id"):
            people[i]["is_active"] = True
    return {"objects": people}

def list_people(root, info, **kw):
    return people

def search_people(root, info, **kw):
    # TODa: Test pagination and others
    return {"total": len(people), "objects": people}

cruddals_config = CruddalsBuilderConfig(
    model=person_model,
    pascal_case_name="Person",
    
    output_field_converter_function=lambda x: graphene.String(),
    input_field_converter_function=lambda x: graphene.String(),
    create_input_field_converter_function=lambda x: graphene.String(),
    update_input_field_converter_function=lambda x: graphene.String(),
    filter_field_converter_function=lambda x: graphene.String(),
    order_by_field_converter_function=lambda x: graphene.String(),

    create_resolver=create_people,
    read_resolver=read_person,
    update_resolver=update_people,
    delete_resolver=delete_people,
    deactivate_resolver=deactivate_people,
    activate_resolver=activate_people,
    list_resolver=list_people,
    search_resolver=search_people,

    prefix="",
    suffix="",
    
    interfaces=(),
    exclude_interfaces=(),
    registry=None,
)

class FinalCruddalsModel(CruddalsModel):
    class Meta:
        config = cruddals_config

schema = FinalCruddalsModel.schema




app = Flask(__name__)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view( 'graphql', schema=schema, graphiql=True, ))

if __name__ == '__main__':
    app.run()
