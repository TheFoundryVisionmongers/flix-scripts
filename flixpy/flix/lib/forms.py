import collections
import dataclasses
import math
import re
import urllib.parse
from typing import Any, Generic, TypeVar, TypedDict, Callable, Type, cast, Mapping

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


class FormOptionModel(TypedDict):
    display_value: str
    value: Any


RequirementModel = TypedDict(
    "RequirementModel",
    {
        "required_id": str,
        "required_value": Any,
        "or": list["RequirementModel"],  # type: ignore # recursive type not supported yet
        "and": list["RequirementModel"],  # type: ignore
    },
    total=False,
)


class FormSectionModel(TypedDict, total=False):
    type: str
    elements: list["FormSectionModel"]  # type: ignore # recursive types not supported yet
    heading: str
    label: str
    id: str
    default: Any
    required: bool
    minimum: int
    maximum: int
    format: str
    format_value: str
    options: list[FormOptionModel]
    multi_select_allowed: bool
    requirements: list[RequirementModel]


class Requirement:
    def __init__(self, spec: RequirementModel):
        self.required_id = spec.get("required_id")
        self.required_value = spec.get("required_value")
        self.and_requirements = [Requirement(req) for req in spec.get("and") or []]
        self.or_requirements = [Requirement(req) for req in spec.get("or") or []]

    def holds(self, parameters: Mapping[str, Any]) -> bool:
        if self.and_requirements:
            return all(req.holds(parameters) for req in self.and_requirements)
        elif self.or_requirements:
            return any(req.holds(parameters) for req in self.or_requirements)
        else:
            return parameters.get(str(self.required_id)) == self.required_value


class Field:
    """A generic form field."""

    def __init__(self, spec: FormSectionModel):
        self.label = spec["label"]
        self.id = spec["id"]
        self.type = spec["type"]
        self.required = spec.get("required", False)
        self.default = spec.get("default")
        self.requirements = [Requirement(req) for req in spec.get("requirements") or []]

    def verify(self, parameters: dict[str, Any], ignore_required: bool = False) -> None:
        if not self.requirements_hold(parameters):
            return

        if self.id not in parameters:
            if self.required and self.default is None and not ignore_required:
                raise ValueError("missing required field {}".format(self.id))
            return

        try:
            self.verify_value(parameters[self.id])
        except ValueError as e:
            raise ValueError("{}: {}".format(self.id, str(e))) from e

    def verify_value(self, value: Any) -> None:
        raise NotImplementedError

    def prompt(self) -> Any:
        raise NotImplementedError

    def format(self, value: Any) -> str:
        return str(value)

    def requirements_hold(self, parameters: Mapping[str, Any]) -> bool:
        return all(req.holds(parameters) for req in self.requirements)


class StringField(Field):
    """A string field."""

    def __init__(self, spec: FormSectionModel):
        super().__init__(spec)

        self.minimum = spec.get("minimum", -math.inf)
        self.maximum = spec.get("maximum", math.inf)
        self.format_type = spec.get("format")
        self.format_pattern = spec.get("format_value", ".*")
        if self.default is None and self.minimum == 0:
            self.default = ""

    def verify_value(self, value: Any) -> None:
        if not isinstance(value, str):
            raise ValueError("not a string: {}".format(value))

        if len(value) < self.minimum:
            raise ValueError("string must be at least {} characters: {}".format(self.minimum, value))
        elif len(value) > self.maximum:
            raise ValueError("string can be at most {} characters: {}".format(self.maximum, value))
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

    def prompt(self) -> str:
        while True:
            value = click.prompt(
                self.label,
                default=self.default,
                type=str,
                hide_input=self.format_type == "password",
                err=True,
            )
            try:
                self.verify_value(value)
                return cast(str, value)
            except ValueError as e:
                click.echo(f"Error: {str(e)}", err=True)


class IntField(Field):
    """An integer field."""

    def __init__(self, spec: FormSectionModel):
        super().__init__(spec)

        self.minimum = spec.get("minimum", -math.inf)
        self.maximum = spec.get("maximum", math.inf)
        if not self.required:
            self.default = self.default or 0

    def verify_value(self, value: Any) -> None:
        if not isinstance(value, int):
            raise ValueError("not an integer: {}".format(value))

        if value < self.minimum:
            raise ValueError("value below minimum allowed value ({}): {}".format(self.minimum, value))
        elif value > self.maximum:
            raise ValueError("value above maximum allowed value ({}): {}".format(self.maximum, value))

    def prompt(self) -> int:
        field_type = click.IntRange(
            max=self.maximum if self.maximum < math.inf else None,
            min=self.minimum if self.minimum > -math.inf else None,
        )
        return cast(int, click.prompt(self.label, default=self.default, type=field_type, err=True))


