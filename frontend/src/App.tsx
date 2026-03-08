import { useEffect } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { useDocumentStore } from './store/documentStore';

function App() {
  const { loadCurrentUser } = useDocumentStore();

  useEffect(() => {
    loadCurrentUser();
  }, []);

  return <AppLayout />;
}

export default App;
