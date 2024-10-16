# GitHub Stars Dashboard - Source Code Structure

This document provides an overview of the source code structure for the GitHub Stars Dashboard project. The project is built using React and organized into components, hooks, and utility functions for better maintainability and reusability.

## File Structure

```
src/
├── components/
│   ├── Dashboard.js
│   ├── SortDropdown.js
│   ├── AdvancedSearchCondition.js
│   ├── AdvancedSearch.js
│   ├── ArXivBadge.js
│   └── ExpandedRepoView.js
├── hooks/
│   └── useRepositories.js
├── utils/
│   ├── arxivUtils.js
│   └── sortUtils.js
├── App.js
├── index.js
└── index.css
```

## Main Application Files

### App.js
The root component of the application. It typically renders the main `Dashboard` component and may include any global providers or context.

### index.js
The entry point of the React application. It renders the `App` component and attaches it to the DOM.

### index.css
Contains global styles for the application. This may include reset styles, global typography rules, or other app-wide CSS.

## Components

### Dashboard.js
The main component that renders the entire dashboard. It orchestrates the other components and manages the overall state of the application.

### SortDropdown.js
A reusable dropdown component for sorting repositories. It allows users to select sorting criteria and direction.

### AdvancedSearchCondition.js
Renders a single condition in the advanced search feature. It includes fields for selecting the search attribute, operator, and value.

### AdvancedSearch.js
Manages the advanced search feature, allowing users to add, remove, and modify search conditions.

### ArXivBadge.js
A small component that displays an arXiv badge for repositories linked to arXiv papers.

### ExpandedRepoView.js
Renders detailed information about a repository when it's expanded in the list view.

## Hooks

### useRepositories.js
A custom hook that manages the fetching, filtering, and sorting of repository data. It encapsulates the complex logic for data manipulation, making it easier to test and maintain.

## Utilities

### arxivUtils.js
Contains utility functions for working with arXiv-related data, such as extracting arXiv IDs and retrieving specific fields from arXiv metadata.

### sortUtils.js
Provides utility functions and constants related to sorting and field operations, including field options, operator lists, and input type determination.

## Usage

To use these components and utilities in your React application:

1. The `index.js` file serves as the entry point and renders the `App` component.

2. The `App.js` file renders the main `Dashboard` component.

3. The `Dashboard` component will handle the rendering of all sub-components and manage the application state.

4. Global styles are defined in `index.css` and applied to the entire application.

## Development

When developing new features or modifying existing ones:

- Keep components focused on a single responsibility.
- Use the `useRepositories` hook for data fetching and manipulation logic.
- Place any new utility functions in the appropriate utility file or create a new one if necessary.
- Update this README when adding new components or significantly changing the project structure.
- Add any global styles to `index.css`, but prefer component-specific styles when possible.

## Testing

- Each component and utility function should have corresponding unit tests.
- Use React Testing Library for component tests.
- Place test files adjacent to the components or utilities they're testing, with a `.test.js` suffix.

## Styling

- The project uses Tailwind CSS for styling. Refer to the Tailwind documentation for available classes.
- Global styles are in `index.css`. Use this for app-wide styling needs.
- Component-specific styles should be added using Tailwind classes directly in the component files.
- If custom styles are needed beyond Tailwind, consider creating a separate CSS module for the component.

## Data Flow

1. The `useRepositories` hook fetches data from the JSON files.
2. The main `Dashboard` component receives the data and filtering/sorting functions from the hook.
3. User interactions (sorting, searching, expanding repos) trigger state updates in the `Dashboard` component.
4. These state changes cause the `useRepositories` hook to re-filter and re-sort the data.
5. The updated data flows down to the child components for rendering.

Remember to keep this README updated as the project evolves. Good documentation is key to maintaining a healthy, collaborative project!
