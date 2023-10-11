import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect, Link } from 'react-router-dom';
import './App.css';

const App = () => {
  const [token, setToken] = useState(sessionStorage.getItem('token'));

  const handleLogout = () => {
    sessionStorage.removeItem('token');
    setToken(null);
  };

  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            {token ? (
              <>
                <li><Link to="/private">Private</Link></li>
                <li><button onClick={handleLogout}>Logout</button></li>
              </>
            ) : (
              <>
                <li><Link to="/signup">Signup</Link></li>
                <li><Link to="/login">Login</Link></li>
              </>
            )}
          </ul>
        </nav>

        <Switch>
          <Route exact path="/">
            <Home />
          </Route>
          <Route path="/signup">
            {token ? <Redirect to="/private" /> : <Signup setToken={setToken} />}
          </Route>
          <Route path="/login">
            {token ? <Redirect to="/private" /> : <Login setToken={setToken} />}
          </Route>
          <PrivateRoute path="/private" token={token}>
            <Private />
          </PrivateRoute>
        </Switch>
      </div>
    </Router>
  );
};

const Home = () => <div>Home Page</div>;

const Signup = ({ setToken }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('/api/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (response.status === 201) {
      const data = await response.json();
      alert(data.message);
      setToken('');
    } else {
      alert('Signup failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Signup</h2>
      <label>Email: <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} /></label><br />
      <label>Password: <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label><br />
      <button type="submit">Submit</button>
    </form>
  );
};

const Login = ({ setToken }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (response.status === 200) {
      const data = await response.json();
      sessionStorage.setItem('token', data.token);
      setToken(data.token);
    } else {
      alert('Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <label>Email: <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} /></label><br />
      <label>Password: <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label><br />
      <button type="submit">Submit</button>
    </form>
  );
};

const PrivateRoute = ({ children, token }) => {
  return (
    <Route
      render={({ location }) =>
        token ? (
          children
        ) : (
          <Redirect
            to={{
              pathname: "/login",
              state: { from: location }
            }}
          />
        )
      }
    />
  );
};

const Private = () => <div>This is a private route</div>;

export default App;
