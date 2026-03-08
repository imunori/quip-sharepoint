import { useState, useEffect } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './components/auth/LoginPage';
import { useDocumentStore } from './store/documentStore';
import { authApi } from './api/quipClient';

function App() {
  const [authenticated, setAuthenticated] = useState(authApi.isLoggedIn());
  const { loadCurrentUser } = useDocumentStore();

  useEffect(() => {
    if (authenticated) {
      loadCurrentUser();
    }
  }, [authenticated]);

  if (!authenticated) {
    return <LoginPage onLogin={() => setAuthenticated(true)} />;
  }

  return <AppLayout />;
}

export default App;
