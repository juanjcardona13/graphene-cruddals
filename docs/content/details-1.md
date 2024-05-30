Propósito Principal de la libreria Graphene-CRUDDALS:

¿Cuál es el propósito principal de tu librería?

El propósito principal de esta librería es servir como puente o conector para crear otras libreriás que se encarguen de la creación, lectura, actualización y eliminación de datos en una base de datos, de esta manera se puede tener un código más limpio y ordenado, además de que se puede reutilizar el código en otros proyectos.
Nacio pro que yo cree otra libreria que se llama Graphene-Django-CRUDDALS (https://github.com/juanjcardona13/graphene_django_cruddals/blob/main/README.md), la cual se encarga de transformar un modelo de Django en un esquema de Graphene, pero esta libreria solo sirve para Django, por lo que decidi crear esta libreria que sirva para cualquier tipo de de dato, por eso esta libreria recibe un diccionario normal de python, junto con un set de utilidades para saber como se debe de hacer la transformación de los campos, no se si es suficientemente claro, si necesetias mas información me puedes preguntar.

¿Qué problema específico busca resolver?

El problema que busca resolver es la creación de un esquema de Graphene a partir de un diccionario de python, de esta manera se puede tener un código más limpio y ordenado, además de que se puede reutilizar el código en otros proyectos.

# Funcionalidades Principales:
¿Cuáles son las funcionalidades principales que ofrece?

Pues como tal, no ofrece un set de funcionalidades, si no que como decia anteriormente, ayuda a poder construir herramientas como Graphene-Django-CRUDDALS, de una manera mas rapida y sencilla, por que solicita todo lo que se necesita para esto y lo conecta.

¿Qué operaciones CRUD soporta y cómo lo hace?

Como tal no soporta ninguna operación CRUD, si no que ayuda a construir herramientas que soporten estas operaciones, por ejemplo Graphene-Django-CRUDDALS, soporta todas las operaciones CRUD, y esta libreria ayuda a construir herramientas como esta.

# Tecnologías Utilizadas:
¿Está construida sobre alguna tecnología específica (por ejemplo, algún framework o biblioteca de Python)?

Si, esta construida sobre la libreria de Graphene.

¿Requiere dependencias específicas?

Si, requiere la libreria de Graphene.

# Casos de Uso:
¿Puedes dar ejemplos de casos de uso comunes?

Casos de uso comunes serian, construir cualqueir libreria en python para la creación de un esquema de Graphene, a partir de un diccionario de python, entonce podria crearse FastApi-CRUDDALS, Flask-CRUDDALS, etc, por que se podria tomar un modelo de Pydantic o de SQLAlchemy y convertirlo en un diccionario, definir los resolvers y listo, se crearia una nueva libreria capaz de tomar un modelo del tipo que sea y convertirlo en un esquema de Graphene con todas las operaciones CRUD y mas.

¿Para qué tipo de aplicaciones o proyectos es más útil?

Es util, solo para desarrolladores que quiera crear una libreria que se encargue de la creación de un esquema de Graphene a partir de un modelo de su ORM favorito, por ejemplo, si alguien quiere crear una libreria que se encargue de la creación de un esquema de Graphene a partir de un modelo de Pydantic, entonces esta libreria le seria de mucha ayuda.

# Instalación:
¿Cómo se instala la librería?

Se instala con pip, pip install graphene-cruddals

¿Qué requisitos previos debe cumplir el usuario?

Debe tener instalado python y pip y Debe de tener un gran conocimiento de como funciona graphql y graphene.

# Configuración y Personalización:
¿Qué nivel de configuración o personalización permite la librería?

Permite una gran cantidad de configuración y personalización, ya que se puede definir como se deben de transformar los campos, como se deben de transformar los resolvers, como se deben de transformar los argumentos, etc.

¿Hay archivos de configuración o parámetros importantes que el usuario deba conocer?

Si, el usuario debe de conocer esta dataclass:

```python
  @dataclass
  class CruddalsBuilderConfig:
      model: Type
      pascal_case_name: str

      get_fields_for_output: Callable[[Type], Dict[str, Any]]
      output_field_converter_function: Callable[[str, Any, RegistryGlobal], GRAPHENE_TYPE]

      get_fields_for_input: Callable[[Type], Dict[str, Any]]
      input_field_converter_function: Callable[[str, Any, RegistryGlobal], GRAPHENE_TYPE]

      get_fields_for_create_input: Callable[[Type], Dict[str, Any]]
      create_input_field_converter_function: Callable[
          [str, Any, RegistryGlobal], GRAPHENE_TYPE
      ]

      get_fields_for_update_input: Callable[[Type], Dict[str, Any]]
      update_input_field_converter_function: Callable[
          [str, Any, RegistryGlobal], GRAPHENE_TYPE
      ]

      get_fields_for_filter: Callable[[Type], Dict[str, Any]]
      filter_field_converter_function: Callable[[str, Any, RegistryGlobal], GRAPHENE_TYPE]

      get_fields_for_order_by: Callable[[Type], Dict[str, Any]]
      order_by_field_converter_function: Callable[
          [str, Any, RegistryGlobal], GRAPHENE_TYPE
      ]

      create_resolver: Callable[..., Any]
      read_resolver: Callable[..., Any]
      update_resolver: Callable[..., Any]
      delete_resolver: Callable[..., Any]
      deactivate_resolver: Callable[..., Any]
      activate_resolver: Callable[..., Any]
      list_resolver: Callable[..., Any]
      search_resolver: Callable[..., Any]

      plural_pascal_case_name: Union[str, None] = None
      prefix: str = ""
      suffix: str = ""
      cruddals_interfaces: Union[Tuple[Type[Any], ...], None] = None
      exclude_cruddals_interfaces: Union[Tuple[str, ...], None] = None
      registry: Union[RegistryGlobal, None] = None
```


# Documentación y Soporte:
¿Existe documentación adicional o ejemplos de uso?

No

¿Ofreces algún tipo de soporte o comunidad para los usuarios?

Si, se puede contactar conmigo en mi correo