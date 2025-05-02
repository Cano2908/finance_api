from typing import Any, Generic, Type, TypeVar, get_args

from apps.api.config.problems.base_problem import BaseProblem

P = TypeVar("P", bound=BaseProblem)


class Problem(Exception, Generic[P]):
    detail: str | None
    extensions: dict[str, Any]

    def __init__(
        self,
        detail: str | None = None,
        **extensions,
    ):
        self.detail = detail
        self.extensions = extensions

    def get_problem_details(
        self, instance: Any
    ) -> (
        P
    ):  # pylint: disable=undefined-variable # reason: `T` is defined in the class signature. False positive.
        problem_class = self._get_problem_class()

        reserved_keys = ["detail", "instance", "title"]

        if problem_class == BaseProblem:
            reserved_keys.remove("title")
            instance = None

        for key in reserved_keys:
            if key in self.extensions:
                raise ValueError(f"Key '{key}' is reserved and cannot be used.")

        model_dict = {
            "detail": self.detail,
            "instance": instance,
            **self.extensions,
        }

        problem_details = problem_class.model_validate(
            obj=model_dict,
        )
        return problem_details

    def _get_problem_class(
        self,
    ) -> Type[
        P
    ]:  # pylint: disable=undefined-variable # reason: `T` is defined in the class signature. False positive.
        orig_class = getattr(self, "__orig_class__", None)
        if orig_class is None:
            raise ValueError(
                "Cannot determine the class of the problem, pleas provide the class as a type hint."
            )

        args = get_args(orig_class)
        return args[0]