class FloatField(Field):
    """A floating point field."""

    def __init__(self, spec: FormSectionModel):
        super().__init__(spec)

        self.minimum = spec.get("minimum", -math.inf)
        self.maximum = spec.get("maximum", math.inf)
        if not self.required:
            self.default = self.default or 0.0

    def verify_value(self, value: Any) -> None:
        if not isinstance(value, float):
            raise ValueError("not a float: {}".format(value))

        if value < self.minimum:
            raise ValueError("value below minimum allowed value ({}): {}".format(self.minimum, value))
        elif value > self.maximum:
            raise ValueError("value above maximum allowed value ({}): {}".format(self.maximum, value))

    def prompt(self) -> float:
        field_type = click.FloatRange(
            max=self.maximum if self.maximum < math.inf else None,
            min=self.minimum if self.minimum > -math.inf else None,
        )
        return cast(float, click.prompt(self.label, default=self.default, type=field_type, err=True))


class BoolField(Field):
    """A boolean field."""

    def __init__(self, spec: FormSectionModel):
        super().__init__(spec)
        # force boolean default
        self.default = self.default or False

    def verify_value(self, value: Any) -> None:
        if not isinstance(value, bool):
            raise ValueError("not a boolean: {}".format(value))

    def prompt(self) -> bool:
        return click.confirm(self.label, default=self.default, err=True)

    def format(self, value: Any) -> str:
        return "Y" if value else "N"


class EnumField(Field):
    """An enum field, allowing you to pick a single option from a list."""

    def __init__(self, spec: FormSectionModel):
        super().__init__(spec)

        self.options: list[FormOptionModel] = spec.get("options", [])

    def verify_value(self, value: Any) -> None:
        if not any(value == choice["value"] for choice in self.options):
            raise ValueError("not a valid option: {}".format(value))

    def prompt(self) -> Any:
        choices = [Choice(choice["value"], choice["display_value"]) for choice in self.options]
        return prompt_enum(choices, label=self.label, default=self.default)

    def format(self, value: Any) -> str:
        for choice in self.options:
            if choice["value"] == value:
                return choice["display_value"]
        return repr(value)


