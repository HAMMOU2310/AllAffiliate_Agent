from __future__ import annotations

import traceback

from core.result import Result
from services.base_service import BaseService


class ErrorAnalyzer(BaseService):
    """
    Analyze exceptions and Result objects.

    This service provides a centralized way
    to inspect failures across the project.
    """

    def analyze_exception(
        self,
        exception: Exception,
    ) -> Result:

        return Result.fail(
            message=str(exception),
            errors=[traceback.format_exc()],
            metadata={
                "type": type(exception).__name__,
            },
        )

    def analyze_result(
        self,
        result: Result,
    ) -> Result:

        if result.success:
            return Result.ok(
                data=result,
                message="Result contains no errors.",
            )

        return Result.ok(
            data={
                "message": result.message,
                "errors": result.errors,
                "metadata": result.metadata,
            },
            message="Result analyzed successfully.",
        )

    def summarize(
        self,
        result: Result,
    ) -> Result:

        summary = {
            "success": result.success,
            "message": result.message,
            "error_count": len(result.errors),
        }

        return Result.ok(
            data=summary,
            message="Summary created successfully.",
        )