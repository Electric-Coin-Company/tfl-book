name: Question
description: Ask a question
labels: ["question"]
assignees:
  - nathan-at-least
body:
  - type: markdown
    attributes:
      value: Thanks for providing feedback and improving clarity!
  - type: textarea
    id: question
    attributes:
      label: Question
      description: What would you like to know?
    validations:
      required: true

