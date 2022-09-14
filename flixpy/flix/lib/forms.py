import collections
import dataclasses
import math
import re
import urllib.parse
from typing import Any, Generic, TypeVar

import asyncclick as click


__all__ = [
    "Form",
    "Field",
    "StringField",
    "IntField",
    "FloatField",
    "BoolField",
    "EnumField",
    "MultichoiceField",
    "Choice",
    "prompt_enum",
]


class Form:
    """This class can be used to validate data against a Flix creation form,
    or to prompt a user for input to construct or modify an object adhering to a creation form."""

    _TYPES = {
        "string": lambda _: StringField,
        "int": lambda _: IntField,
        "float": lambda _: FloatField,
        "bool": lambda _: BoolField,
        "multichoice": lambda field: (
            MultichoiceField if field.get("multi_select_allowed") else EnumField
        ),
    }

    def __init__(self, spec: dict[str, Any]):
        """
        Constructs a new Form.

        :param spec: A creation form as returned by a /form Flix endpoint
        """
        self.fields: collections.OrderedDict[str, Field] = collections.OrderedDict()
        self._read_fields(spec["elements"])

    def _read_fields(self, section):
        for field in section:
            if "elements" in field:
                self._read_fields(field["elements"])
            else:
                field_type = Form._TYPES[field["type"]](field)
                self.fields[field["id"]] = field_type(field)

    def verify(self, parameters: dict[str, Any], ignore_required=False):
        """
        Validates the given object against the creation form.

        :param parameters: The object to validate
        :param ignore_required: If true, no error will be raised for missing required parameters
        :raises ValueError: If the object does not adhere to the creation form
        """
        for field in self.fields.values():
            field.verify(parameters, ignore_required=ignore_required)

    def prompt(self, parameters: dict[str, Any] = None) -> dict[str, Any]:
        """
        Prompt the user for input required to construct an object adhering to this creation form.

        :param parameters: An optional partial object; only parameters not already set will be queried
        :raises ValueError: If a partial object was passed, and the set fields are not valid
        :return: A new instance of the object type described by this creation form
        """
        parameters = parameters or {}
        self.verify(parameters, ignore_required=True)

        for field in self.fields.values():
            if field.id not in parameters:
                parameters[field.id] = field.prompt()
        return parameters

    def prompt_edit(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """
        Prompt the user for input to modify an existing object adhering to this creation form.

        :param parameters: A fully-constructed instance of the object type described by this creation form
        :return: The given object, modified according to user input
        """
        while True:
            option = prompt_enum(
                [
                    Choice(
                        field_id,
                        f"{field.label}: {field.format(parameters.get(field_id))}",
                    )
                    for field_id, field in self.fields.items()
                ],
                prompt="Select field to edit, or press ENTER to save",
                allow_empty=True,
            )
            if option is None:
                break
            else:
                parameters[option] = self.fields[option].prompt()
        return parameters

    def print(self, parameters: dict[str, Any]):
        """
        Pretty-print an instance of the object type defined by this form.

        :param parameters: The object to print
        """
        for name, field in self.fields.items():
            if name in parameters:
                click.echo("{}: {}".format(field.label, field.format(parameters[name])))


class Field:
    """A generic form field."""

    def __init__(self, spec):
        self.label = spec["label"]
        self.id = spec["id"]
        self.type = spec["type"]
        self.required = spec.get("required", False)
        self.default = spec.get("default")

    def verify(self, parameters, ignore_required=False):
        if self.id not in parameters:
            if self.required and self.default is None and not ignore_required:
                raise ValueError("missing required field {}".format(self.id))
            return

        try:
            self.verify_value(parameters[self.id])
        except ValueError as e:
            raise ValueError("{}: {}".format(self.id, str(e))) from e

    def verify_value(self, value):
        raise NotImplementedError

    def prompt(self):
        raise NotImplementedError

    def format(self, value):
        return str(value)


class StringField(Field):
    """A string field."""

    def __init__(self, spec):
        super().__init__(spec)

        self.minimum = spec.get("minimum", -math.inf)
        self.maximum = spec.get("maximum", math.inf)
        self.format_type = spec.get("format")
        self.format_pattern = spec.get("format_value")

    def verify_value(self, value):
        if not isinstance(value, str):
            raise ValueError("not a string: {}".format(value))

        if len(value) < self.minimum:
            raise ValueError(
                "string must be at least {} characters: {}".format(self.minimum, value)
            )
        elif len(value) > self.maximum:
            raise ValueError(
                "string can be at most {} characters: {}".format(self.maximum, value)
            )
        elif self.format_type == "regex":
            if not re.match(self.format_pattern, value):
                raise ValueError("does not match expected format: {}".format(value))
        elif self.format_type == "url":
            try:
                url = urllib.parse.urlparse(value)
                if url.scheme == "" or url.hostname == "":
                    raise ValueError("not a valid URL: {}".format(value))
            except ValueError:
                raise ValueError("not a valid URL: {}".format(value))
        elif self.format_type == "email":
            if "@" not in value:
                raise ValueError("not an email address: {}".format(value))

    def prompt(self):
        while True:
            value = click.prompt(
                self.label,
                default=self.default,
                type=str,
                hide_input=self.format_type == "password",
            )
            try:
                self.verify_value(value)
                return value
            except ValueError as e:
                click.echo(f"Error: {str(e)}", err=True)


class IntField(Field):
    """An integer field."""

    def __init__(self, spec):
        super().__init__(spec)

        self.minimum = spec.get("minimum", -math.inf)
        self.maximum = spec.get("maximum", math.inf)
        if not self.required:
            self.default = self.default or 0

    def verify_value(self, value):
        if not isinstance(value, int):
            raise ValueError("not an integer: {}".format(value))

        if value < self.minimum:
            raise ValueError(
                "value below minimum allowed value ({}): {}".format(self.minimum, value)
            )
        elif value > self.maximum:
            raise ValueError(
                "value above maximum allowed value ({}): {}".format(self.maximum, value)
            )

    def prompt(self):
        field_type = click.IntRange(
            max=self.maximum if self.maximum < math.inf else None,
            min=self.minimum if self.minimum > -math.inf else None,
        )
        return click.prompt(self.label, default=self.default, type=field_type)


class FloatField(Field):
    """A floating point field."""

    def __init__(self, spec):
        super().__init__(spec)

        self.minimum = spec.get("minimum", -math.inf)
        self.maximum = spec.get("maximum", math.inf)
        if not self.required:
            self.default = self.default or 0.0

    def verify_value(self, value):
        if not isinstance(value, float):
            raise ValueError("not a float: {}".format(value))

        if value < self.minimum:
            raise ValueError(
                "value below minimum allowed value ({}): {}".format(self.minimum, value)
            )
        elif value > self.maximum:
            raise ValueError(
                "value above maximum allowed value ({}): {}".format(self.maximum, value)
            )

    def prompt(self):
        field_type = click.FloatRange(
            max=self.maximum if self.maximum < math.inf else None,
            min=self.minimum if self.minimum > -math.inf else None,
        )
        return click.prompt(self.label, default=self.default, type=field_type)


class BoolField(Field):
    """A boolean field."""

    def __init__(self, spec):
        super().__init__(spec)
        # force boolean default
        self.default = self.default or False

    def verify_value(self, value):
        if not isinstance(value, bool):
            raise ValueError("not a boolean: {}".format(value))

    def prompt(self):
        return click.confirm(self.label, default=self.default)

    def format(self, value):
        return "Y" if value else "N"


class EnumField(Field):
    """An enum field, allowing you to pick a single option from a list."""

    def __init__(self, spec):
        super().__init__(spec)

        self.options = spec.get("options", [])

    def verify_value(self, value):
        if not any(value == choice["value"] for choice in self.options):
            raise ValueError("not a valid option: {}".format(value))

    def prompt(self):
        choices = [
            Choice(choice["value"], choice["display_value"]) for choice in self.options
        ]
        return prompt_enum(choices, label=self.label, default=self.default)

    def format(self, value):
        for choice in self.options:
            if choice["value"] == value:
                return choice["display_value"]
        return repr(value)


class MultichoiceField(Field):
    """A multi-choice field, allowing you to pick one or more options from a list."""

    def __init__(self, spec):
        super().__init__(spec)

        self.options = spec.get("options", [])

    def verify_value(self, value):
        if not isinstance(value, list):
            raise ValueError("must be a list: {}".format(value))

        for val in value:
            if not any(val == choice["value"] for choice in self.options):
                raise ValueError("not a valid option: {}".format(val))

    def prompt(self):
        while True:
            value = self._prompt_multichoice()
            try:
                self.verify_value(value)
                return value
            except ValueError as e:
                click.echo(f"Error: {str(e)}", err=True)

    def _prompt_multichoice(self):
        click.echo(f"{self.label}:")
        for i, choice in enumerate(self.options, 1):
            click.echo("  {}) {}".format(i, choice["display_value"]))

        default = (
            _set_to_range(
                {
                    i + 1
                    for i, choice in enumerate(self.options)
                    if choice["value"] == self.default
                }
            )
            if self.default is not None
            else None
        )

        while True:
            selection = click.prompt(
                "Specify one or more comma-separated options", default=default, type=str
            )
            try:
                choices = _range_to_set(selection)
            except ValueError:
                click.echo("Error: not a valid range set", err=True)
                continue

            try:
                return [self.options[i - 1]["value"] for i in choices]
            except IndexError:
                click.echo("Error: choices not in range", err=True)

    def format(self, value):
        return ", ".join(
            next(
                (
                    choice["display_value"]
                    for choice in self.options
                    if choice["value"] == val
                ),
                repr(val),
            )
            for val in value
        )


T = TypeVar("T")


@dataclasses.dataclass
class Choice(Generic[T]):
    value: T
    display_value: str


def prompt_enum(
    options: list[Choice[T]],
    label: str | None = None,
    default: T | None = None,
    prompt: str = "Specify an option",
    allow_empty: bool = False,
    **kwargs,
) -> T | None:
    """
    Prompt the user to select a single item from a list.

    :param options: The options the user should choose from
    :param label: A label to display at the top of the list
    :param default: The default value if no choice is given
    :param prompt: The text to show for the prompt line
    :param allow_empty: Allow no input, in which case None is returned
    :param kwargs: Additional options to pass to click.prompt
    :return: The value corresponding to the user's choice, or None if allow_empty is True and no input was given
    """
    if label is not None:
        click.echo(f"{label}:")
    for i, choice in enumerate(options, 1):
        click.echo("  {}) {}".format(i, choice.display_value))

    default_index = None
    if default is not None:
        default_index = next(
            (i + 1 for i, choice in enumerate(options) if choice.value == default),
            None,
        )
    elif allow_empty:
        default_index = 0
    selection = click.prompt(
        prompt,
        default=default_index,
        type=click.IntRange(1 if not allow_empty else 0, len(options)),
        **kwargs,
    )
    return options[selection - 1].value if selection > 0 else None


def _set_to_range(choices: set[int]) -> str | None:
    if len(choices) == 0:
        return None

    ranges = []
    start = -1
    prev = -1
    for choice in sorted(choices):
        if start > 0 and choice > prev + 1:
            ranges.append((start, prev))
            start = choice
        elif start <= 0:
            start = choice
        prev = choice
    ranges.append((start, prev))
    return ",".join(f"{a}-{b}" if b > a else str(a) for a, b in ranges)


def _range_to_set(rng: str) -> set[int]:
    choices: set[int] = set()
    for x in rng.split(","):
        if "-" in x:
            a, b = map(int, x.split("-", 2))
            choices.update(range(a, b + 1))
        else:
            choices.add(int(x))
    return choices
