from typing import Type, Union, get_args, get_origin


def is_list_type(annotation: Type) -> bool:
    """Check if the annotation is a list type."""
    return get_origin(annotation) is list


def is_optional_type(annotation: Type) -> bool:
    """Check if the annotation is an optional type."""
    return get_origin(annotation) is Union and type(None) in get_args(
        annotation
    )


def unwrap_list(annotation: Type) -> Type:
    """Unwraps the List type to get the actual type."""
    if is_list_type(annotation):
        return get_args(annotation)[0]
    return annotation


def unwrap_optional(annotation: Type) -> Type:
    """Unwraps the Optional type to get the actual type."""
    if is_optional_type(annotation):
        return next(
            arg for arg in get_args(annotation) if arg is not type(None)
        )
    return annotation
