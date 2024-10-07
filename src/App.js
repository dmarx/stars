import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Dashboard from './Dashboard';

function App() {
  return (
    <Router basename={process.env.PUBLIC_URL}>
      <Switch>
        <Route exact path="/" component={Dashboard} />
        {/* Add other routes as needed */}
      </Switch>
    </Router>
  );
}

export default App;
