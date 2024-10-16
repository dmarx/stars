import React from 'react';
import { Plus } from 'lucide-react';
import AdvancedSearchCondition from './AdvancedSearchCondition';

const AdvancedSearch = ({ conditions, setConditions, fieldOptions, allLists, allCategories }) => {
  const addCondition = () => {
    setConditions([...conditions, { field: 'name', operator: 'contains', value: '', conjunction: 'AND' }]);
  };

  const updateCondition = (index, newCondition) => {
    const newConditions = [...conditions];
    newConditions[index] = newCondition;
    setConditions(newConditions);
  };

  const removeCondition = (index) => {
    setConditions(conditions.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-gray-100 p-4 rounded-lg mb-4">
      <h3 className="text-lg font-semibold mb-2">Advanced Search</h3>
      {conditions.map((condition, index) => (
        <div key={index}>
          <AdvancedSearchCondition
            condition={condition}
            updateCondition={(newCondition) => updateCondition(index, newCondition)}
            removeCondition={() => removeCondition(index)}
            fieldOptions={fieldOptions}
            allLists={allLists}
            allCategories={allCategories}
          />
          {index < conditions.length - 1 && (
            <select
              value={condition.conjunction}
              onChange={(e) => updateCondition(index, { ...condition, conjunction: e.target.value })}
              className="mb-2 px-2 py-1 border rounded"
            >
              <option value="AND">AND</option>
              <option value="OR">OR</option>
            </select>
          )}
        </div>
      ))}
      <button onClick={addCondition} className="flex items-center text-blue-500"><Plus size={20} /> Add condition</button>
    </div>
  );
};

export default AdvancedSearch;
