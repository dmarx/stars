import React from 'react';
import { Plus, Trash2 } from 'lucide-react';
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
    <div className="bg-white p-6 rounded-lg shadow-md mb-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">Advanced Search</h3>
      <div className="space-y-4">
        {conditions.map((condition, index) => (
          <div key={index} className="flex items-start">
            <div className="w-20 pt-2">
              {index > 0 && (
                <select
                  value={condition.conjunction}
                  onChange={(e) => updateCondition(index, { ...condition, conjunction: e.target.value })}
                  className="w-full px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="AND">AND</option>
                  <option value="OR">OR</option>
                </select>
              )}
            </div>
            <div className="flex-grow">
              <AdvancedSearchCondition
                condition={condition}
                updateCondition={(newCondition) => updateCondition(index, newCondition)}
                fieldOptions={fieldOptions}
                allLists={allLists}
                allCategories={allCategories}
              />
            </div>
            <button
              onClick={() => removeCondition(index)}
              className="ml-2 p-2 text-red-600 hover:text-red-800 focus:outline-none"
              aria-label="Remove condition"
            >
              <Trash2 size={20} />
            </button>
          </div>
        ))}
      </div>
      <div className="flex justify-center mt-4">
        <button
          onClick={addCondition}
          className="flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus size={20} className="mr-2" />
          Add condition
        </button>
      </div>
    </div>
  );
};

export default AdvancedSearch;
