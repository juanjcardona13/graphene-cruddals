import pytest

from graphene_cruddals.utils.main import (
    build_class,
    camel_to_snake,
    camelize,
    delete_keys,
    get_name_of_model_in_different_case,
    get_separator,
    is_iterable,
    merge_dict,
    transform_string,
    transform_string_with_separator,
)


def test_build_class():
    attrs = {"attr1": True, "method1": lambda self, x: x + 1}
    CustomClass = build_class("CustomClass", (object,), attrs)
    instance = CustomClass()
    assert instance.attr1 is True
    assert instance.method1(1) == 2


def test_build_class_without_attrs():
    CustomClass = build_class("CustomClass", (object,))
    instance = CustomClass()
    assert instance is not None


def test_delete_keys():
    original_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}
    modified_dict = delete_keys(original_dict, ["key2", "key3"])
    assert "key2" not in modified_dict
    assert "key3" not in modified_dict
    assert modified_dict == {"key1": "value1"}


def test_get_separator():
    # Test case 1: String contains a space
    s1 = "Hello World"
    assert get_separator(s1) == " "

    # Test case 2: String contains an underscore
    s2 = "hello_world"
    assert get_separator(s2) == "_"

    # Test case 3: String contains a hyphen
    s3 = "hello-world"
    assert get_separator(s3) == "-"

    # Test case 4: String contains no separator
    s4 = "helloworld"
    assert get_separator(s4) == ""

    # Test case 5: Empty string
    s5 = ""
    assert get_separator(s5) == ""

    # Test case 6: String contains a space and underscore
    s6 = "hello_world hello world"
    assert get_separator(s6) == " "


def test_transform_string_with_separator():
    # Test case 1: Convert string to PascalCase with underscore separator
    result = transform_string_with_separator("hello_world", "PascalCase", "_")
    assert result == "HelloWorld"

    # Test case 2: Convert string to snake_case with hyphen separator
    result = transform_string_with_separator("hello-world", "snake_case", "-")
    assert result == "hello_world"

    # Test case 3: Convert string to kebab-case with space separator
    result = transform_string_with_separator("hello world", "kebab-case", " ")
    assert result == "hello-world"

    # Test case 4: Convert string to lowercase with no separator
    with pytest.raises(ValueError) as exc_info:
        transform_string_with_separator("hello_world", "lowercase", "")
    assert str(exc_info.value) == "actual_separator cannot be empty."


def test_is_iterable():
    assert is_iterable([1, 2, 3]) is True
    assert is_iterable("string", exclude_string=True) is False
    assert is_iterable("string", exclude_string=False) is True


def test_camelize():
    data = {"my_key": {"nested_key": "value"}}
    camelized_data = camelize(data)
    assert camelized_data == {"myKey": {"nestedKey": "value"}}


def test_camel_to_snake():
    assert camel_to_snake("CamelCase") == "camel_case"
    assert camel_to_snake("camelCase") == "camel_case"


@pytest.mark.parametrize(
    "input_string, transformation_type, expected",
    [
        ("camelCase", "snake_case", "camel_case"),
        ("camelCase", "kebab-case", "camel-case"),
        ("camelCase", "camelCase", "camelCase"),
        ("camelCase", "PascalCase", "CamelCase"),
        ("PascalCase", "snake_case", "pascal_case"),
        ("PascalCase", "kebab-case", "pascal-case"),
        ("PascalCase", "camelCase", "pascalCase"),
        ("PascalCase", "PascalCase", "PascalCase"),
        ("snake_case", "snake_case", "snake_case"),
        ("snake_case", "kebab-case", "snake-case"),
        ("snake_case", "camelCase", "snakeCase"),
        ("snake_case", "PascalCase", "SnakeCase"),
        ("kebab-case", "snake_case", "kebab_case"),
        ("kebab-case", "kebab-case", "kebab-case"),
        ("kebab-case", "camelCase", "kebabCase"),
        ("kebab-case", "PascalCase", "KebabCase"),
    ],
)
def test_transform_string(input_string, transformation_type, expected):
    assert transform_string(input_string, transformation_type) == expected


def test_merge_dict():
    src = {"key1": "value1"}
    dest = {"key2": "value2"}
    merged = merge_dict(src, dest)
    assert "key1" in merged and "key2" in merged

    # Test case 1: Empty inputs
    result = merge_dict({}, {})
    assert result == {}

    # Test case 2: Custom inputs
    result = merge_dict({"key1": "value1"}, {"key2": "value2"})
    assert result == {"key1": "value1", "key2": "value2"}

    # Test case 3: Custom inputs with same keys, should raise value error
    with pytest.raises(ValueError):
        merge_dict({"key1": "value1"}, {"key1": "value2"})

    # Test case 4: Custom inputs with same keys with overwrite
    result = merge_dict({"key1": "value1"}, {"key1": "value2"}, overwrite=True)
    assert result == {"key1": "value2"}

    # Test case 5: Custom inputs with same keys with overwrite and different types
    result = merge_dict({"key1": "value1"}, {"key1": 2}, overwrite=True)
    assert result == {"key1": 2}

    # Test case 6: Custom inputs with same keys with overwrite and different types
    result = merge_dict({"key1": 2}, {"key1": "value1"}, overwrite=True)
    assert result == {"key1": "value1"}

    # Test case 7: Custom inputs with same keys with overwrite false and keep both
    result = merge_dict({"key1": "value1"}, {"key1": "value2"}, keep_both=True)
    assert result == {"key1": ["value1", "value2"]}

    # Test case 8: Custom inputs with nested dict
    result = merge_dict(
        {"key1": {"nested_key": "nested_value"}},
        {"key1": {"nested_key2": "nested_value2"}},
    )
    assert result == {
        "key1": {"nested_key": "nested_value", "nested_key2": "nested_value2"}
    }

    # Test case 9: Custom inputs with nested dict and overwrite
    result = merge_dict(
        {"key1": {"nested_key": "nested_value"}},
        {"key1": {"nested_key": "nested_value2"}},
        overwrite=True,
    )
    assert result == {"key1": {"nested_key": "nested_value2"}}


def test_get_name_of_model_in_different_case():
    cases = get_name_of_model_in_different_case("Model", "Models", "Pre", "Suffix")
    assert cases["snake_case"] == "pre_model_suffix"

    # Test case 1: Empty inputs, should raise value error
    with pytest.raises(ValueError):
        get_name_of_model_in_different_case("")

    # Test case 2: Custom inputs
    result = get_name_of_model_in_different_case(
        name_model="user", name_model_plural="users", prefix="pre", suffix="suf"
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
