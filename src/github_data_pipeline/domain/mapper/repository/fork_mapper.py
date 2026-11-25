# src/github_data_pipeline/domain/mapper/repository/fork_mapper.py

from __future__ import annotations

from typing import Any

from src.github_data_pipeline.domain.entity.repository.fork_item import ForkItem


class ForkMapper:
    """
    Maps GitHub fork responses into domain fork entities.
    """

    @staticmethod
    def to_fork_item(
        data: dict[str, Any],
        repo_id: int,
    ) -> ForkItem:
        """
        Convert a GitHub fork response into a ForkItem.

        Args:
            data: Raw fork data returned by the GitHub API.
            repo_id: Unique identifier of the original repository.

        Returns:
            A ForkItem representing the repository fork.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Expected fork data to be a dictionary, "
                f"got {type(data).__name__}: {data!r}"
            )

        owner = data.get("owner")

        if not isinstance(owner, dict):
            raise ValueError(
                f"Invalid or missing owner in fork response: {data!r}"
            )

        required_fields = ("id", "created_at")

        missing_fields = [
            field for field in required_fields
            if data.get(field) is None
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required fork fields: {missing_fields}"
            )

        if owner.get("id") is None or owner.get("login") is None:
            raise ValueError(
                f"Missing required owner fields in fork response: {owner!r}"
            )

        return ForkItem(
            repo_id=repo_id,
            fork_id=data["id"],
            owner_id=owner["id"],
            owner_login=owner["login"],
            created_at=data["created_at"],
        )
