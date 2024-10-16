import React from 'react';
import { X } from 'lucide-react';
import { getOperators, getInputType } from '../utils/sortUtils';

const AdvancedSearchCondition = ({ condition, updateCondition, removeCondition, fieldOptions, allLists, allCategories }) => {
  const renderInput = () => {
    const inputType = getInputType(condition.field);
    switch (inputType) {
      case 'number':
        return (
          <input
            type="number"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className="px-2 py-1 border rounded"
          />
        );
      case 'date':
        return (
          <input
            type="date"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className="px-2 py-1 border rounded"
          />
        );
      case 'list':
        const options = condition.field === 'lists' ? allLists : allCategories;
        return (
          <select
            multiple
            value={condition.value.split(',')}
            onChange={(e) => updateCondition({ ...condition, value: Array.from(e.target.selectedOptions, option => option.value).join(',') })}
            className="px-2 py-1 border rounded"
          >
            {options.map(option => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
        );
      default:
        return (
          <input
            type="text"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className="px-2 py-1 border rounded"
          />
        );
    }
  };

  const fieldType = getInputType(condition.field);
  const operators = getOperators(fieldType);

  return (
    <div className="flex items-center space-x-2 mb-2">
      <select
        value={condition.field}
        onChange={(e) => updateCondition({ ...condition, field: e.target.value, operator: getOperators(getInputType(e.target.value))[0].value })}
        className="px-2 py-1 border rounded"
      >
        {fieldOptions.map(option => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
      <select
        value={condition.operator}
        onChange={(e) => updateCondition({ ...condition, operator: e.target.value })}
        className="px-2 py-1 border rounded"
      >
        {operators.map(op => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>
      {renderInput()}
      <button onClick={removeCondition} className="text-red-500"><X size={20} /></button>
    </div>
  );
};

export default AdvancedSearchCondition;
