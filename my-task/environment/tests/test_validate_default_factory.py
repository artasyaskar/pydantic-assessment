"""Tests for validate_default with default_factory taking validated data."""

from typing import Annotated, Any, List

import pytest
from annotated_types import Gt
from pydantic import BaseModel, Field, ValidationError

PositiveInt = Annotated[int, Gt(0)]


def test_validate_default_with_factory_taking_data():
    """Test that validate_default works correctly with default_factory taking validated data."""
    
    def count_items(data: dict[str, Any]) -> int:
        """Factory that transforms validated data into a count."""
        return len(data.get('items', []))
    
    class Container(BaseModel):
        items: List[str] = []
        count: PositiveInt = Field(
            default_factory=count_items, 
            validate_default=True
        )
    
    # Should work: factory produces 3, which is > 0
    container = Container(items=['a', 'b', 'c'])
    assert container.count == 3
    
    # Should fail validation: factory produces 0, which is not > 0
    with pytest.raises(ValidationError) as exc_info:
        Container(items=[])
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('count',)
    assert errors[0]['type'] == 'greater_than'
    assert errors[0]['ctx']['gt'] == 0


def test_validate_default_with_factory_producing_invalid_value():
    """Test that validation catches invalid factory output."""
    
    def always_zero(data: dict[str, Any]) -> int:
        """Factory that always returns 0 (invalid for PositiveInt)."""
        return 0
    
    class Model(BaseModel):
        value: PositiveInt = Field(
            default_factory=always_zero,
            validate_default=True
        )
    
    # Should fail: factory produces 0, not > 0
    with pytest.raises(ValidationError) as exc_info:
        Model()
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('value',)
    assert errors[0]['type'] == 'greater_than'


def test_validate_default_with_factory_taking_data_nested():
    """Test nested models with validate_default and data-taking factory."""
    
    def sum_values(data: dict[str, Any]) -> int:
        """Factory that sums nested values."""
        nested = data.get('nested', {})
        return nested.get('x', 0) + nested.get('y', 0)
    
    class Nested(BaseModel):
        x: int = 0
        y: int = 0
    
    class Parent(BaseModel):
        nested: Nested = Nested()
        total: PositiveInt = Field(
            default_factory=sum_values,
            validate_default=True
        )
    
    # Should work: 5 + 3 = 8 > 0
    parent = Parent(nested={'x': 5, 'y': 3})
    assert parent.total == 8
    
    # Should fail: 0 + 0 = 0, not > 0
    with pytest.raises(ValidationError):
        Parent(nested={'x': 0, 'y': 0})


def test_validate_default_without_factory():
    """Test validate_default works normally without factory."""
    
    class Model(BaseModel):
        value: PositiveInt = Field(default=5, validate_default=True)
    
    model = Model()
    assert model.value == 5
    
    # Should fail with invalid default
    class BadModel(BaseModel):
        value: PositiveInt = Field(default=0, validate_default=True)
    
    with pytest.raises(ValidationError):
        BadModel()


def test_factory_without_validate_default():
    """Test factory without validate_default doesn't validate output."""
    
    def always_zero(data: dict[str, Any]) -> int:
        return 0
    
    class Model(BaseModel):
        value: PositiveInt = Field(default_factory=always_zero)
        # No validate_default - should not validate the factory output
    
    # Without validate_default, factory output is not re-validated
    # This is the expected behavior
    model = Model()
    assert model.value == 0  # No validation error


def test_factory_not_taking_data_with_validate_default():
    """Test validate_default with factory that doesn't take data."""
    
    call_count = 0
    
    def get_value() -> int:
        nonlocal call_count
        call_count += 1
        return 5
    
    class Model(BaseModel):
        value: PositiveInt = Field(default_factory=get_value, validate_default=True)
    
    model = Model()
    assert model.value == 5
    assert call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
