import React from 'react';
import { getOperators, getInputType } from '../utils/sortUtils';

const AdvancedSearchCondition = ({ condition, updateCondition, fieldOptions, allLists, allCategories }) => {
  const renderInput = () => {
    const inputType = getInputType(condition.field);
    const inputClass = "w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";
    
    switch (inputType) {
      case 'number':
        return (
          <input
            type="number"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className={inputClass}
          />
        );
      case 'date':
        return (
          <input
            type="date"
            value={condition.value}
            onChange={(e) => updateCondition({ ...condition, value: e.target.value })}
            className={inputClass}
          />
        );
      case 'list':
        const options = condition.field === 'lists' ? allLists : allCategories;
        return (
          <select
            multiple
            value={condition.value.split(',')}
            onChange={(e) => updateCondition({ ...condition, value: Array.from(e.target.selectedOptions, option => option.value).join(',') })}
            className={inputClass}
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
            className={inputClass}
          />
        );
    }
  };

  const fieldType = getInputType(condition.field);
  const operators = getOperators(fieldType);

  return (
    <div className="flex items-center space-x-2">
      <select
        value={condition.field}
        onChange={(e) => updateCondition({ ...condition, field: e.target.value, operator: getOperators(getInputType(e.target.value))[0].value })}
        className="w-1/3 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {fieldOptions.map(option => (
          <option key={option.value} value={option.value}>{option.label}</option>
        ))}
      </select>
      <select
        value={condition.operator}
        onChange={(e) => updateCondition({ ...condition, operator: e.target.value })}
        className="w-1/3 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {operators.map(op => (
          <option key={op.value} value={op.value}>{op.label}</option>
        ))}
      </select>
      <div className="w-1/3">
        {renderInput()}
      </div>
    </div>
  );
};

export default AdvancedSearchCondition;