class MultichoiceField(Field):
    """A multi-choice field, allowing you to pick one or more options from a list."""

    def __init__(self, spec: FormSectionModel):
        super().__init__(spec)

        self.options: list[FormOptionModel] = spec.get("options", [])

    def verify_value(self, value: Any) -> None:
        if not isinstance(value, list):
            raise ValueError("must be a list: {}".format(value))

        for val in value:
            if not any(val == choice["value"] for choice in self.options):
                raise ValueError("not a valid option: {}".format(val))

    def prompt(self) -> list[Any]:
        choices = [Choice(choice["value"], choice["display_value"]) for choice in self.options]
        return prompt_multichoice(choices, label=self.label, default=self.default)

    def format(self, value: Any) -> str:
        return ", ".join(
            next(
                (choice["display_value"] for choice in self.options if choice["value"] == val),
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
    **kwargs: Any,
) -> T:
    """
    Prompt the user to select a single item from a list.

    :param options: The options the user should choose from
    :param label: A label to display at the top of the list
    :param default: The default value if no choice is given
    :param prompt: The text to show for the prompt line
    :param kwargs: Additional options to pass to click.prompt
    :return: The value corresponding to the user's choice, or default if not None and no input was given
    """
    if label is not None:
        click.echo(f"{label}:", err=True)
    for i, choice in enumerate(options, 1):
        click.echo("  {}) {}".format(i, choice.display_value), err=True)

    default_index = None
    if default is not None:
        default_index = next((i for i, choice in enumerate(options, 1) if choice.value == default), 0)

    selection: int = click.prompt(
        prompt,
        default=default_index,
        type=click.IntRange(0 if default_index == 0 else 1, len(options)),
        show_default=default_index != 0,
        err=True,
        **kwargs,
    )
    if default is None:
        return options[selection - 1].value
    else:
        return options[selection - 1].value if selection > 0 else default


def prompt_multichoice(
    options: list[Choice[T]],
    label: str | None = None,
    default: T | None = None,
    prompt: str = "Specify one or more comma-separated options",
) -> list[T]:
    if label is not None:
        click.echo(f"{label}:", err=True)
    for i, choice in enumerate(options, 1):
        click.echo("  {}) {}".format(i, choice.display_value), err=True)

    default_range = (
        _set_to_range({i + 1 for i, choice in enumerate(options) if choice.value == default})
        if default is not None
        else None
    )

    while True:
        selection = click.prompt(prompt, default=default_range, type=str, err=True)
        try:
            choices = _range_to_set(selection)
        except ValueError:
            click.echo("Error: not a valid range set", err=True)
            continue

        try:
            return [options[i - 1].value for i in choices]
        except IndexError:
            click.echo("Error: choices not in range", err=True)


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


TDict = TypeVar("TDict", bound=Mapping[str, Any])


class Form:
    """This class can be used to validate data against a Flix creation form,
    or to prompt a user for input to construct or modify an object adhering to a creation form."""

    _TYPES: dict[str, Callable[[FormSectionModel], Type[Field]]] = {
        "string": lambda _: StringField,
        "int": lambda _: IntField,
        "float": lambda _: FloatField,
        "bool": lambda _: BoolField,
        "multichoice": lambda field: (MultichoiceField if field.get("multi_select_allowed") else EnumField),
    }

    def __init__(self, spec: FormSectionModel):
        """
        Constructs a new Form.

        :param spec: A creation form as returned by a /form Flix endpoint
        """
        self.fields: collections.OrderedDict[str, Field] = collections.OrderedDict()
        self._read_fields(spec["elements"])

    def _read_fields(self, section: list[FormSectionModel]) -> None:
        for field in section:
            if "elements" in field:
                self._read_fields(field["elements"])
            else:
                field_type = Form._TYPES[field["type"]](field)
                self.fields[field["id"]] = field_type(field)

    def verify(self, parameters: dict[str, Any], ignore_required: bool = False) -> None:
        """
        Validates the given object against the creation form.

        :param parameters: The object to validate
        :param ignore_required: If true, no error will be raised for missing required parameters
        :raises ValueError: If the object does not adhere to the creation form
        """
        for field in self.fields.values():
            field.verify(parameters, ignore_required=ignore_required)

    def prompt(self, parameters: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Prompt the user for input required to construct an object adhering to this creation form.

        :param parameters: An optional partial object; only parameters not already set will be queried
        :raises ValueError: If a partial object was passed, and the set fields are not valid
        :return: A new instance of the object type described by this creation form
        """
        parameters = parameters or {}
        self.verify(parameters, ignore_required=True)

        for field in self.fields.values():
            if field.id not in parameters and field.requirements_hold(parameters):
                parameters[field.id] = field.prompt()
        return parameters

    def prompt_edit(self, parameters: TDict) -> TDict:
        """
        Prompt the user for input to modify an existing object adhering to this creation form.

        :param parameters: A fully-constructed instance of the object type described by this creation form
        :return: The given object, modified according to user input
        """
        # a bit ugly, but needed to work around typing limitations
        # the creation form specification guarantees type correctness
        params = cast(dict[str, Any], parameters)
        while True:
            # query for any unset fields, or fields that became enabled after a change to another field
            params = self.prompt(params)

            option: str = prompt_enum(
                [
                    Choice(
                        field_id,
                        f"{field.label}: {field.format(params.get(field_id))}",
                    )
                    for field_id, field in self.fields.items()
                    if field.requirements_hold(params)
                ],
                default="",
                prompt="Select field to edit, or press ENTER to save",
            )
            if option == "":
                break
            else:
                params[option] = self.fields[option].prompt()
        return cast(TDict, params)

    def print(self, parameters: TDict, *, err: bool = False) -> None:
        """
        Pretty-print an instance of the object type defined by this form.

        :param parameters: The object to print
        :param err: Whether to print to standard error
        """
        for name, field in self.fields.items():
            if name in parameters and field.requirements_hold(parameters):
                click.echo("{}: {}".format(field.label, field.format(parameters[name])), err=err)
