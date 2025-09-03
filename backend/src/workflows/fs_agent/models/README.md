# fs_agent workflow models

This directory contains Pydantic models that define structured outputs for the File System Agent workflow nodes. These models ensure type safety and consistent data structures throughout the workflow.

## Model overview

All models are Pydantic BaseModel classes that define the structure of outputs from LLM-powered nodes:

```python
from pydantic import BaseModel, Field

class ExampleOutput(BaseModel):
    field_name: str = Field(description="Field description")
    optional_field: Optional[str] = None
```

## Model files

### [observe_output.py](observe_output.py)

Defines the structured output from the observe node's analysis.

```python
class ObserveOutput(BaseModel):
    observation: str = Field(
        description="Summary of current context and user intent"
    )
    relevant_files: List[str] = Field(
        default_factory=list,
        description="Files mentioned or relevant to the request"
    )
    previous_action_summary: Optional[str] = Field(
        default=None,
        description="Summary of previous actions taken"
    )
    workspace_state: str = Field(
        description="Current state of the workspace"
    )
```

**Key fields:**
- `observation`: Contextual understanding of the situation
- `relevant_files`: Files that may be involved in the operation
- `previous_action_summary`: What has been done so far
- `workspace_state`: Current workspace status

### [plan_output.py](plan_output.py)

Defines the structured output from the plan node's decision-making.

```python
class PlanOutput(BaseModel):
    action_type: Literal["list", "read", "write", "edit", "delete", "none"] = Field(
        description="Type of action to perform"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Target file path for the action"
    )
    content: Optional[str] = Field(
        default=None,
        description="Content for write/edit operations"
    )
    reasoning: str = Field(
        description="Explanation of the planned action"
    )
    needs_thinking: bool = Field(
        default=False,
        description="Whether deeper reasoning is required"
    )
    safety_classification: Literal["safe", "risky"] = Field(
        description="Whether the action requires user approval"
    )
    thought_process: Optional[str] = Field(
        default=None,
        description="Detailed thinking for complex decisions"
    )
```

**Key fields:**
- `action_type`: The specific operation to perform
- `file_path`: Target file for the operation
- `content`: Data for write operations
- `reasoning`: Explanation for the user
- `needs_thinking`: Triggers thinking loop
- `safety_classification`: Determines approval flow
- `thought_process`: Records thinking iterations

## Model validation

Pydantic provides automatic validation:

```python
# Valid usage
output = PlanOutput(
    action_type="write",
    file_path="/workspace/test.txt",
    content="Hello World",
    reasoning="Creating a test file as requested",
    safety_classification="risky"
)

# Invalid - will raise ValidationError
output = PlanOutput(
    action_type="invalid_action",  # Not in allowed literals
    safety_classification="unknown"  # Not safe or risky
)
```

## Type safety benefits

1. **Compile-time checking**: IDEs can validate field access
2. **Runtime validation**: Invalid data raises clear errors
3. **Documentation**: Field descriptions serve as inline docs
4. **Serialization**: Easy JSON conversion for logging
5. **Schema generation**: Automatic OpenAPI schemas

## Integration with LLM

Models are used with structured output generation:

```python
from langchain_core.pydantic_v1 import BaseModel
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
structured_llm = llm.with_structured_output(PlanOutput)

response = await structured_llm.ainvoke(prompt)
# response is guaranteed to be a PlanOutput instance
```

## Field conventions

### Required vs optional
- Required fields: Core data needed for operation
- Optional fields: Additional context or conditional data

### Default values
```python
# List fields default to empty list
files: List[str] = Field(default_factory=list)

# Optional fields default to None
description: Optional[str] = None

# Boolean fields have explicit defaults
is_safe: bool = Field(default=True)
```

### Descriptions
All fields include descriptions for:
- LLM guidance during generation
- Developer documentation
- API schema generation

## Validation patterns

### Path validation
```python
@validator('file_path')
def validate_path(cls, v):
    if v and '..' in v:
        raise ValueError("Path traversal not allowed")
    return v
```

### Content limits
```python
@validator('content')
def validate_content_size(cls, v):
    if v and len(v) > 1_000_000:  # 1MB limit
        raise ValueError("Content too large")
    return v
```

## Evolution guidelines

When adding new models:

1. **Start minimal**: Include only essential fields
2. **Add validation**: Include validators for security
3. **Document clearly**: Field descriptions are crucial
4. **Version carefully**: Changes may break existing flows
5. **Test thoroughly**: Validate with real LLM outputs

## Common patterns

### Union types for flexibility
```python
class ActionOutput(BaseModel):
    result: Union[FileContent, FileList, OperationStatus]
```

### Nested models for complex data
```python
class FileInfo(BaseModel):
    path: str
    size: int
    modified: datetime

class DirectoryListing(BaseModel):
    files: List[FileInfo]
    total_size: int
```

### Enums for constrained choices
```python
from enum import Enum

class ActionType(str, Enum):
    LIST = "list"
    READ = "read"
    WRITE = "write"
    EDIT = "edit"
    DELETE = "delete"
```