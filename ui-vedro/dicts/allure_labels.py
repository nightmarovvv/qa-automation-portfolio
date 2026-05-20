# Typed allure label catalog. Free strings split the report on typos
# ("Bord" vs "Board"); the enum-like classes catch this at import.
# The decorator also enforces the team's reading order:
# Feature -> Story -> Priority -> AllureID.

from __future__ import annotations

import allure


class Feature:
    Board = "Board"
    TaskEditor = "Task editor"
    Search = "Search"


class Story:
    CreateTask = "Create task"
    EditTask = "Edit task"
    Search = "Debounced search"
    Validation = "Form validation"
    SaveErrors = "Save errors"


class Priority:
    Blocker = allure.severity_level.BLOCKER
    Critical = allure.severity_level.CRITICAL
    Normal = allure.severity_level.NORMAL
    Minor = allure.severity_level.MINOR


class AllureID:
    # Typed marker for the TMS id so allure_labels() can route it to
    # allure.id() instead of allure.label("custom", ...).

    def __init__(self, tms_id: str):
        self.tms_id = tms_id


def allure_labels(*labels):
    # Usage:
    # @allure_labels(Feature.Board, Story.CreateTask, Priority.Critical, AllureID("B-101"))
    def decorator(cls):
        for label in labels:
            if isinstance(label, AllureID):
                cls = allure.id(label.tms_id)(cls)
            elif isinstance(label, allure.severity_level):
                cls = allure.severity(label)(cls)
            elif label in vars(Feature).values():
                cls = allure.feature(label)(cls)
            elif label in vars(Story).values():
                cls = allure.story(label)(cls)
            else:
                cls = allure.label("custom", str(label))(cls)
        return cls

    return decorator
