"""
Create forms to answer questions using govuk-frontend macros.

The main function in this module is `from_question`. It should be possible to
do everything you might want to do just by calling `from_question` with a
content loader Question.

Read the docstring for `from_question` for more detail on how this works.
"""

from typing import Optional, Tuple

from jinja2 import Markup, escape

from dmutils.forms.errors import govuk_error

from dmcontent.questions import Question


__all__ = ["from_question", "govuk_input"]


def from_question(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None
) -> Optional[Tuple[str, dict]]:
    """Create parameters object for govuk-frontend macros from a question

    `from_question` aims to solve the developer need of

        Given a content loader Question
        I want to create a form element using the GOV.UK Design System
        So that the user gets a good experience

    in a way that requires the developer to know as little as possible about
    the Question object in question.

    `from_question` takes a Question and returns the name of the govuk-frontend
    macro to call and the parameters to call it with. Calling the macro with
    the parameters is left to the app developer.

    A little bit of Jinja magic is required for this; assuming you have called
    `from_question` already and have the macro name and parameters, you need a
    table of macro names to macros in a Jinja template:

        {% set govuk_forms = {
            "govukInput": govukInput,
            "govukRadios": govukRadios,
            ...
        } %}

        {{ govuk_frontend[macro_name](parameters) }}

    :param question: A Question or QuestionSummary
    :param data: A dict that may contain the answer for question
    :param errors: A dict which may contain an error message for the question

    :returns: The name of the macro and the parameters in a tuple, or None
              if we don't know how to handle this type of question
    """
    if question.type == "text":
        return "govukInput", govuk_input(question, data, errors)
    else:
        return None


def govuk_input(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None
) -> dict:
    """Create govukInput macro parameters from a text question"""

    params = _params(question, data, errors)
    params["classes"] = "app-text-input--height-compatible"

    return params


def _params(
    question: Question, data: Optional[dict] = None, errors: Optional[dict] = None
) -> dict:
    """Common parameters for govuk-frontent components

    The GOV.UK Design System macro library govuk-frontend has a consistent set
    of parameters that are used across almost all of its component macros.

    This function abstracts out those common parameters to hopefully simplify
    creating parameter sets for specific macros.

    *This function should however be considered an implementation detail of
    this module, and you should avoid using it outside of this file (hence the
    underscore).*

    The parameters handled by this function include:

        - errorMessage (optional)
        - hint (optional)
        - id
        - label
        - name
        - value (optional)

    :returns: A dictionary with parameters that are generally useful for
              govuk-frontend component macros
    """
    params = {
        "id": f"input-{question.id}",
        "name": question.id,
    }

    label_text = question.question
    if question.is_optional:
        # GOV.UK Design System says
        # > mark the labels of optional fields with '(optional)'
        label_text += " (optional)"

    params["label"] = {
        # Style the label as a page heading, following the
        # GOV.UK Design System question pages pattern at
        # https://design-system.service.gov.uk/patterns/question-pages/
        "classes": "govuk-label--l",
        "isPageHeading": True,

        "text": label_text,
    }

    hint_html = Markup()
    if question.get("question_advice"):
        # Put the question advice inside the hint, wrapped in a div
        # We add the class .app-hint--text so the question advice
        # can be styled like a normal paragraph with the following Sass
        #
        #     .app-hint--text {
        #       @extend %govuk-body--m
        #     }
        hint_html += Markup('<div class="app-hint--text">\n')
        hint_html += escape(question.question_advice)
        hint_html += Markup("\n</div>")
        if question.get("hint"):
            hint_html += "\n"

    if question.get("hint"):
        hint_html += escape(question.hint)

    if hint_html:
        params["hint"] = {"html": hint_html}

    if data and question.id in data:
        params["value"] = data[question.id]

    if errors and question.id in errors:
        params["errorMessage"] = govuk_error(errors[question.id])["errorMessage"]

    return params
