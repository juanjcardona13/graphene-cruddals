import pytest
import graphene
from graphene_cruddals.utils.main import build_class, delete_keys, is_iterable, camelize, camel_to_snake, transform_string, merge_dict, get_name_of_model_in_different_case, exists_conversion_for_model, get_converted_model, validate_list_func_cruddals, get_schema_query_mutation

# Tests for build_class function
def test_build_class():
    attrs = {'attr1': True, 'method1': lambda self, x: x + 1}
    CustomClass = build_class('CustomClass', (object,), attrs)
    instance = CustomClass()
    assert instance.attr1 == True
    assert instance.method1(1) == 2

# Tests for delete_keys function
def test_delete_keys():
    original_dict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    modified_dict = delete_keys(original_dict, ['key2', 'key3'])
    assert 'key2' not in modified_dict
    assert 'key3' not in modified_dict
    assert modified_dict == {'key1': 'value1'}

# Tests for is_iterable function
def test_is_iterable():
    assert is_iterable([1, 2, 3]) == True
    assert is_iterable("string", exclude_string=True) == False
    assert is_iterable("string", exclude_string=False) == True

# Tests for camelize function
def test_camelize():
    data = {'my_key': {'nested_key': 'value'}}
    camelized_data = camelize(data)
    assert camelized_data == {'myKey': {'nestedKey': 'value'}}

# Tests for camel_to_snake function
def test_camel_to_snake():
    assert camel_to_snake('CamelCase') == 'camel_case'
    assert camel_to_snake('camelCase') == 'camel_case'

# Tests for transform_string function
@pytest.mark.parametrize("input_string, transformation_type, expected", [
    ("CamelCase", "snake_case", "camel_case"),
    ("snake_case", "PascalCase", "SnakeCase"),
    ("kebab-case", "camelCase", "kebabCase"),
])
def test_transform_string(input_string, transformation_type, expected):
    assert transform_string(input_string, transformation_type) == expected

# Tests for merge_dict function
def test_merge_dict():
    src = {'key1': 'value1'}
    dest = {'key2': 'value2'}
    merged = merge_dict(src, dest)
    assert 'key1' in merged and 'key2' in merged

    # Test case 1: Empty inputs
    result = merge_dict({}, {})
    assert result == {}

    # Test case 2: Custom inputs
    result = merge_dict({'key1': 'value1'}, {'key2': 'value2'})
    assert result == {'key1': 'value1', 'key2': 'value2'}

    # Test case 3: Custom inputs with same keys, should raise value error
    with pytest.raises(ValueError):
        merge_dict({'key1': 'value1'}, {'key1': 'value2'})

    # Test case 4: Custom inputs with same keys with overwrite
    result = merge_dict({'key1': 'value1'}, {'key1': 'value2'}, overwrite=True)
    assert result == {'key1': 'value2'}

    # Test case 5: Custom inputs with same keys with overwrite and different types
    result = merge_dict({'key1': 'value1'}, {'key1': 2}, overwrite=True)
    assert result == {'key1': 2}

    # Test case 6: Custom inputs with same keys with overwrite and different types
    result = merge_dict({'key1': 2}, {'key1': 'value1'}, overwrite=True)
    assert result == {'key1': 'value1'}

    # Test case 7: Custom inputs with same keys with overwrite false and keep both
    result = merge_dict({'key1': 'value1'}, {'key1': 'value2'}, keep_both=True)
    assert result == {'key1': ['value1', 'value2']}

    # Test case 8: Custom inputs with nested dict
    result = merge_dict({'key1': {'nested_key': 'nested_value'}}, {'key1': {'nested_key2': 'nested_value2'}})
    assert result == {'key1': {'nested_key': 'nested_value', 'nested_key2': 'nested_value2'}}

    # Test case 9: Custom inputs with nested dict and overwrite
    result = merge_dict({'key1': {'nested_key': 'nested_value'}}, {'key1': {'nested_key': 'nested_value2'}}, overwrite=True)
    assert result == {'key1': {'nested_key': 'nested_value2'}}



# Tests for get_name_of_model_in_different_case function
def test_get_name_of_model_in_different_case():
    cases = get_name_of_model_in_different_case("Model", "Models", "Pre", "Suffix")
    assert cases['snake_case'] == 'pre_model_suffix'

    # Test case 1: Empty inputs, should raise value error
    with pytest.raises(ValueError):
        get_name_of_model_in_different_case("")

    # Test case 2: Custom inputs
    result = get_name_of_model_in_different_case(
        name_model="user",
        name_model_plural="users",
        prefix="pre",
        suffix="suf"
    )
    assert result == {
        "snake_case": "pre_user_suf",
        "plural_snake_case": "pre_users_suf",
        "camel_case": "preUserSuf",
        "plural_camel_case": "preUsersSuf",
        "pascal_case": "PreUserSuf",
        "plural_pascal_case": "PreUsersSuf",
    }

    # Test case 3: Only name_model input
    result = get_name_of_model_in_different_case(name_model="product")
    assert result == {
        "snake_case": "product",
        "plural_snake_case": "products",
        "camel_case": "product",
        "plural_camel_case": "products",
        "pascal_case": "Product",
        "plural_pascal_case": "Products",
    }


